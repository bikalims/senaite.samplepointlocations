# -*- coding: utf-8 -*-

from datetime import timedelta

from plone.dexterity.utils import createContent
from plone.namedfile import NamedBlobFile
from zope.component import getMultiAdapter

from bika.lims import api
from bika.lims.utils import tmpID
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.interfaces import IContentMigrator
from senaite.core.setuphandlers import setup_core_catalogs
from senaite.core.upgrade.utils import delete_object
from senaite.core.upgrade.utils import permanently_allow_type_for
from senaite.core.upgrade.v02_06_000 import get_setup_folder
from senaite.core.upgrade.v02_06_000 import profile
from senaite.core.upgrade.v02_06_000 import update_content_actions
from senaite.core.upgrade.v02_06_000 import remove_at_portal_types

from senaite.samplepointlocations import logger


def migrate_samplepoints_to_dx(tool):
    """Converts existing sample points to Dexterity
    """
    logger.info("Convert SamplePoints to Dexterity ...")

    # ensure old AT types are flushed first
    remove_at_portal_types(tool)

    # ensure new indexes
    portal = api.get_portal()
    setup_core_catalogs(portal)

    # run required import steps
    tool.runImportStepFromProfile(profile, "typeinfo")
    tool.runImportStepFromProfile(profile, "workflow")
    tool.runImportStepFromProfile(profile, "rolemap")

    # update content actions
    update_content_actions(tool)

    # allow to create the new DX based sample templates below clients
    permanently_allow_type_for("Client", "SamplePoint")

    # NOTE: Sample Points can be created in setup and client context!
    query = {"portal_type": "SamplePoint"}
    # search all AT based sample points
    brains = api.search(query, SETUP_CATALOG)
    total = len(brains)

    # get the old setup folder
    old_setup = api.get_setup().get("bika_samplepoints")
    # get the new setup folder
    new_setup = get_setup_folder("samplepoints")

    # get all objects first
    objects = map(api.get_object, brains)
    for num, obj in enumerate(objects):
        if api.is_dexterity_content(obj):
            # migrated already
            continue

        # get the current parent of the object
        origin = api.get_parent(obj)

        # get the destination container
        if origin == new_setup:
            # migrated already
            continue

        # migrate the object to dexterity
        if origin == old_setup:
            migrate_samplepoint_to_dx(obj, new_setup)
        else:
            migrate_samplepoint_to_dx(obj)

        logger.info("Migrated sample point {0}/{1}: {2} -> {3}".format(
            num, total, api.get_path(obj), api.get_path(obj)))

    if old_setup:
        # remove old AT folder
        if len(old_setup) == 0:
            delete_object(old_setup)
        else:
            logger.warn("Cannot remove {}. Is not empty".format(old_setup))

    logger.info("Convert SamplePoints to Dexterity [DONE]")


def migrate_samplepoint_to_dx(src, destination=None):
    """Migrates a Sample Point to DX in destination folder

    :param src: The source AT object
    :param destination: The destination folder. If `None`, the parent folder of
                        the source object is taken
    """

    # Create the object if it does not exist yet
    src_id = src.getId()
    target_id = src_id

    # check if we migrate within the same folder
    if destination is None:
        # use a temporary ID for the migrated content
        target_id = tmpID()
        # set the destination to the source parent
        destination = api.get_parent(src)

    target = destination.get(target_id)
    if not target:
        # Don' use the api to skip the auto-id generation
        target = createContent("SamplePoint", id=target_id)
        destination._setObject(target_id, target)
        target = destination._getOb(target_id)

    # Manually set the fields
    # NOTE: always convert string values to unicode for dexterity fields!
    target.title = api.safe_unicode(src.Title() or "")
    target.description = api.safe_unicode(src.Description() or "")

    # we set the fields with our custom setters
    target.setLatitude(src.getLatitude())
    target.setLongitude(src.getLongitude())
    target.setElevation(src.getElevation())
    target.setSampleTypes(src.getRawSampleTypes())
    target.setComposite(src.getComposite())

    # attachment file
    attachment = src.getAttachmentFile()
    if attachment:
        filename = attachment.filename
        new_attachment = NamedBlobFile(data=attachment.data,
                                       filename=api.safe_unicode(filename),
                                       contentType=attachment.content_type)
        target.setAttachmentFile(new_attachment)

    # sampling frequency
    freq = dict.fromkeys(["days", "hours", "minutes", "seconds"], 0)
    freq.update(src.getSamplingFrequency() or {})
    freq = dict([(key, api.to_int(val, 0)) for key, val in freq.items()])
    freq = timedelta(**freq)
    target.setSamplingFrequency(freq)

    # Migrate the contents from AT to DX
    migrator = getMultiAdapter(
        (src, target), interface=IContentMigrator)

    # copy all (raw) attributes from the source object to the target
    migrator.copy_attributes(src, target)

    # copy the UID
    migrator.copy_uid(src, target)

    # copy auditlog
    migrator.copy_snapshots(src, target)

    # copy creators
    migrator.copy_creators(src, target)

    # copy workflow history
    migrator.copy_workflow_history(src, target)

    # copy marker interfaces
    migrator.copy_marker_interfaces(src, target)

    # copy dates
    migrator.copy_dates(src, target)

    # uncatalog the source object
    migrator.uncatalog_object(src)

    # delete the old object
    migrator.delete_object(src)

    # change the ID *after* the original object was removed
    migrator.copy_id(src, target)

    return target

# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.core.upgrade import upgradestep
from senaite.samplepointlocations import PRODUCT_NAME
from senaite.samplepointlocations import logger
from senaite.core.setuphandlers import _run_import_step
from senaite.core.config import PROJECTNAME as product

version = "1.0.1"
profile = "profile-{0}:default".format(product)

ID_FORMATTING_SP = [
    {
        "portal_type": "SamplePoint",
        "form": "SP{seq:06d}",
        "prefix": "samplepoint",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    }
]


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    setup_id_formatting(portal)
    change_action_title(portal)
    _run_import_step(portal, "rolemap", profile="profile-bika.lims:default")
    setup.runImportStepFromProfile(profile, "typeinfo")
    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def change_action_title(portal):
    pt = api.get_tool("portal_types", context=portal)
    fti = pt.get("Client")
    actions = fti.listActions()
    for action in actions:
        if action.id == "samplepointlocations":
            action.title = "Sample Point Locations"
            logger.info("Changed action title to Sample Point Location")


def setup_id_formatting(portal, format_definition=None):
    """Setup default ID formatting"""
    if not format_definition:
        logger.info("Setting up ID formatting ...")
        for formatting in ID_FORMATTING_SP:
            setup_id_formatting(portal, format_definition=formatting)
        logger.info("Setting up ID formatting [DONE]")
        return

    bs = portal.bika_setup
    p_type = format_definition.get("portal_type", None)
    if not p_type:
        return

    form = format_definition.get("form", "")
    if not form:
        logger.info("Param 'form' for portal type {} not set [SKIP")
        return

    logger.info("Applying format '{}' for {}".format(form, p_type))
    ids = list()
    for record in bs.getIDFormatting():
        if record.get("portal_type", "") == p_type:
            continue
        ids.append(record)
    ids.append(format_definition)
    bs.setIDFormatting(ids)

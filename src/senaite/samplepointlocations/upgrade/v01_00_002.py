# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.core.upgrade import upgradestep
from senaite.samplepointlocations import PRODUCT_NAME
from senaite.samplepointlocations import logger
from senaite.core.setuphandlers import _run_import_step
from senaite.core.config import PROJECTNAME as product

version = "1.0.2"
profile = "profile-{0}:default".format(product)


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    rename_all_samplepointlocations(portal)
    _run_import_step(portal, "rolemap", profile="profile-bika.lims:default")
    setup.runImportStepFromProfile(profile, "typeinfo")
    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def rename_all_samplepointlocations(portal):
    logger.info("Renaming all Samplepoint Locations...")
    num = 0
    clients = portal.clients.objectValues()

    for client in clients:
        cid = client.getId()
        logger.info("Renaming SamplePointLocations of client {}...".format(cid))
        for client_object in client.values():
            if client_object.portal_type == "SamplePointLocation":
                import pdb;pdb.set_trace()
                num = num + 1
                # client_object.edit(id="SPL000001")
                client_object.setId("SPL000001")
                client_object.reindexObject()
        logger.info("Renamed SamplePointLocations of client {}...".format(cid))
    logger.info("Renamed a total of {} samplepointlocations, committing...".format(num))

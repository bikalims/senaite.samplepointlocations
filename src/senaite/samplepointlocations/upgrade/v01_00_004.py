# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.core.upgrade import upgradestep
from senaite.samplepointlocations import PRODUCT_NAME
from senaite.samplepointlocations import logger
from senaite.core.setuphandlers import _run_import_step
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.config import PROJECTNAME as product

version = "1.0.4"
profile = "profile-{0}:default".format(product)


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    update_sample_points(portal)
    update_sample_point_location(portal)

    _run_import_step(portal, "rolemap", profile="profile-bika.lims:default")
    setup.runImportStepFromProfile(profile, "typeinfo")
    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def update_sample_points(portal):
    query = {
    "portal_type": "SamplePoint",
    }
    brains = api.search(query, SETUP_CATALOG)
    for indx,sample in enumerate(brains):
        obj = sample.getObject()
        Sample_point_id = ''
        if hasattr(obj,"SystemId"):
            Sample_point_id = obj.SystemId
            obj.reindexObject()
        if Sample_point_id:
            obj.SamplePointId = Sample_point_id
            obj.reindexObject()


def update_sample_point_location(portal):
    query = {
    "portal_type": "SamplePointLocation",
    }
    brains = api.search(query, SETUP_CATALOG)
    for indx,sample in enumerate(brains):
        obj = sample.getObject()
        Sample_point_location_id = ''
        if hasattr(obj,"SystemLocationsId"):
            Sample_point_location_id = obj.SystemLocationsId
            obj.reindexObject()
        if hasattr(obj,"system_location_id"):
            Sample_point_location_id = obj.system_location_id
            obj.reindexObject()
        if Sample_point_location_id:
            obj.sample_point_location_id = Sample_point_location_id
            obj.reindexObject()

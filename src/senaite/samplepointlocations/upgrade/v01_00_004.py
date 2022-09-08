# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.core.upgrade import upgradestep
from senaite.samplepointlocations import PRODUCT_NAME
from senaite.samplepointlocations import logger
from senaite.core.catalog import SETUP_CATALOG

version = "1.0.4"


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    update_sample_points(portal)
    update_sample_point_location(portal)
    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def update_sample_points(portal):
    query = {
    "portal_type": "SamplePoint",
    }
    brains = api.search(query, SETUP_CATALOG)
    for indx,sample in enumerate(brains):
        obj = sample.getObject()
        obj.reindexObject()


def update_sample_point_location(portal):
    query = {
    "portal_type": "SamplePointLocation",
    }
    brains = api.search(query, SETUP_CATALOG)
    for indx,sample in enumerate(brains):
        obj = sample.getObject()
        System_location_id = ''
        if hasattr(obj,"SystemLocationsId"):
            System_location_id = obj.SystemLocationsId
            obj.reindexObject()
        if System_location_id:
            obj.system_location_id = System_location_id
            obj.reindexObject()

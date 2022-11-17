from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import ISamplePoint
from plone.indexer import indexer
from senaite.samplepointlocations.content.samplepointlocation import (
    ISamplePointLocation,
)
from senaite.samplepointlocations import logger


@indexer(ISamplePointLocation)
def location_client_uid(instance):
    return instance.aq_parent.UID()


@indexer(IAnalysisRequest)
def ar_location_title(instance):
    try:
        loc = instance.getSamplePointLocation()
        return loc.title
    except Exception:
        return ""


@indexer(ISamplePoint)
def sp_location_title(instance):
    try:
        loc = instance.getSamplePointLocation()
        return loc.title
    except Exception:
        return ""


@indexer(ISamplePoint)
def sp_location_uid(instance):
    try:
        loc = instance.getSamplePointLocation()
        if loc:
            return loc.UID()
    except Exception:
        logger.info("sp_location_uid: failed")
        return ""


@indexer(ISamplePointLocation)
def sp_location_id(instance):
    try:
        return instance.sample_point_location_id
    except Exception:
        logger.info("sp_location_id: failed")
        return ""


@indexer(ISamplePointLocation)
def sp_location_account_managers(instance):
    try:
        return instance.account_managers
    except Exception:
        logger.info("sp_location_account_managers: failed")
        return ""


@indexer(ISamplePoint)
def sp_id(instance):
    try:
        return instance.SamplePointId
    except Exception:
        logger.info("sp_id: failed")
        return ""

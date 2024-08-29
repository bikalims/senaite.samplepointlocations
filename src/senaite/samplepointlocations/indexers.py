from plone.indexer import indexer

from bika.lims import api
from bika.lims.interfaces import IAnalysisRequest
from senaite.core.interfaces import ISamplePoint
from senaite.samplepointlocations import logger
from senaite.samplepointlocations.content.samplepointlocation import (
    ISamplePointLocation,
)


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
    brain = getBrainSamplePointLocation(instance)
    return brain.Title


def getBrainSamplePointLocation(instance):
    try:
        sample_point_location = instance.sample_point_location
        if len(sample_point_location) == 1:
            uid = sample_point_location[0]
            return api.get_brain_by_uid(uid)
        elif len(sample_point_location) == 2 and sample_point_location[1] == "":
            uid = sample_point_location[0]
            return api.get_brain_by_uid(uid)
    except Exception:
        return ""


@indexer(ISamplePoint)
def sp_location_uid(instance):
    sample_point_location = instance.sample_point_location
    if sample_point_location:
        if len(sample_point_location) == 1:
            return sample_point_location[0]
        elif len(sample_point_location) == 2 and sample_point_location[1] == "":
            return sample_point_location[0]
    else:
        if instance.portal_type == "SamplePoint":
            parent = instance.aq_parent
            if parent.portal_type != "SamplePointLocation":
                return
            return parent.UID()


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
        return instance.sample_point_id
    except Exception:
        logger.info("sp_id: failed")
        return ""

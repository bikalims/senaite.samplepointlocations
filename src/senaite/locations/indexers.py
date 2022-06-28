from bika.lims.interfaces import IAnalysisRequest
from bika.lims.interfaces import ISamplePoint
from plone.indexer import indexer
from senaite.app.supermodel import SuperModel
from senaite.api import get_object_by_uid


@indexer(IAnalysisRequest)
def ar_location_title(instance):
    loc = instance.getLocation()
    return loc.title if loc else ""
    # try:
    #     model = SuperModel(instance)
    #     model_data = model.to_dict()
    #     loc = get_object_by_uid(model_data["Location"])
    #     return loc.title if loc else ""
    # except Exception:
    #     return ""


@indexer(ISamplePoint)
def sp_location_title(instance):
    try:
        model = SuperModel(instance)
        model_data = model.to_dict()
        loc = get_object_by_uid(model_data["SamplePointLocation"])
        return loc.title if loc else ""
    except Exception:
        return ""

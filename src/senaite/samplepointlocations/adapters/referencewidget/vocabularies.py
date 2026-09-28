# -*- coding: utf-8 -*-
from bika.lims.utils import get_client
from bika.lims import api
from senaite.core.adapters.referencewidget.vocabularies import (
    ClientAwareReferenceWidgetVocabulary as CARWV)
from senaite.core.adapters.referencewidget.vocabularies import (
    DefaultReferenceWidgetVocabulary)


class ClientAwareReferenceWidgetVocabulary(CARWV):
    """Injects search criteria (filters) in the query when the current context
    is, belongs or is associated to a Client
    """

    # portal_types that might be bound to a client
    client_bound_types = [
        "Contact",
        "Batch",
        "AnalysisProfile",
        "AnalysisSpec",
        "ARTemplate",
        "SamplePoint",
        "SamplePointLocation"
    ]

    samplepointlocation_bound_types = [
        "SamplePoint",
    ]

    def get_raw_query(self):
        """Returns the raw query to use for current search, based on the
        base query + update query
        """
        query = DefaultReferenceWidgetVocabulary.get_raw_query(self)

        portal_types = self.get_portal_types(query)
        if not set(portal_types).intersection(("SamplePointLocation", "SamplePoint")):
            return super(ClientAwareReferenceWidgetVocabulary, self).get_raw_query()

        field_name = self.request.get("field_name", "") or ""
        name, separator, column = field_name.rpartition("-")
        is_sample_add = name in ("SamplePoint", "SamplePointLocation") and column.isdigit()
        client = get_client(self.context)
        if client and "getClientUID" not in query:
            query["getClientUID"] = [api.get_uid(client), ""]

        if "SamplePointLocation" in portal_types:
            if is_sample_add and "getClientUID" not in query and "UID" not in query:
                query["UID"] = ""

        if "SamplePoint" in portal_types:
            # The unsaved form's explicit query takes precedence over context.
            if "getSamplePointLocationUID" not in query and "UID" not in query:
                getter = getattr(self.context, "getSamplePointLocation", None)
                location = getter() if callable(getter) else None
                if location:
                    query["getSamplePointLocationUID"] = api.get_uid(location)
                elif is_sample_add:
                    query["UID"] = ""
            if is_sample_add:
                query.pop("sampletype_uid", None)

        return query

    def is_samplepointlocation_aware(self, query):
        """Returns whether the query passed in requires a filter by samplepointlocation
        """
        portal_types = self.get_portal_types(query)
        intersect = set(portal_types).intersection(self.samplepointlocation_bound_types)
        return len(intersect) > 0

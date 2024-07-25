# -*- coding: utf-8 -*-
from bika.lims.utils import get_client
from senaite import api
from senaite.core.adapters.referencewidget.vocabularies import (
    ClientAwareReferenceWidgetVocabulary as CARWV)


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
        query = super(
            ClientAwareReferenceWidgetVocabulary, self).get_raw_query()

        context = self.context
        if self.is_client_aware(query):

            client = get_client(self.context)
            client_uid = client and api.get_uid(client) or None

            if client_uid:
                # Apply the search criteria for this client
                if "Contact" in self.get_portal_types(query):
                    query["getParentUID"] = [client_uid]
                else:
                    query["getClientUID"] = [client_uid, ""]

        if self.is_samplepointlocation_aware(query):
            if not hasattr(context, "getSamplePointLocation"):
                return query
            spl = context.getSamplePointLocation()
            samplepointlocation_uid = spl and api.get_uid(spl) or None
            if "SamplePoint" in self.get_portal_types(query):
                query["getSamplePointLocationUID"] = [samplepointlocation_uid, ""]

        return query

    def is_samplepointlocation_aware(self, query):
        """Returns whether the query passed in requires a filter by samplepointlocation
        """
        portal_types = self.get_portal_types(query)
        intersect = set(portal_types).intersection(self.samplepointlocation_bound_types)
        return len(intersect) > 0

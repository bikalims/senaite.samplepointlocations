from senaite import api
from senaite.locations import check_installed


def get_client_info(self, obj):
    """Returns the client info of an object"""
    info = self.get_base_info(obj)

    # Set the default contact, but only if empty. The Contact field is
    # flushed each time the Client changes, so we can assume that if there
    # is a selected contact, it belongs to current client already
    default_contact = self.get_default_contact(client=obj)
    if default_contact:
        contact_info = self.get_contact_info(default_contact)
        contact_info.update({"if_empty": True})
        info["field_values"].update({"Contact": contact_info})

    # Set default CC Email field
    info["field_values"].update(
        {"CCEmails": {"value": obj.getCCEmails(), "if_empty": True}}
    )

    # UID of the client
    uid = api.get_uid(obj)

    # catalog queries for UI field filtering
    filter_queries = {
        "Contact": {"getParentUID": [uid]},
        "CCContact": {"getParentUID": [uid]},
        "InvoiceContact": {"getParentUID": [uid]},
        "SamplePoint": {
            "getClientUID": [uid, ""],
        },
        "Template": {
            "getClientUID": [uid, ""],
        },
        "Profiles": {
            "getClientUID": [uid, ""],
        },
        "Specification": {
            "getClientUID": [uid, ""],
        },
        "Sample": {
            "getClientUID": [uid],
        },
        "Batch": {
            "getClientUID": [uid, ""],
        },
        "Location": {
            "getClientUID": [uid],
        },
    }
    info["filter_queries"] = filter_queries
    return info


def get_sampletype_info(self, obj):
    """Returns the info for a Sample Type"""
    info = self.get_base_info(obj)

    # client
    client = self.get_client()
    client_uid = client and api.get_uid(client) or ""

    info.update(
        {
            "prefix": obj.getPrefix(),
            "minimum_volume": obj.getMinimumVolume(),
            "hazardous": obj.getHazardous(),
            "retention_period": obj.getRetentionPeriod(),
        }
    )

    # catalog queries for UI field filtering
    sample_type_uid = api.get_uid(obj)
    filter_queries = {
        # Display Sample Points that have this sample type assigned plus
        # those that do not have a sample type assigned
        "SamplePoint": {
            "sampletype_uid": [sample_type_uid, None],
            "getClientUID": [client_uid, ""],
        },
        # Display Specifications that have this sample type assigned only
        "Specification": {
            "sampletype_uid": sample_type_uid,
            "getClientUID": [client_uid, ""],
        },
        # Display Location that have this sample type assigned only
        "Location": {
            "getClientUID": [client_uid],
        },
        # Display AR Templates that have this sample type assigned plus
        # those that do not have a sample type assigned
        "Template": {
            "sampletype_uid": [sample_type_uid, None],
            "getClientUID": [client_uid, ""],
        },
    }
    info["filter_queries"] = filter_queries
    return info


@check_installed(None)
def getLocation(self):  # noqa camelcase
    """Returns the AR's location"""
    return self.getField("Location").get(self)

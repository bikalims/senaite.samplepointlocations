from bika.lims.interfaces import IAddSampleFieldsFlush
from bika.lims.interfaces import IAddSampleObjectInfo
from collections import OrderedDict
from senaite import api
from senaite.samplepointlocations import check_installed
from senaite.samplepointlocations import logger
from zope.component import getAdapters


def get_record_metadata(self, record):
    """Returns the metadata for the record passed in"""
    metadata = OrderedDict()
    extra_fields = {}
    for key, value in record.items():
        if not key.endswith("_uid"):
            continue

        # This is a reference field (ends with _uid), so we add the
        # metadata key, even if there is no way to handle objects this
        # field refers to
        metadata_key = key.replace("_uid", "")
        metadata_key = "{}_metadata".format(metadata_key.lower())
        metadata[metadata_key] = {}

        if not value:
            continue

        logger.debug("------get_record_metadata: {}".format(metadata_key))

        # Get objects information (metadata)
        objs_info = self.get_objects_info(record, key)
        objs_uids = map(lambda obj: obj["uid"], objs_info)
        metadata[metadata_key] = dict(zip(objs_uids, objs_info))

        # Grab 'field_values' fields to be recalculated too
        for obj_info in objs_info:
            field_values = obj_info.get("field_values", {})
            for field_name, field_value in field_values.items():
                if not isinstance(field_value, dict):
                    # this is probably a list, e.g. "Profiles" field
                    continue
                uids = self.get_uids_from_record(field_value, "uid")
                if len(uids) == 1:
                    extra_fields[field_name] = uids[0]

    # Populate metadata with object info from extra fields (hidden fields)
    for field_name, uid in extra_fields.items():
        key = "{}_metadata".format(field_name.lower())
        if metadata.get(key):
            # This object has been processed already, skip
            continue
        obj = self.get_object_by_uid(uid)
        if not obj:
            continue
        obj_info = self.get_object_info(obj, field_name, record=extra_fields)
        if not obj_info or "uid" not in obj_info:
            continue
        metadata[key] = {obj_info["uid"]: obj_info}
    sort_ordered_dict_by_list(
        metadata,
        [
            "client_metadata",
            "samplepointlocation_metadata",
            "samplepoint_metadata",
            "sampletype_metadata",
        ],
    )
    logger.debug("get_record_metadata: {}".format(metadata))
    logger.debug("get_record_metadata: exit")
    return metadata


def get_object_info(self, obj, key, record=None):
    """Returns the object info metadata for the passed in object and key
    :param obj: the object from which extract the info from
    :param key: The key of the field from the record (e.g. Client_uid)
    :return: dict that represents the object
    """
    # Check if there is a function to handle objects for this field
    field_name = key.replace("_uid", "")
    func_name = "get_{}_info".format(field_name.lower())
    logger.debug("get_object_info: func_name = {}".format(func_name))
    # always ensure we have a record
    if record is None:
        record = {}

    if func_name == "get_samplepointlocation_info":
        info = self.get_base_info(obj)
        client = self.get_client()
        client_uid = client and api.get_uid(client) or ""
        info = get_samplepointlocation_info(obj, info, client_uid)
    elif func_name == "get_samplepoint_info":
        info = self.get_base_info(obj)
        client = self.get_client()
        client_uid = client and api.get_uid(client) or ""
        info = get_samplepoint_info(obj, info, client_uid)
    else:
        func = getattr(self, func_name, None)
        # Get the info for each object
        info = callable(func) and func(obj) or self.get_base_info(obj)

    # Check if there is any adapter to handle objects for this field
    for name, adapter in getAdapters((obj,), IAddSampleObjectInfo):
        logger.debug("adapter for '{}': {}".format(field_name, name))
        ad_info = adapter.get_object_info_with_record(record)
        self.update_object_info(info, ad_info)

    return info


def get_samplepointlocation_info(obj, info, client_uid):
    """Returns the client info of an object"""

    # catalog queries for UI field filtering
    location_uid = api.get_uid(obj)
    sp_query = {
        # "getSamplePointLocationUID": [location_uid, None],
        "getClientUID": [client_uid, ""],
    }
    sp_UIDs = []
    for sample_point in obj.values():
        if sample_point.portal_type == "SamplePoint":
            sp_UIDs.append(sample_point.UID())
    # catalog queries for UI field filtering
    sp_query["UID"] =  sp_UIDs

    filter_queries = {
        # Display Sample Points that have this sample type assigned plus
        # those that do not have a sample type assigned
        "SamplePoint": sp_query
    }
    info["filter_queries"] = filter_queries

    def get_account_managers_emailaddreses(account_managers):
        emails = []
        for index, uid in enumerate(account_managers):
            man = api.get_object_by_uid(uid)
            emails.append(man.getEmailAddress())
        return emails
    ac_man_emails = get_account_managers_emailaddreses(obj.account_managers)

    info["field_values"].update(
        {"CCEmails": {"value": ac_man_emails, "if_empty": True}}
    )

    return info


def get_samplepoint_info(obj, info, client_uid):
    """Returns the client info of an object"""

    UIDs = []
    for sample_type in obj.getSampleTypes():
        UIDs.append(sample_type.UID())
    # catalog queries for UI field filtering
    st_query = {"UID": UIDs}

    filter_queries = {
        # Display Sample Points that have this sample type assigned plus
        # those that do not have a sample type assigned
        "SampleType": st_query
    }
    info["filter_queries"] = filter_queries
    if len(UIDs) == 1:
        sample_uid = UIDs[0]
        sample_title = api.get_object_by_uid(sample_uid).Title()
        info["field_values"].update(
            {"SampleType": {"uid": sample_uid, "title": sample_title}}
        )

    return info


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
        "SamplePointLocation": {
            "getClientUID": [uid],
        },
    }
    info["filter_queries"] = filter_queries
    return info


def ajax_get_flush_settings(self):
    """Returns the settings for fields flush"""
    flush_settings = {
        "Client": [
            "Contact",
            "CCContact",
            "InvoiceContact",
            "SamplePoint",
            "Template",
            "Profiles",
            "PrimaryAnalysisRequest",
            "Specification",
            "Batch",
        ],
        "Contact": ["CCContact"],
        "SamplePointLocation": [
            "SamplePoint",
            "SampleType",
        ],
        "SamplePoint": [
            "SampleType",
        ],
        "SampleType": [
            "Specification",
            "Template",
        ],
        "PrimarySample": [
            "Batch" "Client",
            "Contact",
            "CCContact",
            "CCEmails",
            "ClientOrderNumber",
            "ClientReference",
            "ClientSampleID",
            "ContainerType",
            "DateSampled",
            "EnvironmentalConditions",
            "InvoiceContact",
            "Preservation",
            "Profiles",
            "SampleCondition",
            "SamplePoint",
            "SampleType",
            "SamplingDate",
            "SamplingDeviation",
            "StorageLocation",
            "Specification",
            "Template",
        ],
    }

    # Maybe other add-ons have additional fields that require flushing
    for name, ad in getAdapters((self.context,), IAddSampleFieldsFlush):
        logger.info("Additional flush settings from {}".format(name))
        additional_settings = ad.get_flush_settings()
        for key, values in additional_settings.items():
            new_values = flush_settings.get(key, []) + values
            flush_settings[key] = list(set(new_values))

    return flush_settings


@check_installed(None)
def getSamplePointLocation(self):  # noqa camelcase
    """Returns the AR's location"""
    return self.getField("SamplePointLocation").get(self)


def sort_ordered_dict_by_list(adict, alist):
    for key in alist:
        move_to_end(adict, key)


def move_to_end(adict, key):
    current = ()
    other = []
    for k, v in adict.items():
        if k == key:
            current = [
                (k, v),
            ]
        else:
            other.append((k, v))
    if other:
        adict.clear()
        adict.update(other)
        adict.update(current)

from bika.lims.interfaces import IAddSampleObjectInfo
from collections import OrderedDict
from senaite import api
from senaite.locations import check_installed
from senaite.locations import logger
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
        metadata, ["client_metadata", "sampletype_metadata", "location_metadata"]
    )
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

    if func_name == "get_location_info":
        info = self.get_base_info(obj)
        client = self.get_client()
        client_uid = client and api.get_uid(client) or ""
        sampletype_uid = None
        if len(record.get("SampleType_uid", "")) > 0:
            sampletype_uid = record["SampleType_uid"]
        info = get_location_info(obj, info, client_uid, sampletype_uid)
    else:
        func = getattr(self, func_name, None)
        # Get the info for each object
        info = callable(func) and func(obj) or self.get_base_info(obj)

    # Check if there is any adapter to handle objects for this field
    for name, adapter in getAdapters((obj,), IAddSampleObjectInfo):
        logger.info("adapter for '{}': {}".format(field_name, name))
        ad_info = adapter.get_object_info_with_record(record)
        self.update_object_info(info, ad_info)

    return info


def get_location_info(obj, info, client_uid, sampletype_uid):
    """Returns the client info of an object"""

    # catalog queries for UI field filtering
    location_uid = api.get_uid(obj)
    sp_query = {
        "getSamplePointLocationUID": [location_uid, None],
        "getClientUID": [client_uid, ""],
    }
    if sampletype_uid is not None:
        sp_query["sampletype_uid"] = [sampletype_uid, None]

    filter_queries = {
        # Display Sample Points that have this sample type assigned plus
        # those that do not have a sample type assigned
        "SamplePoint": sp_query
    }
    info["filter_queries"] = filter_queries

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
        "Location": {
            "getClientUID": [uid],
        },
    }
    info["filter_queries"] = filter_queries
    return info


@check_installed(None)
def getLocation(self):  # noqa camelcase
    """Returns the AR's location"""
    return self.getField("Location").get(self)


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

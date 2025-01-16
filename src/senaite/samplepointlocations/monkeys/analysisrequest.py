from bika.lims.interfaces import IAddSampleFieldsFlush
from bika.lims.interfaces import IAddSampleObjectInfo
from senaite import api
from senaite.samplepointlocations import check_installed
from senaite.samplepointlocations import logger
from zope.component import getAdapters


def get_record_metadata(self, record):
    """Returns the metadata for the record passed in
    """
    metadata = {}
    extra_fields = {}
    client_metadata = {}

    keys = sorted(record.keys())
    for key in keys:
        value = record[key]
        metadata_key = "{}_metadata".format(key.lower())
        metadata[metadata_key] = {}

        if not value:
            logger.info("get_record_metadata:key {}".format(key))
            continue

        # Get objects information (metadata)
        objs_info = self.get_objects_info(record, key, client_metadata)
        if key == "Client":
            client_metadata = objs_info[0]
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
        obj_info = self.get_object_info(
            obj, field_name, record=extra_fields)
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


def get_object_info(self, obj, key, record=None, client_metadata={}):
    """Returns the object info metadata for the passed in object and key
    :param obj: the object from which extract the info from
    :param key: The key of the field from the record (e.g. Client_uid)
    :return: dict that represents the object
    """
    # Check if there is a function to handle objects for this field
    field_name = key
    func_name = "get_{}_info".format(field_name.lower())
    func = getattr(self, func_name, None)

    # always ensure we have a record
    if record is None:
        record = {}

    # Get the info for each object
    if func_name == "get_samplepointlocation_info":
        info = self.get_base_info(obj)
        client = self.get_client()
        client_uid = client and api.get_uid(client) or ""
        info = get_samplepointlocation_info(obj, info, client_uid, client_metadata=client_metadata)
    elif func_name == "get_samplepoint_info":
        info = self.get_base_info(obj)
        client = self.get_client()
        client_uid = client and api.get_uid(client) or ""
        info = get_samplepoint_info(obj, info, client_uid)
    else:
        func = getattr(self, func_name, None)
        # Get the info for each object
        info = callable(func) and func(obj) or self.get_base_info(obj)

    # update query filters based on record values
    func_name = "get_{}_queries".format(field_name.lower())
    func = getattr(self, func_name, None)
    if callable(func):
        info["filter_queries"] = func(obj, record)

    # Check if there is any adapter to handle objects for this field
    for name, adapter in getAdapters((obj, ), IAddSampleObjectInfo):
        logger.info("adapter for '{}': {}".format(field_name, name))
        ad_info = adapter.get_object_info_with_record(record)
        self.update_object_info(info, ad_info)

    return info


def get_samplepointlocation_info(obj, info, client_uid, client_metadata={}):
    """Returns the client info of an object"""

    # catalog queries for UI field filtering

    # update client_metadata info
    if client_metadata:
        location_uid = obj.UID()
        filter_queries = client_metadata["filter_queries"]
        sp_query = filter_queries["SamplePoint"]
        sp_query["getSamplePointLocationUID"] = [location_uid, ""]
        client_metadata["filter_queries"]["SamplePoint"] = sp_query

    def get_account_managers_emailaddreses(account_managers):
        emails = []
        for index, contact in enumerate(account_managers):
            emails.append(contact.getEmailAddress())
        return emails
    ac_man_emails = get_account_managers_emailaddreses(obj.getAccountManagers())

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

    if UIDs:
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


def get_objects_info(self, record, key, client_metadata):
    """
    Returns a list with the metadata for the objects the field with
    field_name passed in refers to. Returns empty list if the field is not
    a reference field or the record for this key cannot be handled
    :param record: a record for a single sample (column)
    :param key: The key of the field from the record (e.g. Client_uid)
    :return: list of info objects
    """
    # Get the objects from this record. Returns a list because the field
    # can be multivalued
    uids = self.get_uids_from_record(record, key)
    objects = map(self.get_object_by_uid, uids)
    objects = map(lambda obj: self.get_object_info(
        obj, key, record=record, client_metadata=client_metadata), objects)
    return filter(None, objects)


def get_client_info(self, obj):
    """Returns the client info of an object
    """
    info = self.get_base_info(obj)

    # Set the default contact, but only if empty. The Contact field is
    # flushed each time the Client changes, so we can assume that if there
    # is a selected contact, it belongs to current client already
    default_contact = self.get_default_contact(client=obj)
    if default_contact:
        contact_info = self.get_contact_info(default_contact)
        contact_info.update({"if_empty": True})
        info["field_values"].update({
            "Contact": contact_info
        })

    # Set default CC Email field
    info["field_values"].update({
        "CCEmails": {"value": obj.getCCEmails(), "if_empty": True}
    })

    return info


def ajax_get_flush_settings(self):
    """Returns the settings for fields flush"""
    flush_settings = {
        "Client": [
        ],
        "Contact": [
        ],
        "SamplePointLocation": [
        ],
        "PrimarySample": [
            "EnvironmentalConditions",
        ]
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

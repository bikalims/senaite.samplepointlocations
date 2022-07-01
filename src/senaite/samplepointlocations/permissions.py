AddSamplePointLocation = "senaite.samplepointlocations: Add SamplePointLocation"

ADD_CONTENT_PERMISSIONS = {
    "SamplePointLocation": AddSamplePointLocation,
}


def setup_default_permissions(portal):
    mp = portal.manage_permission
    mp(AddSamplePointLocation, ["Manager", "LabManager", "LabClerk"], True)

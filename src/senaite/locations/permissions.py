AddLocation = "senaite.locations: Add Location"

ADD_CONTENT_PERMISSIONS = {
    "Location": AddLocation,
}


def setup_default_permissions(portal):
    mp = portal.manage_permission
    mp(AddLocation, ["Manager", "LabManager", "LabClerk"], True)

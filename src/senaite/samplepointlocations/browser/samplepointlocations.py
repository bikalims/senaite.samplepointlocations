import collections
from bika.lims import api
from bika.lims.utils import get_link
from senaite.app.listing import ListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.samplepointlocations.permissions import AddSamplePointLocation
from senaite.samplepointlocations import _


class SamplePointLocationsView(ListingView):
    def __init__(self, context, request):
        super(SamplePointLocationsView, self).__init__(context, request)
        self.catalog = SETUP_CATALOG
        path = api.get_path(self.context)
        self.contentFilter = dict(
            portal_type="SamplePointLocation", sort_on="created", path={"query": path}
        )
        self.form_id = "locations"

        self.context_actions = {
            _("Add"): {
                "url": "++add++SamplePointLocation",
                "permission": AddSamplePointLocation,
                "icon": "++resource++bika.lims.images/add.png",
            }
        }

        self.icon = "{}/{}/{}".format(
            self.portal_url, "/++resource++bika.lims.images", "sampletype_big.png"
        )

        self.title = "Sample Point Locations"
        self.description = self.context.Description()
        self.show_select_column = True

        self.columns = collections.OrderedDict(
            (
                ("location_id", dict(title=_("ID"), index="getId")),
                ("location_title", dict(title=_("Title"), index="Title")),
                (
                    "location_managers",
                    dict(title=_("Managers"), index="getManagers"),
                ),
                (
                    "location_address",
                    dict(title=_("Address"), index="getAddress"),
                ),
            )
        )

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "transitions": [
                    {"id": "deactivate"},
                ],
                "columns": self.columns.keys(),
            },
            {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {"is_active": False},
                "transitions": [
                    {"id": "activate"},
                ],
                "columns": self.columns.keys(),
            },
            {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        obj = api.get_object(obj)
        item["replace"]["location_id"] = get_link(
            href=api.get_url(obj), value=obj.getId()
        )
        item["replace"]["location_title"] = get_link(
            href=api.get_url(obj), value=obj.Title()
        )
        managers = []
        if len(obj.account_managers) > 0:
            for uid in obj.account_managers:
                man = api.get_object_by_uid(uid)
                managers.append(man.getFullname())
            item["replace"]["location_managers"] = ", ".join(managers)
        address_lst = []
        if len(obj.address) > 0:
            address = obj.address[0]
            if address.get("address"):
                address_lst.append(address["address"])
            if address.get("city"):
                address_lst.append(address["city"])
            if address.get("zip"):
                address_lst.append(address["zip"])
            if address.get("subdivision1"):
                address_lst.append(address["subdivision1"])
            if address.get("country"):
                address_lst.append(address["country"])
        item["replace"]["location_address"] = get_link(
            href=api.get_url(obj), value=", ".join(address_lst)
        )
        return item

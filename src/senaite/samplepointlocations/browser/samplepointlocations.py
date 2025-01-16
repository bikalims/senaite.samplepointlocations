import collections
from bika.lims import api
from bika.lims.api import safe_unicode as su
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
            portal_type="SamplePointLocation", sort_on="sortable_title", sort_order="ascending", path={"query": path}
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
                (
                    "sample_point_location_id",
                    dict(
                        title=_("Sample Point Location ID"),
                    ),
                ),
                ("location_title", dict(title=_("Title"), index="Title")),
                ("summary", dict(title=_("Summary"))),
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
        sample_point_location_id_var = obj.sample_point_location_id
        if sample_point_location_id_var:
            item["replace"]["sample_point_location_id"] = get_link(
                href=api.get_url(obj), value=sample_point_location_id_var
            )
        item["replace"]["location_title"] = get_link(
            href=api.get_url(obj), value=obj.Title()
        )
        item["summary"] = obj.description
        managers = []
        if obj.account_managers and len(obj.account_managers) > 0:
            for uid in obj.account_managers:
                man = api.get_object_by_uid(uid)
                managers.append(man.getFullname())
            item["replace"]["location_managers"] = ", ".join(managers)
        address_lst = []
        if obj.address and len(obj.address) > 0:
            address = obj.address[0]
            if address.get("address"):
                address_lst.append(su(address["address"]).unicode("utf-8"))
            if address.get("city"):
                address_lst.append(su(address["city"]).unicode("utf-8"))
            if address.get("zip"):
                address_lst.append(su(address["zip"]).unicode("utf-8"))
            if address.get("subdivision1"):
                address_lst.append(
                    su(address["subdivision1"]).unicode("utf-8"))
            if address.get("country"):
                address_lst.append(su(address["country"]).unicode("utf-8"))
        if address_lst:
            item["replace"]["location_address"] = get_link(
                href=api.get_url(obj), value=", ".join(address_lst)
            )
        return item

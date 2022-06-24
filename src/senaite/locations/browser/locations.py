import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _b
from bika.lims.utils import get_link
from senaite.app.listing import ListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.locations.permissions import AddLocation
from senaite.locations import _


class LocationsView(ListingView):
    def __init__(self, context, request):
        super(LocationsView, self).__init__(context, request)
        self.catalog = SETUP_CATALOG
        path = api.get_path(self.context)
        self.contentFilter = dict(
            portal_type="Location", sort_on="created", path={"query": path}
        )
        self.form_id = "locations"

        self.context_actions = {
            _("Add"): {
                "url": "++add++Location",
                "permission": AddLocation,
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
        item["replace"]["location_address"] = get_link(
            href=api.get_url(obj), value=obj.address
        )
        return item

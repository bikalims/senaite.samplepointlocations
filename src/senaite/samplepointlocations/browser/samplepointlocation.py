import collections
from bika.lims import api
from bika.lims.permissions import AddSamplePoint
from bika.lims.utils import get_link
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from senaite.app.listing import ListingView
from senaite.core.catalog import SETUP_CATALOG
from senaite.samplepointlocations import _

# from senaite.samplepointlocations import logger


class SamplePointLocationView(ListingView):
    template = ViewPageTemplateFile("templates/samplepointlocation_view.pt")

    def __init__(self, context, request):
        super(SamplePointLocationView, self).__init__(context, request)
        self.catalog = SETUP_CATALOG
        path = api.get_path(self.context)
        self.contentFilter = dict(
            portal_type="SamplePoint",
            sort_on="sortable_title",
            sort_order="ascending",
            path={"query": path},
        )
        self.form_id = "locations"

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=SamplePoint",
                "permission": AddSamplePoint,
                "icon": "++resource++bika.lims.images/add.png",
            }
        }

        self.icon = "{}/{}/{}".format(
            self.portal_url, "/++resource++bika.lims.images", "sampletype_big.png"
        )

        self.title = "Sample Points"
        self.description = self.context.Description()
        self.show_select_column = True

        self.columns = collections.OrderedDict(
            (
                ("SamplePointId", dict(title=_("Sample Point ID"))),
                ("location_title", dict(title=_("Title"), index="Title")),
                (
                    "sample_types",
                    dict(
                        title=_("Sample Type"),
                    ),
                ),
                (
                    "equipment_id",
                    dict(
                        title=_("Equipment ID"),
                    ),
                ),
                (
                    "equipment_type",
                    dict(
                        title=_("Equipment Type"),
                    ),
                ),
                (
                    "equipment_description",
                    dict(
                        title=_("Equipment Description"),
                    ),
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
        if hasattr(obj,'SamplePointId'):
            sample_point_id = obj.SamplePointId
            if sample_point_id:
                item["replace"]["SamplePointId"] = get_link(
                    href=api.get_url(obj), value=sample_point_id
                )
        item["replace"]["location_title"] = get_link(
            href=api.get_url(obj), value=obj.Title()
        )
        sample_types = obj.getSampleTypes()
        type_titles = []
        for sample_type in sample_types:
            type_titles.append(sample_type.Title())
        item["sample_types"] = type_titles
        item["equipment_id"] = obj.equipment_id
        item["equipment_type"] = obj.equipment_type
        item["equipment_description"] = obj.equipment_description
        return item

    def get_fields(self):
        address_lst = []
        if self.context.address and len(self.context.address) > 0:
            address = self.context.address[0]
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
        managers = []
        if self.context.account_managers and len(self.context.account_managers) > 0:
            for uid in self.context.account_managers:
                man = api.get_object_by_uid(uid)
                managers.append(man.getFullname())
        return [
            {
                "title": "Sample Point Location ID",
                "value": self.context.getSamplePointLocationID(),
            },
            {"title": "Account Managers", "value": ", ".join(managers)},
            {"title": "Address ", "value": ", ".join(address_lst)},
            {
                "title": "Summary",
                "value": self.context.description,
            },
        ]

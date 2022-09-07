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
            portal_type="SamplePoint", sort_on="created", path={"query": path}
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

        self.title = "Systems"
        self.description = self.context.Description()
        self.show_select_column = True

        self.columns = collections.OrderedDict(
            (
                ("system_id", dict(title=_("System ID"))),
                ("location_title", dict(title=_("Title"), index="Title")),
                ("sample_types", dict(title=_("Sample Type"),)),
                ("equipment_id", dict(title=_("Equipment ID"),)),
                ("equipment_type", dict(title=_("Equipment Type"),)),
                ("equipment_description", dict(title=_("Equipment Description"),)),
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
        System_Id = obj.SystemId
        if System_Id:
            item["replace"]["system_id"] = get_link(
                href=api.get_url(obj), value=System_Id
            )
        item["replace"]["location_title"] = get_link(
            href=api.get_url(obj), value=obj.Title()
        )
        Sample_types = obj.getSampleTypes()
        Type_titles = []
        for sample_type in Sample_types:
            Type_titles.append(sample_type.Title())
        item["sample_types"] = Type_titles
        item["equipment_id"] = obj.EquipmentID
        item["equipment_type"] = obj.EquipmentType
        item["equipment_description"] = obj.EquipmentDescription
        return item

    def get_fields(self):
        address_lst = []
        if len(self.context.address) > 0:
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
        if len(self.context.account_managers) > 0:
            for uid in self.context.account_managers:
                man = api.get_object_by_uid(uid)
                managers.append(man.getFullname())
        return [
            {"title": "System Location ID", "value": self.context.system_location_id},
            {"title": "Account Managers", "value": ", ".join(managers)},
            {"title": "Address ", "value": ", ".join(address_lst)},
        ]

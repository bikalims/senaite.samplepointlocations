from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from bika.lims import FieldEditContact
from bika.lims import SETUP_CATALOG
from bika.lims.interfaces import IAnalysisRequest
from Products.CMFCore.permissions import View
from senaite.core.browser.widgets import ReferenceWidget
from senaite.locations.extenders.fields import ExtReferenceField
from senaite.locations.interfaces import ISenaiteLocationsLayer
from senaite.locations import _
from zope.component import adapts
from zope.interface import implementer

location_field = ExtReferenceField(
    "Location",
    required=False,
    allowed_types=("Location",),
    relationship="AnalysisRequestLocation",
    format="select",
    mode="rw",
    read_permission=View,
    write_permission=FieldEditContact,
    widget=ReferenceWidget(
        label=_(u"Sample Point Location"),
        render_own_label=True,
        size=20,
        catalog_name=SETUP_CATALOG,
        base_query={"sort_on": "sortable_title"},
        showOn=True,
        visible={
            "add": "edit",
            "header_table": "prominent",
            "secondary": "disabled",
            "verified": "view",
            "published": "view",
        },
        ui_item="title",
        colModel=[
            dict(columnName="UID", hidden=True),
            dict(columnName="title", width="60", label=_("Title")),
        ],
    ),
)


@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class AnalysisRequestSchemaExtender(object):
    adapts(IAnalysisRequest)
    layer = ISenaiteLocationsLayer

    fields = [
        location_field,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields

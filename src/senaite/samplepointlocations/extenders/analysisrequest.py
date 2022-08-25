from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims import FieldEditContact
from bika.lims import SETUP_CATALOG
from bika.lims.interfaces import IAnalysisRequest
from Products.CMFCore.permissions import View
from senaite.samplepointlocations.extenders.fields import ExtReferenceField
from senaite.samplepointlocations.interfaces import ISenaiteSamplePointLocationsLayer
from senaite.samplepointlocations import _
from .utils import ClientAwareReferenceWidget
from zope.component import adapts
from zope.interface import implementer
from zope.interface import implements

location_field = ExtReferenceField(
    "SamplePointLocation",
    required=False,
    allowed_types=("SamplePointLocation",),
    relationship="AnalysisRequestSamplePointLocation",
    format="select",
    mode="rw",
    read_permission=View,
    write_permission=FieldEditContact,
    # accessor="getSamplePointLocation",
    # edit_accessor="getSamplePointLocation",
    # mutator="setSamplePointLocation",
    widget=ClientAwareReferenceWidget(
        label=_(u"System Location"),
        render_own_label=True,
        size=20,
        catalog_name=SETUP_CATALOG,
        base_query={"sort_on": "sortable_title", "is_active": True},
        showOn=True,
        visible={
            "add": "edit",
            "header_table": "visible",
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
    layer = ISenaiteSamplePointLocationsLayer

    fields = [
        location_field,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields


class AnalysisRequestSchemaModifier(object):
    adapts(IAnalysisRequest)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """
        """
        schema['SamplePoint'].widget.label = "System"

        return schema

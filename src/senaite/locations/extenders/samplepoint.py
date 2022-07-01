from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims import FieldEditContact
from bika.lims import SETUP_CATALOG
from bika.lims.interfaces import ISamplePoint
from collections import OrderedDict
from Products.CMFCore.permissions import View
from senaite.locations.extenders.fields import ExtReferenceField
from senaite.locations.interfaces import ISenaiteLocationsLayer
from senaite.locations import _
from .utils import ClientAwareReferenceWidget
from zope.component import adapts
from zope.interface import implementer


sample_point_location_field = ExtReferenceField(
    "SamplePointLocation",
    required=False,
    allowed_types=("Location",),
    relationship="SamplePointLocationLocation",
    format="select",
    mode="rw",
    read_permission=View,
    write_permission=FieldEditContact,
    widget=ClientAwareReferenceWidget(
        label=_(u"Sample Point Location"),
        description=_(u"The location where the sample point can be found"),
        render_own_label=False,
        size=20,
        catalog_name=SETUP_CATALOG,
        base_query={
            "is_active": True,
            "sort_on": "sortable_title",
            "sort_order": "ascending",
        },
        showOn=True,
        visible={"edit": "visible", "view": "visible"},
        ui_item="Title",
        colModel=[
            dict(columnName="UID", hidden=True),
            dict(columnName="Title", width="60", label=_("Title")),
        ],
    ),
)


@implementer(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
class SamplePointSchemaExtender(object):
    adapts(ISamplePoint)
    layer = ISenaiteLocationsLayer

    fields = [
        sample_point_location_field,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        # return schematas
        result = OrderedDict(
            [
                (
                    "default",
                    [
                        "id",
                        "title",
                        "allowDiscussion",
                        "subject",
                        "description",
                        "SamplePointLocation",
                        "location",
                        "contributors",
                        "creators",
                        "effectiveDate",
                        "expirationDate",
                        "language",
                        "rights",
                        "creation_date",
                        "modification_date",
                        "SamplingFrequency",
                        "SampleTypes",
                        "Composite",
                        "Latitude",
                        "Longitude",
                        "Elevation",
                        "AttachmentFile",
                    ],
                )
            ]
        )
        return result

    def getFields(self):
        return self.fields


@implementer(ISchemaModifier, IBrowserLayerAwareExtender)
class SamplePointSchemaModifier(object):
    """Change Schema Fields"""

    adapts(ISamplePoint)
    layer = ISenaiteLocationsLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        for field in schema.fields():
            field.schemata = "default"
        return schema

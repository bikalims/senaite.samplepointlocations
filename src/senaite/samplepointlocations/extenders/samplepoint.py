from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims import FieldEditContact
from bika.lims import SETUP_CATALOG
from bika.lims.interfaces import ISamplePoint
from collections import OrderedDict
from Products.CMFCore.permissions import View
from senaite.samplepointlocations.extenders.fields import ExtReferenceField
from senaite.samplepointlocations.interfaces import ISenaiteSamplePointLocationsLayer
from senaite.samplepointlocations import _
from senaite.samplepointlocations import logger
from .utils import ClientAwareReferenceWidget
from zope.component import adapts
from zope.interface import implementer


sample_point_location_field = ExtReferenceField(
    "SamplePointLocation",
    required=False,
    allowed_types=("SamplePointLocation",),
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
        visible={"edit": "hidden", "view": "visible"},
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
    layer = ISenaiteSamplePointLocationsLayer

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
    layer = ISenaiteSamplePointLocationsLayer

    def __init__(self, context):
        self.context = context

    def _get_parent_location(self):
        parent = self.context
        while True:
            if parent.portal_type == "SamplePointLocation":
                return parent.UID()
            parent = parent.aq_parent

    def fiddle(self, schema):
        for field in schema.fields():
            field.schemata = "default"
        return schema


def handleObjectAdded(obj, event):
    if obj.isTemporary():
        return
    if obj.portal_type == "SamplePoint":
        obj.setSamplePointLocation(obj.aq_parent)
        logger.info(
            "handleObjectAdded: {} -> {}".format(
                obj.getSamplePointLocation().Title(), obj.aq_parent.Title()
            )
        )


def handleObjectModified(obj, event):
    if obj.portal_type == "SamplePoint":
        obj.setSamplePointLocation(obj.aq_parent)
        logger.info(
            "handleObjectModified: {} -> {}".format(
                obj.getSamplePointLocation().Title(), obj.aq_parent.Title()
            )
        )

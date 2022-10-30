from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from bika.lims import FieldEditContact
from bika.lims.interfaces import ILabContact
from .fields import ExtStringField
from Products.Archetypes.Widget import StringWidget
from Products.CMFCore.permissions import View
from senaite.samplepointlocations.interfaces import ISenaiteSamplePointLocationsLayer
from senaite.samplepointlocations import _
from zope.component import adapts
from zope.interface import implementer

contact_id_field = ExtStringField(
    "ContactId",
    required=False,
    mode="rw",
    read_permission=View,
    write_permission=FieldEditContact,
    widget=StringWidget(
        size=30,
        label=_(u"Contact ID"),
    ),
)


@implementer(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
class LabContactSchemaExtender(object):
    adapts(ILabContact)
    layer = ISenaiteSamplePointLocationsLayer

    fields = [
        contact_id_field,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields

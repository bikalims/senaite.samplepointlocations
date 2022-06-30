from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from bika.lims import FieldEditContact
from bika.lims import SETUP_CATALOG
from bika.lims.interfaces import ISamplePoint
from bika.lims.utils import get_client
from collections import OrderedDict
import json
from Products.Archetypes.Registry import registerWidget
from Products.CMFCore.permissions import View
from senaite import api
from senaite.core.browser.widgets import ReferenceWidget
from senaite.locations.extenders.fields import ExtReferenceField
from senaite.locations.interfaces import ISenaiteLocationsLayer
from senaite.locations import _
import six
from zope.component import adapts
from zope.interface import implementer


class ClientAwareReferenceWidget(ReferenceWidget):
    _properties = ReferenceWidget._properties.copy()

    def get_base_query(self, context, fieldName):
        base_query = self.base_query
        if callable(base_query):
            try:
                base_query = base_query(context, self, fieldName)
            except TypeError:
                base_query = base_query()
        if base_query and isinstance(base_query, six.string_types):
            base_query = json.loads(base_query)

        # portal_type: use field allowed types
        field = context.Schema().getField(fieldName)
        allowed_types = getattr(field, "allowed_types", None)
        allowed_types_method = getattr(field, "allowed_types_method", None)
        if allowed_types_method:
            meth = getattr(context, allowed_types_method)
            allowed_types = meth(field)
        # If field has no allowed_types defined, use widget"s portal_type prop
        base_query["portal_type"] = (
            allowed_types if allowed_types else self.portal_types
        )
        client = get_client(context)
        client_uid = client and api.get_uid(client) or None

        if client_uid:
            # Apply the search criteria for this client
            # Contact is the only object bound to a Client that is stored
            # in portal_catalog. And in this catalog, getClientUID does not
            # exist, rather getParentUID
            if "Contact" in allowed_types:
                base_query["getParentUID"] = [client_uid]
            else:
                base_query["getClientUID"] = [client_uid, ""]
        return json.dumps(base_query)


registerWidget(ClientAwareReferenceWidget, title="Client aware Reference Widget")


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

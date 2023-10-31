# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from plone.autoform import directives
from bika.lims.interfaces import IDeactivable
from plone.dexterity.content import Container
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.schema import AddressField
from senaite.core.schema import UIDReferenceField
from senaite.core.schema.addressfield import PHYSICAL_ADDRESS
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from senaite import api
from senaite.samplepointlocations import _
from zope.interface import implementer
from zope.schema import TextLine
from senaite.core.catalog import CONTACT_CATALOG


class ISamplePointLocation(model.Schema):
    """Marker interface and Dexterity Python Schema for SamplePointLocation"""

    sample_point_location_id = TextLine(
        title=_("Sample Point Location ID"),
        required=True,
    )
    directives.widget(
        "account_managers",
        UIDReferenceWidgetFactory,
        catalog=CONTACT_CATALOG,
        query="get_contacts_query",
        display_template="<a href='${url}'>${title}</a>",
        columns=[
            {
                "name": "title",
                "width": "30",
                "align": "left",
                "label": _(u"Title"),
            },
        ],
        limit=4,
    )
    account_managers = UIDReferenceField(
        title=_(u"Account Managers"),
        allowed_types=("LabContact",),
        multi_valued=True,
        description=_(u"Sample point location manager/s"),
        required=False,
    )
    address = AddressField(
        title=_("Address"),
        address_types=[PHYSICAL_ADDRESS],
    )


@implementer(ISamplePointLocation, IDeactivable)
class SamplePointLocation(Container):
    """Content-type class for ISamplePointLocation"""

    _catalogs = [SETUP_CATALOG]

    security = ClassSecurityInfo()

    @security.private
    def accessor(self, fieldname):
        """Return the field accessor for the fieldname"""
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        return schema[fieldname].get

    @security.private
    def mutator(self, fieldname):
        """Return the field mutator for the fieldname"""
        schema = api.get_schema(self)
        if fieldname not in schema:
            return None
        result = schema[fieldname].set
        self.reindexObject()
        return result

    @security.protected(permissions.View)
    def getAccountManagers(self):
        """Returns the account_managers"""
        accessor = self.accessor("account_managers")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAccountManagers(self, value):
        """Set account_managers by the field accessor"""
        mutator = self.mutator("account_managers")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getSamplePointLocationID(self):
        """Returns the sample_point_location_id"""
        accessor = self.accessor("sample_point_location_id")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setSamplePointLocationID(self, value):
        """Set sample_point_location_id by the field accessor"""
        mutator = self.mutator("sample_point_location_id")
        return mutator(self, value)

    @security.protected(permissions.View)
    def getAddress(self):
        """Returns the address"""
        accessor = self.accessor("address")
        return accessor(self)

    @security.protected(permissions.ModifyPortalContent)
    def setAddress(self, value):
        """Set address by the field accessor"""
        mutator = self.mutator("address")
        return mutator(self, value)

    @security.private
    def get_contacts_query(self):
        """Return the query for the account managers field"""
        return {
            "portal_type": "LabContact",
            "is_active": True,
            "sort_on": "title",
            "sort_order": "asscending",
        }

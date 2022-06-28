# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from bika.lims.interfaces import IDeactivable
from plone.dexterity.content import Container
from plone.supermodel import model
from Products.CMFCore import permissions
from senaite.core.catalog import SETUP_CATALOG
from senaite import api
from senaite.locations import _
from zope import schema
from zope.interface import implementer


class ILocation(model.Schema):
    """Marker interface and Dexterity Python Schema for Location"""

    address = schema.TextLine(title=_(u"Address"), required=False)


@implementer(ILocation, IDeactivable)
class Location(Container):
    """Content-type class for ILocation"""

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
        return schema[fieldname].set

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

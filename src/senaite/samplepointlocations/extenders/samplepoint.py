from Products.CMFPlone.utils import safe_hasattr
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from zope.interface import implementer
from zope.component import adapter
from zope.interface import provider

from senaite.core.schema import UIDReferenceField
from senaite.core.z3cform.widgets.uidreference import UIDReferenceWidgetFactory
from senaite.core.catalog import SETUP_CATALOG
from senaite.samplepointlocations import _
from senaite.samplepointlocations import logger
from senaite.samplepointlocations import is_installed


class IExtendedSamplePointMarker(Interface):
    pass


@provider(IFormFieldProvider)
class IExtendedSamplePoint(model.Schema):
    """
    Extended Page content type schema with an extra field
    """

    sample_point_id = schema.TextLine(
        title=_("Sample Point ID"),
        required=False,
    )
    directives.widget(
        "sample_point_location",
        UIDReferenceWidgetFactory,
        catalog=SETUP_CATALOG,
        query={"sort_on": "title", },
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
    sample_point_location = UIDReferenceField(
        title=_(u"Sample Point Location"),
        allowed_types=("SamplePointLocation",),
        multi_valued=False,
        description=_(u"The location where the sample point can be found"),
        required=False,
    )
    equipment_id = schema.TextLine(
        title=_("Equipment ID"),
        description=_(u"The equipment id used on the sample point"),
        required=False,
    )
    equipment_type = schema.TextLine(
        title=_("Equipment Type"),
        description=_(u"The equipment type used on the sample point"),
        required=False,
    )
    equipment_description = schema.TextLine(
        title=_("Equipment Description"),
        description=_(u"The equipment type used on the sample point"),
        required=False,
    )


@implementer(IExtendedSamplePoint)
@adapter(IExtendedSamplePointMarker)
class ExtendedSamplePoint(object):
    def __init__(self, context):
        self.context = context

    @property
    def sample_point_id(self):
        if safe_hasattr(self.context, 'sample_point_id'):
            return self.context.sample_point_id
        return None

    @sample_point_id.setter
    def sample_point_id(self, value):
        self.context.sample_point_id = value

    @property
    def equipment_id(self):
        if safe_hasattr(self.context, 'equipment_id'):
            return self.context.equipment_id
        return None

    @equipment_id.setter
    def equipment_id(self, value):
        self.context.equipment_id = value

    @property
    def equipment_type(self):
        if safe_hasattr(self.context, 'equipment_type'):
            return self.context.equipment_type
        return None

    @equipment_type.setter
    def equipment_type(self, value):
        self.context.equipment_type = value

    @property
    def equipment_description(self):
        if safe_hasattr(self.context, 'equipment_description'):
            return self.context.equipment_description
        return None

    @equipment_description.setter
    def equipment_description(self, value):
        self.context.equipment_description = value


def handleObjectAdded(obj, event):
    if obj.isTemporary():
        return
    if obj.portal_type == "SamplePoint":
        parent = obj.aq_parent
        if parent.portal_type != "SamplePointLocation":
            return
        obj.sample_point_location = [parent.UID()]
        logger.info(
            "handleObjectAdded: {} -> {}".format(
                parent.Title(), obj.Title()
            )
        )


def handleObjectModified(obj, event):
    if not is_installed():
        return
    if obj.portal_type == "SamplePoint":
        parent = obj.aq_parent
        if parent.portal_type != "SamplePointLocation":
            return
        obj.sample_point_location = [parent.UID()]
        logger.info(
            "handleObjectModified: {} -> {}".format(
                parent.Title(), obj.Title()
            )
        )

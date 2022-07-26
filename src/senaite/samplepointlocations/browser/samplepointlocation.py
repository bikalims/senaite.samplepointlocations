from bika.lims import SETUP_CATALOG
from bika.lims.api import get_uid
from bika.lims.api import get_url
from bika.lims.api import search
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.browser import edit
from senaite.samplepointlocations import logger


class SamplePointLocationEditForm(edit.DefaultEditForm):
    template = ViewPageTemplateFile("templates/samplepointlocation_edit.pt")
    label = "Sample Point Location"

    def get_sample_types(self):
        types = []
        brains = search(
            {
                "portal_type": "SamplePoint",
                "getSamplePointLocationUID": get_uid(self.context),
            },
            SETUP_CATALOG,
        )
        for brain in brains:
            types.append({"title": brain.Title, "url": brain.getURL()})
        return types

    def get_add_link(self):
        return "{}/createObject?type_name=SamplePoint".format(get_url(self.context))

    def update(self):
        logger.info("SamplePointLocationEditForm: update")
        super(SamplePointLocationEditForm, self).update()

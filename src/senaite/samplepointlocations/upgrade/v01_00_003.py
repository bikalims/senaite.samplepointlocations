# -*- coding: utf-8 -*-

from bika.lims import api
from senaite.core.upgrade import upgradestep
from senaite.samplepointlocations import PRODUCT_NAME
from senaite.samplepointlocations import logger

version = "1.0.3"

ID_FORMATTING_SP = [
    {
        "portal_type": "SamplePoint",
        "form": "SP{seq:06d}",
        "prefix": "samplepoint",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    }
]


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup_id_formatting(portal)
    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True


def setup_id_formatting(portal, format_definition=None):
    """Setup default ID formatting"""
    if not format_definition:
        logger.info("Setting up ID formatting ...")
        for formatting in ID_FORMATTING_SP:
            setup_id_formatting(portal, format_definition=formatting)
        logger.info("Setting up ID formatting [DONE]")
        return

    bs = portal.bika_setup
    p_type = format_definition.get("portal_type", None)
    if not p_type:
        return

    form = format_definition.get("form", "")
    if not form:
        logger.info("Param 'form' for portal type {} not set [SKIP")
        return

    logger.info("Applying format '{}' for {}".format(form, p_type))
    ids = list()
    for record in bs.getIDFormatting():
        if record.get("portal_type", "") == p_type:
            continue
        ids.append(record)
    ids.append(format_definition)
    bs.setIDFormatting(ids)

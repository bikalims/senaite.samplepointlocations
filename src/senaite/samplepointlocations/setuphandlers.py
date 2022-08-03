from bika.lims import api
from plone.registry.interfaces import IRegistry
from Products.CMFPlone.interfaces import INonInstallable
from senaite.samplepointlocations import logger
from senaite.samplepointlocations import PRODUCT_NAME
from senaite.samplepointlocations import PROFILE_ID
from senaite.core.catalog import SAMPLE_CATALOG
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.setuphandlers import _run_import_step
from senaite.core.setuphandlers import setup_other_catalogs
from zope.component import getUtility
from zope.interface import implementer

# Tuples of (catalog, index_name, index_attribute, index_type)
INDEXES = [
    (SETUP_CATALOG, "getSamplePointLocation", "", "FieldIndex"),
    (SETUP_CATALOG, "getSamplePointLocationUID", "", "FieldIndex"),
]

# Tuples of (catalog, column_name)
COLUMNS = [
    (SETUP_CATALOG, "getSamplePointLocation"),
    (SETUP_CATALOG, "getSamplePointLocationUID"),
]

NAVTYPES = []

# An array of dicts. Each dict represents an ID formatting configuration
ID_FORMATTING = [
    {
        "portal_type": "SamplePointLocation",
        "form": "SPL{seq:06d}",
        "prefix": "location",
        "sequence_type": "generated",
        "counter_type": "",
        "split_length": 1,
    }
]


def setup_handler(context):
    """Generic setup handler"""
    if context.readDataFile("{}.txt".format(PRODUCT_NAME)) is None:
        return

    logger.info("{} setup handler [BEGIN]".format(PRODUCT_NAME.upper()))
    portal = context.getSite()

    add_location_to_client(portal)
    remove_client_sample_types_action(portal)

    # Configure visible navigation items
    setup_navigation_types(portal)

    # Setup catalogs
    setup_catalogs(portal)

    # Apply ID format to content types
    setup_id_formatting(portal)

    logger.info("{} setup handler [DONE]".format(PRODUCT_NAME.upper()))


def pre_install(portal_setup):
    """Runs before the first import step of the *default* profile
    This handler is registered as a *pre_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} pre-install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)  # noqa
    portal = context.getSite()  # noqa

    logger.info("{} pre-install handler [DONE]".format(PRODUCT_NAME.upper()))


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)  # noqa
    portal = context.getSite()  # noqa

    _run_import_step(portal, "workflow", PROFILE_ID)
    logger.info("{} install handler [DONE]".format(PRODUCT_NAME.upper()))


def post_uninstall(portal_setup):
    """Runs after the last import step of the *uninstall* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} uninstall handler [BEGIN]".format(PRODUCT_NAME.upper()))

    # https://docs.plone.org/develop/addons/components/genericsetup.html#custom-installer-code-setuphandlers-py
    profile_id = "profile-{}:uninstall".format(PRODUCT_NAME)
    context = portal_setup._getImportContext(profile_id)  # noqa
    portal = context.getSite()  # noqa
    remove_client_allowed_types(portal)
    logger.info("{} uninstall handler [DONE]".format(PRODUCT_NAME.upper()))


def setup_navigation_types(portal):
    """Add additional types for navigation"""
    registry = getUtility(IRegistry)
    key = "plone.displayed_types"
    display_types = registry.get(key, ())

    new_display_types = set(display_types)
    new_display_types.update(NAVTYPES)
    registry[key] = tuple(new_display_types)


def setup_id_formatting(portal, format_definition=None):
    """Setup default ID formatting"""
    if not format_definition:
        logger.info("Setting up ID formatting ...")
        for formatting in ID_FORMATTING:
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


def setup_catalogs(portal):
    """Setup patient catalogs"""
    # setup_core_catalogs(portal, catalog_classes=CATALOGS)
    setup_other_catalogs(portal, indexes=INDEXES, columns=COLUMNS)


def add_location_to_client(portal):
    pt = api.get_tool("portal_types", context=portal)
    fti = pt.get("Client")
    # Added location listing
    actions = fti.listActions()
    action_ids = [a.id for a in actions]
    if "samplepointlocations" not in action_ids:
        fti.addAction(
            id="samplepointlocations",
            name="SamplePointLocations",
            permission="View",
            category="object",
            visible=True,
            icon_expr="string:${portal_url}/images/samplepoint.png",
            action="string:${object_url}/samplepointlocations",
            condition="",
            link_target="",
        )

    # add to allowed types
    allowed_types = fti.allowed_content_types
    if allowed_types:
        allowed_types = list(allowed_types)
        if "SamplePointLocation" not in allowed_types:
            allowed_types.append("SamplePointLocation")
            fti.allowed_content_types = allowed_types
            logger.info("Add SamplePointLocation from Client's allowed types")


def remove_client_sample_types_action(portal):
    pt = api.get_tool("portal_types", context=portal)
    fti = pt.get("Client")

    # removed location listing
    actions = fti.listActions()
    for idx, action in enumerate(actions):
        if action.id == "samplepoints":
            fti.deleteActions(
                [
                    idx,
                ]
            )
            break


def remove_client_allowed_types(portal):
    pt = api.get_tool("portal_types", context=portal)
    fti = pt.get("Client")

    # removed location listing
    actions = fti.listActions()
    for idx, action in enumerate(actions):
        if action.id == "samplepointlocations":
            fti.deleteActions(
                [
                    idx,
                ]
            )
            break

    # Remove location from allowed types
    allowed_types = fti.allowed_content_types
    if allowed_types:
        allowed_types = list(allowed_types)
        if "SamplePointLocation" in allowed_types:
            allowed_types.remove("SamplePointLocation")
            logger.info("Remove SamplePointLocation from Client's allowed types")
            fti.allowed_content_types = allowed_types


@implementer(INonInstallable)
class HiddenProfiles(object):
    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            "senaite.samplepointlocations:uninstall",
        ]

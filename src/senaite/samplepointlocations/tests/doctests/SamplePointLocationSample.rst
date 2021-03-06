Location Sample
----------------

Running this test from the buildout directory:

    bin/test test_textual_doctests -t SamplePointLocationSample

Test Setup
..........

Needed Imports:

    >>> from AccessControl.PermissionRole import rolesForPermissionOn
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from bika.lims.utils.analysisrequest import create_partition
    >>> from bika.lims.workflow import doActionFor as do_action_for
    >>> from bika.lims.workflow import isTransitionAllowed
    >>> from bika.lims.workflow import getAllowedTransitions
    >>> from DateTime import DateTime
    >>> from plone.app.testing import setRoles
    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import TEST_USER_PASSWORD
    >>> from senaite import api
    >>> from senaite.core.catalog import SAMPLE_CATALOG
    >>> from senaite.core.catalog import SETUP_CATALOG
    >>> from plone import api as plone_api

Functional Helpers:

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> def start_server():
    ...     from Testing.ZopeTestCase.utils import startZServer
    ...     ip, port = startZServer()
    ...     return "http://{}:{}/{}".format(ip, port, portal.id)

    >>> def new_sample_point(location, **kw):
    ...     values = {'SamplePointLocation': api.get_uid(location)}
    ...     values.update(kw)
    ...     samplepoint = api.create(location, "SamplePoint", title='SP1', **values)
    ...     return samplepoint

    >>> def new_sample(services, client, contact, sample_type, location, date_sampled=None, **kw):
    ...     values = {
    ...         'Client': api.get_uid(client),
    ...         'Contact': api.get_uid(contact),
    ...         'SamplePointLocation': api.get_uid(location),
    ...         'DateSampled': date_sampled or DateTime().strftime("%Y-%m-%d"),
    ...         'SampleType': api.get_uid(sample_type)}
    ...     values.update(kw)
    ...     service_uids = map(api.get_uid, services)
    ...     sample = create_analysisrequest(client, request, values, service_uids)
    ...     return sample

    >>> def get_roles_for_permission(permission, context):
    ...     allowed = set(rolesForPermissionOn(permission, context))
    ...     return sorted(allowed)

Variables:

    >>> portal = self.portal
    >>> request = self.request
    >>> setup = api.get_setup()

We need to create some basic objects for the test:

    >>> setRoles(portal, TEST_USER_ID, ['LabManager',])
    >>> client = api.create(portal.clients, "Client", Name="Client One", ClientID="C1", MemberDiscountApplies=False)
    >>> contact = api.create(client, "Contact", Firstname="Rita", Lastname="Mohale")
    >>> sampletype = api.create(setup.bika_sampletypes, "SampleType", title="Blood", Prefix="B")
    >>> labcontact = api.create(setup.bika_labcontacts, "LabContact", Firstname="Lab", Lastname="Manager")
    >>> department = api.create(setup.bika_departments, "Department", title="Clinical Lab", Manager=labcontact)
    >>> category = api.create(setup.bika_analysiscategories, "AnalysisCategory", title="Blood", Department=department)
    >>> MC = api.create(setup.bika_analysisservices, "AnalysisService", title="Malaria Count", Keyword="MC", Price="10", Category=category.UID(), Accredited=True)
    >>> MS = api.create(setup.bika_analysisservices, "AnalysisService", title="Malaria Species", Keyword="MS", Price="10", Category=category.UID(), Accredited=True)


SamplePointLocation Sample Integration
..........................
Create a new location:

    >>> sp_loc_title = 'SamplePointLocation One'
    >>> sp_loc1 = api.create(client, 'SamplePointLocation', title=sp_loc_title, description='Desc')
    >>> sp_loc1.title == sp_loc_title
    True

Test location workflow
    >>> api.get_workflows_for(sp_loc1)
    ('senaite_deactivable_type_workflow',)

    >>> api.get_workflow_status_of(sp_loc1)
    'active'

Global add permission:

    >>> from senaite.samplepointlocations.permissions import AddSamplePointLocation
    >>> get_roles_for_permission(AddSamplePointLocation, portal)
    ['Manager']

Create a new sameple point:

    >>> samplepoint1 = new_sample_point(sp_loc1)
    >>> samplepoint1.getSamplePointLocation().title == sp_loc_title
    True

Create a new sample:

    >>> sample = new_sample([MC, MS], client, contact, sampletype, location=sp_loc1)
    >>> api.get_workflow_status_of(sample)
    'sample_due'
    >>> sample.getSamplePointLocation().title == sp_loc_title
    True
    >>> # import pdb; pdb.set_trace()  # fmt: skip

Find sample by location:
    >>> setup_cat = plone_api.portal.get_tool(name=SETUP_CATALOG)
    >>> len(setup_cat(portal_type='SamplePointLocation'))
    1
    >>> sample_cat = plone_api.portal.get_tool(name=SAMPLE_CATALOG)
    >>> len(sample_cat(portal_type='AnalysisRequest'))
    1
    >>> len(sample_cat(portal_type='AnalysisRequest', getSamplePointLocation='DDDDD'))
    0
    >>> len(sample_cat(portal_type='AnalysisRequest', getSamplePointLocation=sp_loc_title))
    1
    >>> len(sample_cat(portal_type='AnalysisRequest', getSamplePointLocationUID=sp_loc1.UID()))
    1

# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s senaite.locations -t test_location.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src senaite.locations.testing.SENAITE_LOCATIONS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/senaite/locations/tests/robot/test_location.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Location
  Given a logged-in site administrator
    and an add Client form
   When I type 'My Location' into the title field
    and I submit the form
   Then a Location with the title 'My Location' has been created

Scenario: As a site administrator I can view a Location
  Given a logged-in site administrator
    and a Location 'My Location'
   When I go to the Location view
   Then I can see the Location title 'My Location'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Client form
  Go To  ${PLONE_URL}/++add++Client

a Location 'My Location'
  Create content  type=Client  id=my-location  title=My Location

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Location view
  Go To  ${PLONE_URL}/my-location
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Location with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Location title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}

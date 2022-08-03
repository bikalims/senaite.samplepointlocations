from senaite.samplepointlocations import check_installed


@check_installed(None)
def getSamplePointLocation(self):  # noqa camelcase
    """Returns the sample point's location"""
    return self.getField("SamplePointLocation").get(self)


@check_installed(None)
def setSamplePointLocation(self, value):  # noqa camelcase
    """Sets the sample point's location"""
    return self.getField("SamplePointLocation").set(self, value)

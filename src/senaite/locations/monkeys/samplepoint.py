from senaite.locations import check_installed


@check_installed(None)
def getSamplePointLocation(self):  # noqa camelcase
    """Returns the sample point's location"""
    return self.getField("SamplePointLocation").get(self)

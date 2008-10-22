from pycucumber import Given, When, Then


@Given("I can't fail")
def cant_fail():
    pass

@When("I try")
def try():
    pass

@Then("I succeed")
def succeed():
    pass

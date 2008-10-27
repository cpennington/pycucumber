from pycucumber import Given, When, Then

@Given("pass")
@When("pass")
@Then("pass")
def succeed():
    pass

@Given("fail")
@When("fail")
@Then("fail")
def fail():
    assert False

@Given("skip")
@When("skip")
@Then("skip")
def skip():
    assert False

@Given("ambig.*")
@When("ambig.*")
@Then("ambig.*")
def ambig():
    assert False

@Given(".*uous")
@When(".*uous")
@Then(".*uous")
def uous():
    assert False

from pycucumber import Given, When, Then

@Given("pass")
@When("pass")
@Then("pass")
def succeed():
    print "succeeding"
    pass

@Given("fail")
@When("fail")
@Then("fail")
def fail():
    print "failing"
    assert False

@Given("skip")
@When("skip")
@Then("skip")
def skip():
    print "should be skipped"
    assert False

@Given("ambig.*")
@When("ambig.*")
@Then("ambig.*")
def ambig():
    print "should be ambiguous"
    assert False

@Given("ambiguous")
@When("ambiguous")
@Then("ambiguous")
def uous():
    print "should be ambiguous"
    assert False

@Given("var:(.+)")
@When("var:(.+)")
@Then("var:(.+)")
def variable(name):
    print "name is "+name
    assert name == 'pass'

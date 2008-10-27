from __future__ import with_statement
import os

from pycucumber import Given, When, Then, Test, display_results
from ast_visitors import Succeeded, Failed, Unimplemented, Ambiguous, Skipped, Visitor
import sys

class ResultCounter(Visitor):
    def __init__(self, result_type):
        self.count = 0
        self.result_type = result_type

    def visitFeature(self, feature):
        for child in feature.children():
            child.accept(self)
        return self.count

    def visitCondition(self, cond):
        if type(cond.result) == self.result_type:
            self.count += 1

    def visitAction(self, act):
        if type(act.result) == self.result_type:
            self.count += 1

    def visitResult(self, res):
        if type(res.result) == self.result_type:
            self.count += 1

class PyCucumberTest(object):
    def set_feature(self, file):
        self.feature = file

    def set_rules(self, file):
        self.rules = file

    def run_test(self):
        execfile(self.rules)
        with open(self.feature) as feature:
            self.results = Test("".join(feature.readlines()))
    
    def did_test_pass(self):
        return self.results.result.is_success()

    def count_results(self, result_type):
        return ResultCounter(result_type).visitFeature(self.results)


cuke_test = PyCucumberTest()

@Given("a feature file (\S+)")
def feature_file(file):
    assert os.path.isfile(file), "Feature file %s doesn't exist" % file
    global cuke_test
    cuke_test.set_feature(file)


@Given("a rules file (\S+)")
def rules_file(file):
    assert os.path.isfile(file), "Rules file %s doesn't exist" % file
    global cuke_test
    cuke_test.set_rules(file)

@When("I run them")
def run_test():
    global cuke_test
    cuke_test.run_test()

@Then(r"the feature should (pass|fail)")
def check_result(result):
    global cuke_test
    assert (result == 'pass') == cuke_test.did_test_pass(), "Test unexpectedly %sed" % result

@Then(r"(\d+) test(?:s)? should (.+)")
def check_result(num_tests, condition):
    cases = {'pass': Succeeded,
             'fail': Failed,
             'be unimplemented': Unimplemented,
             'be ambiguous': Ambiguous,
             'be skipped': Skipped}
    global cuke_test
    count = cuke_test.count_results(cases[condition])
    num_tests = int(num_tests)
    assert num_tests == count, "%d expected, %d found" % (num_tests, count)
    

if __name__ == "__main__":
    with open(sys.argv[1]) as file:
        display_results(Test("".join(file.readlines())))

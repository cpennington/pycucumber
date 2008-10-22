from __future__ import with_statement

from pycucumber import Given, When, Then, Test
import sys
                

class PyCucumberTest(object):
    def set_feature(self, file):
        self.feature = file

    def set_rules(self, file):
        self.rules = file

    def run_test(self, file):
        self.results = file
    

@Given("a feature file (\S+)")
def feature_file(file):
    return file

@Given("a rules file (\S+)")
def rules_file(file):
    return file

@When("I run them")
def run_test():
    return file


if __name__ == "__main__":
    with open(sys.argv[1]) as file:
        Test("".join(file.readlines()))

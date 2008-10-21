from __future__ import with_statement

from pycucumber import Given, When, Then, Test
import sys

num_list = []
@Given(r"I have entered (?P<num>\d+) into the calculator")
def enter(num):
    global num_list
    num_list.append(int(num))

result = 0
@When(r"I press add")
def add():
    global num_list, result
    result = sum(num_list)
 
@Then(r"the result should be (?P<num>\d+) on the screen")
def check(num):
    global result
    assert int(num) == result, str(result) + " is not " + num

if __name__ == "__main__":
    with open(sys.argv[1]) as file:
        Test("".join(file.readlines()))

from __future__ import with_statement
import re
from ast_nodes import Purpose, Role, Goal, Condition, Action, Result, Scenario, Feature, parse
from ast_visitors import PrettyPrinter, TestRunner

_givens = []
_whens = []
_thens = []

def create_collector(bag):
    def collector(regex):
        def decorate(fn):
            bag.append((re.compile(regex), fn))
            return fn
        return decorate
    return collector

Given = create_collector(_givens)
When = create_collector(_whens)
Then = create_collector(_thens)

def Test(text):
    #print("Input:\n" + text)

    feature = parse(text)

    #print("AST:\n" + PrettyPrinter().visitFeature(feature))
    TestRunner(_givens, _whens, _thens).visitFeature(feature)
    return feature

def display_results(feature):
    print PrettyPrinter().visitFeature(feature).encode('utf-8')

def display_implemented_commands():
    for (regex, fn) in _givens + _whens + _thens:
        print fn.__doc__

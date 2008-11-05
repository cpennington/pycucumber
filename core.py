from __future__ import with_statement
import re
from ast_nodes import Purpose, Role, Goal, Condition, Action, Result, Scenario, Feature, parse
from ast_visitors import PrettyPrinter, TestRunner
from regex_parser import parse_regex, SimplifyPrinter, TreePrinter
import inspect

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

def display_commands_in_bag(bag, name):
    for (regex, fn) in bag:
        tree = parse_regex(regex.pattern)
        print "%s %s" % (name, tree.accept(SimplifyPrinter(["<%s>" % arg for arg in inspect.getargspec(fn)[0]])))

def display_implemented_commands():
    for bag, name in [(_givens, "Given"), (_whens, "When"), (_thens, "Then")]:
        display_commands_in_bag(bag, name)

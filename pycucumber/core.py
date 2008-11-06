from __future__ import with_statement
import re
from ast_nodes import Purpose, Role, Goal, Condition, Action, Result, Scenario, Feature, parse
from ast_visitors import PrettyPrinter, TestRunner, CheckRules
from regex_parser import parse_regex, SimplifyPrinter, TreePrinter
import inspect

_givens = []
_whens = []
_thens = []

def create_collector(bag):
    def collector(regex, names=[]):
        def decorate(fn):
            bag.append((re.compile(regex), fn, names))
            return fn
        return decorate
    return collector

Given = create_collector(_givens)
When = create_collector(_whens)
Then = create_collector(_thens)

def Test(text):
    feature = parse(unicode(text, 'utf-8'))
    feature.accept(TestRunner(_givens, _whens, _thens))
    return feature

def CheckSyntax(text):
    feature = parse(unicode(text, 'utf-8'))
    feature.accept(CheckRules(_givens, _whens, _thens))
    return feature

def display_results(feature):
    print feature.accept(PrettyPrinter())

def override(*iterables):
    iterables = map(iter, iterables)
    while iterables:
        results = []
        to_remove = []
        for it in iterables:
            try:
                res = it.next()
                results.append(res)
            except StopIteration:
                to_remove.append(it)
        for it in to_remove:
            iterables.remove(it)
        try:
            yield results[0]
        except IndexError:
            raise StopIteration


def display_commands_in_bag(bag, name):
    for (regex, fn, names) in bag:
        tree = parse_regex(regex.pattern)
        inspected_names = inspect.getargspec(fn)[0]
        real_names = list(override(names, inspected_names))
        command = "%s %s" % (name, tree.accept(SimplifyPrinter(["<%s>" % arg for arg in real_names])))
        description = fn.__doc__ if fn.__doc__ else "No description"
        print "%s: %s" % (command, description)

def display_implemented_commands():
    for bag, name in [(_givens, "Given"), (_whens, "When"), (_thens, "Then")]:
        display_commands_in_bag(bag, name)

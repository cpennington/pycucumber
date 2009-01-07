from __future__ import with_statement
import re
from ast_nodes import Purpose, Role, Goal, Condition, Action, Result, Scenario, Feature, parse
from ast_visitors import TestRunner, CheckRules, Skipped, Succeeded, Failed
from regex_parser import parse_regex, SimplifyPrinter, TreePrinter
import inspect
import readline
import sys

_givens = []
_whens = []
_thens = []

def create_collector(bag):
    def collector(regex, names=[]):
        def decorate(fn):
            # We append a \Z to the supplied regular expression to force it to match
            # the entire line
            bag.append((re.compile(r"%s\Z" % regex), fn, names))
            return fn
        return decorate
    return collector

Given = create_collector(_givens)
When = create_collector(_whens)
Then = create_collector(_thens)

def Test(text, output_stream=sys.stdout, interactive=False):
    return run_visitor(text, TestRunner(_givens, _whens, _thens), output_stream, interactive)

def CheckSyntax(text, output_stream=sys.stdout):
    return run_visitor(text, CheckRules(_givens, _whens, _thens), output_stream, False)

def run_visitor(text, visitor, output_stream, interactive):
    feature = parse(unicode(text, 'utf-8'))
    feature_gen = feature.accept(visitor)
    event = feature_gen.next()
    try:
        while True:
            if callable(event):
                if interactive:
                    result = interact(event)
                else:
                    result = event()
            else:
                result = None
                print >> output_stream, event,
                output_stream.flush()
            event = feature_gen.send(result)
    except StopIteration:
        pass
    return feature

previous_selection = 'r'
def get_choice():
    return raw_input("\n-- (R)un, (S)kip, (P)ass, or (F)ail [%s]: " % previous_selection).lower()

options = {
    's': Skipped(''),
    'p': Succeeded(''),
    'f': Failed('','Failed By User'),
    }
def interact(pending_event):
    global previous_selection
    result = None
    while result is None:
        input = get_choice()
        if input == '':
            input = previous_selection
        else:
            input = input[0]
            previous_selection = input
        try:
            result = options[input]
        except KeyError:
            if input == 'r':
                result = pending_event()
    return result

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
        command = "%s %s" % (name, tree.accept(SimplifyPrinter(["<%s>" % arg if arg is not None else None for arg in real_names])))
        description = fn.__doc__ if fn.__doc__ else "No description"
        print "%s: %s" % (command, description)

def display_implemented_commands():
    for bag, name in [(_givens, "Given"), (_whens, "When"), (_thens, "Then")]:
        display_commands_in_bag(bag, name)

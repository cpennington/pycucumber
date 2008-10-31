from __future__ import with_statement
import re
import pprint
from optparse import OptionParser
import sys
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


# TODO: use inspect module to find arity
# TODO: implement More Cases
# TODO: implement But
# TODO: implement alternating actions and results

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

def file_list_callback(option, opt_str, value, parser):
    assert value is None
    done = 0
    value = []
    rargs = parser.rargs
    while rargs:
        arg = rargs[0]

        # Stop if we hit an arg like "--foo", "-a", "-fx", "--file=f",
        # etc.  Note that this also stops on "-3" or "-3.0", so if
        # your option takes numeric values, you will need to handle
        # this.
        if ((arg[:2] == "--" and len(arg) > 2) or
            (arg[:1] == "-" and len(arg) > 1 and arg[1] != "-")):
            break
        else:
            value.append(arg)
            del rargs[0]
    
        setattr(parser.values, option.dest, value)

def add_parse_options(parser):
    parser.add_option("-r", "--rules", action="callback", callback=file_list_callback, dest="rules")
    parser.add_option("-f", "--features", action="callback", callback=file_list_callback, dest="features")
    parser.add_option("-l", "--list", action="store_const", const="list", dest="command")
    

def load_rules(rules):
    for rule in rules:
        execfile(rule)

def main():
    parser = OptionParser()
    add_parse_options(parser)
    (options, args) = parser.parse_args()
    load_rules(options.rules)
    if options.command == "list":
        display_implemented_commands()
    else:
        for feature_file in options.features:
            with open(feature_file) as file:
                display_results(Test(u"".join(file.readlines())))

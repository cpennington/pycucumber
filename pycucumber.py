import re
import pprint
import traceback
from pyparsing import ZeroOrMore, LineStart, Optional, Suppress
from pyparsing import Group, Keyword, ParserElement, Combine, Word, printables
from pyparsing import LineEnd, White, alphanums, CharsNotIn


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

def named_line(starts_with, name = None):
    ParserElement.setDefaultWhitespaceChars(" \t")
    
    line = Suppress(Keyword(starts_with)) + Combine(ZeroOrMore(CharsNotIn(" \t\r\n") + Optional(White(" \t")))) + Optional(Suppress(LineEnd() + ZeroOrMore(LineStart() + LineEnd())))
    if (name):
        line = line.setResultsName(name)
    return line

def grammar():
    purpose = named_line("In order", "Purpose")
    role = named_line("As", "Role")
    goal = named_line("To", "Goal")
    header = Optional(purpose) + Optional(role) + Optional(goal)

    repeats = named_line("And")

    conditions = Group(named_line("Given") + ZeroOrMore(repeats)).setResultsName("Givens")
    actions = Group(named_line("When") + ZeroOrMore(repeats)).setResultsName("Whens")
    results = Group(named_line("Then") + ZeroOrMore(repeats)).setResultsName("Thens")

    scenario = named_line("Scenario:", "Scenario") + conditions + actions + results

    feature = named_line("Feature:", "Feature") + header + scenario
        
    return feature

def get_matches(bag, line):
    matches = []
    for (regex, fn) in bag:
        match = regex.match(line)
        if (match):
            matches.append((fn, match.groups()))
    return matches

class Unimplemented(object):
    def __init__(self, line):
        self.line = line
    def get_results(self, failed):
        return self
    def is_success(self):
        return False
    def __str__(self):
        return "Unimplemented: " + self.line

class Ambiguous(object):
    def __init__(self, line, matches):
        self.line = line
        self.matches = matches
    def get_results(self, failed):
        return self
    def is_success(self):
        return False
    def __str__(self):
        return "Ambiguous: " + self.line

class Failed(object):
    def __init__(self, line, reason):
        self.line = line
        self.reason = reason
    def is_success(self):
        return False
    def __str__(self):
        return "Failed: " + self.line + "\n" + self.reason

class Succeeded(object):
    def __init__(self, line):
        self.line = line
    def is_success(self):
        return True
    def __str__(self):
        return "Succeeded: " + self.line

class Skipped(object):
    def __init__(self, line):
        self.line = line
    def is_success(self):
        return False
    def __str__(self):
        return "Skipped: " + self.line

class Executable(object):
    def __init__(self, line, fn, args):
        self.line = line
        self.fn = fn
        self.args = args
    def get_results(self, failed):
        if failed:
            return Skipped(self.line)
        try:
            self.fn(*self.args)
        except Exception, e:
            return Failed(self.line, traceback.format_exc(e))
        return Succeeded(self.line)

def add_tests(lines, bag, list):
    for line in lines:
        matches = get_matches(bag, line)
        if (len(matches) == 0):
            list.append(Unimplemented(line))
            continue
        if (len(matches) > 1):
            list.append(Ambiguous(line, matches))
            continue
        (fn, args) = matches[0]
        list.append(Executable(line, fn, args))

# TODO: use inspect module to find arity
# TODO: implement More Cases
# TODO: implement But
# TODO: implement alternating actions and results

def Test(text):
    print(text)
    feature = grammar().parseString(text)
    
    tests = {
        'conds': [],
        'actions': [],
        'results': [],
        }
    add_tests(feature['Givens'], _givens, tests['conds'])
    add_tests(feature['Whens'], _whens, tests['actions'])
    add_tests(feature['Thens'], _thens, tests['results'])

    conditions_failed = False
    results = []
    for test in tests["conds"]:
        result = test.get_results(conditions_failed)
        conditions_failed = conditions_failed or not result.is_success()
        results.append(result)

    actions_failed = conditions_failed
    for test in tests["actions"]:
        result = test.get_results(actions_failed)
        actions_failed = actions_failed or not result.is_success()
        results.append(result)

    for test in tests["results"]:
        result = test.get_results(actions_failed)
        results.append(result)

    return results

def display_results(results):
    for result in results:
        print result

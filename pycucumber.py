import re
import pprint
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
    return(TestRunner(_givens, _whens, _thens).visitFeature(feature))

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
    for scenario in results:
        for test in scenario:
            print test

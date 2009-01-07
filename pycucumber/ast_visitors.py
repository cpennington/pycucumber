from __future__ import with_statement

import traceback
import copy
import contextlib

class Visitor(object):
    def __init__(self):
        pass

    def visitFeature(self, feature):
        for child in feature.children():
            for event in child.accept(self):
                yield event

    def visitScenario(self, scenario):
        for child in scenario.children():
            for event in child.accept(self):
                yield event

    def visitStep(self, step):
        for child in step.children():
            for event in child.accept(self):
                yield event

    def visitMoreExamples(self, examples):
        for child in examples.children():
            for event in child.accept(self):
                yield event

    def visitExampleRow(self, example):
        pass

    def visitPurpose(self, purpose):
        pass

    def visitGoal(self, goal):
        pass

    def visitRole(self, role):
        pass

    def visitCondition(self, cond):
        pass

    def visitAction(self, act):
        pass

    def visitResult(self, res):
        pass


feature_managers = []
def RegisterFeatureContextManager(manager):
    feature_managers.append(manager())

scenario_managers = []
def RegisterScenarioContextManager(manager):
    scenario_managers.append(manager())

def get_matches(bag, line):
    matches = []
    for (regex, fn, name) in bag:
        match = regex.match(line)
        if (match):
            matches.append((fn, match.groups()))
    return matches

def check_test(bag, line):
    matches = get_matches(bag, line)
    if (len(matches) == 0):
        return Unimplemented(line)
    if (len(matches) > 1):
        return Ambiguous(matches, line)
    (fn, args) = matches[0]
    return WellFormed(fn, args)

def run_test(bag, line, arg_queue = None):
    syntax_check = check_test(bag, line)
    if not syntax_check.is_success():
        return syntax_check
    if arg_queue:
        args = [arg_queue.pop(0) for arg in syntax_check.args]
    else:
        args = syntax_check.args
    try:
        syntax_check.fn(*args)
    except Exception, e:
        return Failed("%s" % traceback.format_exc(e), line)
    return Succeeded(line)

class Unimplemented(object):
    def __init__(self, line):
        self.line = line
    def is_success(self):
        return False
    def __str__(self):
        return self.__unicode__().encode('ascii', 'backslashreplace')
    def __unicode__(self):
        return u"Unimplemented"

class Ambiguous(object):
    def __init__(self, matches, line):
        self.matches = matches
        self.line = line
    def is_success(self):
        return False
    def __str__(self):
        return self.__unicode__().encode('ascii', 'backslashreplace')
    def __unicode__(self):
        return u"Ambiguous"

class WellFormed(object):
    def __init__(self, fn, args):
        self.fn = fn
        self.args = args
    def is_success(self):
        return True
    def __str__(self):
        return self.__unicode__().encode('ascii', 'backslashreplace')
    def __unicode__(self):
        return u"Well Formed"

class WrongNumArgs(object):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
    def __str__(self):
        return self.__unicode__().encode('ascii', 'backslashreplace')
    def __unicode__(self):
        return u"Wrong Number of Arguments: %d expected, %d listed" % (self.expected, self.actual)

class Failed(object):
    def __init__(self, reason, line):
        self.reason = reason
        self.line = line
    def is_success(self):
        return False
    def __str__(self):
        return self.__unicode__().encode('ascii', 'backslashreplace')
    def __unicode__(self):
        return u"Failed: " + self.reason

class Succeeded(object):
    def __init__(self, line):
        self.line = line
    def is_success(self):
        return True
    def __str__(self):
        return self.__unicode__().encode('ascii', 'backslashreplace')
    def __unicode__(self):
        return u"Succeeded"

class Skipped(object):
    def __init__(self, line):
        self.line = line
    def is_success(self):
        return False
    def __str__(self):
        return self.__unicode__().encode('ascii', 'backslashreplace')
    def __unicode__(self):
        return u"Skipped"

def format_feature(feature):
    return u"Feature: %s\n" % feature.text

def format_purpose(purpose):
    return u"In order %s\n" % purpose.text

def format_goal(goal):
    return u"I want %s\n" % goal.text

def format_role(role):
    return u"As %s\n" % role.text

def format_scenario(scenario):
    return u"Scenario: %s\n" % scenario.text

def format_test_result(result):
    return u"(%s)\n" % result if result else "Not Yet Run"

def format_test(test, prefix, is_first, indent_str):
    return u"%s %s" % (prefix if is_first else indent_str + "And",
                       test.text)

def format_action(action, is_first, indent_str):
    return format_test(action, "When", is_first, indent_str)

def format_condition(cond, is_first, indent_str):
    return format_test(cond, "Given", is_first, indent_str)

def format_result(result, is_first, indent_str):
    return format_test(result, "Then", is_first, indent_str)

def format_row(row_data):
    return "|%s|" % "|".join(row_data), example.result

def format_more_examples(examples):
    return 'More Examples:\n'

class IndentManager:
    def __init__(self):
        self.indent = 0
        self.indent_str = "  "

    def __enter__(self):
        self.indent += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.indent -= 1

    def indented_line(self, line):
        return u"%s%s" % (self.indent_str*self.indent, line)

class TestRunner(Visitor):
    def __init__(self, conditions, actions, results, output_file = None):
        self.cond_funcs = conditions
        self.act_funcs = actions
        self.res_funcs = results
        self.output_file = output_file
        self.indenter = IndentManager()

    def visitPurpose(self, purpose, arg_queue=None):
        yield self.indenter.indented_line(format_purpose(purpose))

    def visitGoal(self, goal, arg_queue=None):
        yield self.indenter.indented_line(format_goal(goal))

    def visitRole(self, role, arg_queue=None):
        yield self.indenter.indented_line(format_role(role))

    def visitChildren(self, node, arg_queue=None):
        with self.indenter:
            for child in node.children():
                gen = child.accept(self, arg_queue)
                result = None
                try:
                    while True:
                        result = yield gen.send(result)
                except StopIteration:
                    pass

    def visitFeature(self, feature):
        yield self.indenter.indented_line(format_feature(feature))
        with contextlib.nested(*(feature_managers + [self.indenter])):
            gen = self.visitChildren(feature)
            result = None
            while True:
                result = yield gen.send(result)

    def visitScenario(self, scenario, arg_queue=None):
        self.execute_next_condition = True
        self.execute_next_action = True
        self.execute_next_result = True
        self.current_scenario = scenario

        yield self.indenter.indented_line(format_scenario(scenario))
        self.first_cond = True

        with contextlib.nested(*(scenario_managers + [self.indenter])):
            gen = self.visitChildren(scenario, arg_queue)
            result = None
            while True:
                result = yield gen.send(result)

    def visitStep(self, step, arg_queue=None):
        self.first_action = True
        self.first_result = True
        gen = self.visitChildren(step, arg_queue)
        result = None
        while True:
            result = yield gen.send(result)

    def visitCondition(self, cond, arg_queue=None):
        yield self.indenter.indented_line(
            format_condition(cond, self.first_cond, self.indenter.indent_str))
        cond.result = yield lambda: run_test(self.cond_funcs, cond.text, arg_queue) if self.execute_next_condition else Skipped(cond.text)
        if not cond.result.is_success():
            self.execute_next_condition = False
            self.execute_next_action = False
            self.execute_next_result = False

        yield format_test_result(cond.result)
        self.first_cond = False

    def visitAction(self, act, arg_queue=None):
        yield self.indenter.indented_line(
            format_action(act, self.first_action, self.indenter.indent_str))

        act.result = yield lambda: run_test(self.act_funcs, act.text, arg_queue) if self.execute_next_action else Skipped(act.text)
        if not act.result.is_success():
            self.execute_next_action = False
            self.execute_next_result = False

        yield format_test_result(act.result)
        self.first_action = False

    def visitResult(self, res, arg_queue=None):
        yield self.indenter.indented_line(
            format_result(res, self.first_result, self.indenter.indent_str))

        res.result = yield lambda: run_test(self.res_funcs, res.text, arg_queue) if self.execute_next_result else Skipped(res.text)
        if not res.result.is_success():
            self.execute_next_action = False

        yield format_test_result(res.result)
        self.first_result = False

    def visitMoreExamples(self, examples, arg_queue=None):
        yield self.indenter.indented_line(format_more_examples(examples))
        with self.indenter:
            gen = self.visitChildren(examples, arg_queue)
            result = None
            while True:
                result = yield gen.send(result)

    def visitExampleRow(self, example, arg_queue):
        yield self.indenter.indented_line(format_row(example))

        example.scenario = copy.deepcopy(self.current_scenario)
        example.scenario.more_examples = None
        gen = self.visitScenario(example.scenario, copy.deepcopy(example.data))
        result = None
        while True:
            result = yield gen.send(result)

        example.result = example.scenario.result

        yield self.indenter.indented_line(format_result(example.result))


class CheckRules(Visitor):
    def __init__(self, conditions, actions, results):
        self.cond_funcs = conditions
        self.act_funcs = actions
        self.res_funcs = results
        self.args_accurate = True
        self.indenter = IndentManager()

    def visitChildren(self, node, arg_queue=None):
        with self.indenter:
            for child in node.children():
                gen = child.accept(self, arg_queue)
                result = None
                try:
                    while True:
                        result = yield gen.send(result)
                except StopIteration:
                    pass

    def visitPurpose(self, purpose, arg_queue=None):
        yield self.indenter.indented_line(format_purpose(purpose))

    def visitGoal(self, goal, arg_queue=None):
        yield self.indenter.indented_line(format_goal(goal))

    def visitRole(self, role, arg_queue=None):
        yield self.indenter.indented_line(format_role(role))

    def visitFeature(self, feature):
        yield self.indenter.indented_line(format_feature(feature))
        with self.indenter:
            gen = self.visitChildren(feature)
            result = None
            while True:
                result = yield gen.send(result)

    def visitScenario(self, scenario, arg_queue=None):
        self.args_required = 0

        yield self.indenter.indented_line(format_scenario(scenario))

        self.first_cond = True
        with self.indenter:
            gen = self.visitChildren(scenario, arg_queue)
            result = None
            while True:
                result = yield gen.send(result)

    def visitStep(self, step, arg_queue=None):
        self.first_action = True
        self.first_result = True
        gen = self.visitChildren(step, arg_queue)
        result = None
        while True:
            result = yield gen.send(result)

    def visitCondition(self, cond, arg_queue=None):
        yield self.indenter.indented_line(
            format_condition(cond, self.first_cond, self.indenter.indent_str))
        cond.result = check_test(self.cond_funcs, cond.text)
        if self.args_accurate and cond.result.is_success():
            self.args_required += len(cond.result.args)
        else:
            self.args_accurate = False

        self.first_cond = False
        yield format_test_result(cond.result)

    def visitAction(self, act, arg_queue=None):
        yield self.indenter.indented_line(
            format_action(act, self.first_action, self.indenter.indent_str))

        act.result = check_test(self.act_funcs, act.text)
        if self.args_accurate and act.result.is_success():
            self.args_required += len(act.result.args)
        else:
            self.args_accurate = False

        self.first_action = False
        yield format_test_result(act.result)

    def visitResult(self, res, arg_queue=None):
        yield self.indenter.indented_line(
            format_result(res, self.first_result, self.indenter.indent_str))

        res.result = check_test(self.res_funcs, res.text)
        if self.args_accurate and res.result.is_success():
            self.args_required += len(res.result.args)
        else:
            self.args_accurate = False

        self.first_result = False
        yield format_test_result(res.result)

    def visitMoreExamples(self, examples, arg_queue=None):
        yield self.indenter.indented_line(format_more_examples(examples))
        with self.indenter:
            gen = self.visitChildren(examples, arg_queue)
            result = None
            while True:
                result = yield gen.send(result)

    def visitExampleRow(self, example, arg_queue):
        yield self.indenter.indented_line(format_row(example))
        if not self.args_accurate:
            example.result = Skipped(None)
        elif self.args_required != len(example.data):
            example.result = WrongNumArgs(self.args_required, len(example.data))
        else:
            example.result = WellFormed(None, None)

        yield self.indenter.indented_line(format_result(example.result))

class YieldResults(Visitor):

    def yield_result(self, node):
        yield node.result

    visitExampleRow = yield_result
    visitCondition = yield_result
    visitAction = yield_result
    visitResult = yield_result

from __future__ import with_statement

import traceback
import copy
import contextlib

class Visitor(object):
    def __init__(self):
        pass

    def visitFeature(self, feature):
        for child in feature.children():
            child.accept(self)

    def visitScenario(self, scenario):
        for child in scenario.children():
            child.accept(self)

    def visitStep(self, step):
        for child in step.children():
            child.accept(self)
        pass

    def visitMoreExamples(self, examples):
        for child in examples.children():
            child.accept(self)
        pass

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
    return u"Feature: %s" % feature.text

def format_purpose(purpose):
    return u"In order %s" % purpose.text

def format_goal(goal):
    return u"I want %s" % goal.text

def format_role(role):
    return u"As %s" % role.text

def format_scenario(scenario):
    return u"Scenario: %s" % scenario.text

def format_test_result(result):
    return u"(%s)" % result if result else "Not Yet Run"

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
        line = self.indenter.indented_line(format_purpose(purpose))
        if self.output_file:
            print >> self.output_file, line
            self.output_file.flush()
        return [line], Succeeded(unicode(purpose))

    def visitGoal(self, goal, arg_queue=None):
        line = self.indenter.indented_line(format_goal(goal))
        if self.output_file:
            print >> self.output_file, line
            self.output_file.flush()
        return [line], Succeeded(unicode(goal))

    def visitRole(self, role, arg_queue=None):
        line = self.indenter.indented_line(format_role(role))
        if self.output_file:
            print >> self.output_file, line
            self.output_file.flush()
        return [line], Succeeded(unicode(role))

    def visitChildren(self, node, arg_queue=None):
        first_failure = None
        child_lines = []
        with self.indenter:
            for child in node.children():
                line, result = child.accept(self, arg_queue)
                child_lines.append(line)
                if not result.is_success() and not first_failure:
                    first_failure = result

        if not first_failure:
            return child_lines, Succeeded(unicode(node))
        else:
            return child_lines, Failed("Child test %s" % first_failure, first_failure.line)

    def visitFeature(self, feature):
        line = self.indenter.indented_line(format_feature(feature))
        if self.output_file:
            print >> self.output_file, line
            self.output_file.flush()

        with contextlib.nested(*(feature_managers + [self.indenter])):
            child_lines, feature.result = self.visitChildren(feature)

        return [line] + child_lines, feature.result

    def visitScenario(self, scenario, arg_queue=None):
        self.execute_next_condition = True
        self.execute_next_action = True
        self.execute_next_result = True
        self.current_scenario = scenario

        line = self.indenter.indented_line(format_scenario(scenario))
        if self.output_file:
            print >> self.output_file, line
            self.output_file.flush()

        self.first_cond = True

        with contextlib.nested(*(scenario_managers + [self.indenter])):
            child_lines, scenario.result = self.visitChildren(scenario, arg_queue)
        return [line] + child_lines, scenario.result

    def visitStep(self, step, arg_queue=None):
        self.first_action = True
        self.first_result = True
        child_lines, step.result = self.visitChildren(step, arg_queue)
        return child_lines, step.result

    def visitCondition(self, cond, arg_queue=None):
        start = self.indenter.indented_line(
            format_condition(cond, self.first_cond, self.indenter.indent_str))
        if self.output_file:
            print >> self.output_file, start,
            self.output_file.flush()

        cond.result = run_test(self.cond_funcs, cond.text, arg_queue) if self.execute_next_condition else Skipped(cond.text)
        if not cond.result.is_success():
            self.execute_next_condition = False
            self.execute_next_action = False
            self.execute_next_result = False

        result = format_test_result(cond.result)
        if self.output_file:
            print >> self.output_file, result
            self.output_file.flush()

        self.first_cond = False
        return [start + result], cond.result

    def visitAction(self, act, arg_queue=None):
        start = self.indenter.indented_line(
            format_action(act, self.first_action, self.indenter.indent_str))
        if self.output_file:
            print >> self.output_file, start,
            self.output_file.flush()

        act.result = run_test(self.act_funcs, act.text, arg_queue) if self.execute_next_action else Skipped(act.text)
        if not act.result.is_success():
            self.execute_next_action = False
            self.execute_next_result = False

        result = format_test_result(act.result)
        if self.output_file:
            print >> self.output_file, result
            self.output_file.flush()

        self.first_action = False
        return [start + result], act.result

    def visitResult(self, res, arg_queue=None):
        start = self.indenter.indented_line(
            format_result(res, self.first_result, self.indenter.indent_str))
        if self.output_file:
            print >> self.output_file, start,
            self.output_file.flush()

        res.result = run_test(self.res_funcs, res.text, arg_queue) if self.execute_next_result else Skipped(res.text)
        if not res.result.is_success():
            self.execute_next_action = False

        result = format_test_result(res.result)
        if self.output_file:
            print >> self.output_file, result
            self.output_file.flush()

        self.first_result = False
        return [start + result], res.result

    def visitMoreExamples(self, examples, arg_queue=None):
        with self.indenter:
            child_lines, examples.result = self.visitChildren(examples, arg_queue)
        return ['MoreExamples:'] + child_lines, examples.result

    def visitExampleRow(self, example, arg_queue):
        row = self.indenter.indented_line(format_row(example))
        if self.output_file:
            print >> self.output_file, row,
            self.output_file.flush()

        example.scenario = copy.deepcopy(self.current_scenario)
        example.scenario.more_examples = None
        self.visitScenario(example.scenario, copy.deepcopy(example.data))
        example.result = example.scenario.result

        result = self.indenter.indented_line(format_result(example.result))
        if self.output_file:
            print >> self.output_file, result
            self.output_file.flush()

        return [row + result], example.result


class CheckRules(Visitor):
    def __init__(self, conditions, actions, results):
        self.cond_funcs = conditions
        self.act_funcs = actions
        self.res_funcs = results
        self.args_accurate = True

    def visitCondition(self, cond):
        cond.result = check_test(self.cond_funcs, cond.text)
        if self.args_accurate and cond.result.is_success():
            self.args_required += len(cond.result.args)
        else:
            self.args_accurate = False

    def visitAction(self, act):
        act.result = check_test(self.act_funcs, act.text)
        if self.args_accurate and act.result.is_success():
            self.args_required += len(act.result.args)
        else:
            self.args_accurate = False

    def visitResult(self, res):
        res.result = check_test(self.res_funcs, res.text)
        if self.args_accurate and res.result.is_success():
            self.args_required += len(res.result.args)
        else:
            self.args_accurate = False

    def visitScenario(self, scenario):
        self.args_required = 0
        for child in scenario.children():
            child.accept(self)

    def visitExampleRow(self, example):
        if not self.args_accurate:
            example.result = Skipped(None)
        elif self.args_required != len(example.data):
            example.result = WrongNumArgs(self.args_required, len(example.data))
        else:
            example.result = WellFormed(None, None)

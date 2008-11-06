import traceback
import copy

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


class PrettyPrinter(Visitor):
    def __init__(self):
        self.indent = 0
        self.indent_str = "  "

    def current_indent(self):
        return self.indent_str*self.indent
        

    def visitFeature(self, feature):
        ret = u"%sFeature: %s\n" % (self.current_indent(), feature.text)
        self.indent += 1
        for child in feature.children():
            ret += child.accept(self)
        self.indent -= 1
        return ret

    def visitPurpose(self, purpose):
        return u"%sIn order %s\n" % (self.current_indent(), purpose.text)

    def visitGoal(self, goal):
        return u"%sI want %s\n" % (self.current_indent(), goal.text)

    def visitRole(self, role):
        return "%sAs %s\n" % (self.current_indent(), role.text)

    def visitScenario(self, scenario):
        ret = u"\n%sScenario: %s\n" % (self.current_indent(), scenario.text)
        self.indent += 1

        self.first_cond = True
        for child in scenario.children():
            ret += child.accept(self)
        self.indent -= 1
        return ret

    def format_test(self, test, prefix):
        return u"%s%s %s (%s)\n" % (self.current_indent(),
                                   prefix,
                                   test.text,
                                   test.result if test.result else "Not Yet Run")

    def visitCondition(self, cond):
        ret = self.format_test(cond, "Given" if self.first_cond else self.indent_str + "And")
        self.first_cond = False
        return ret

    def visitStep(self, step):
        ret = ""

        self.first_act = True
        self.first_res = True

        for child in step.children():
            ret += child.accept(self)
        return ret

    def visitAction(self, act):
        ret = self.format_test(act, "When" if self.first_act else self.indent_str + "And")
        self.first_act = False
        return ret

    def visitResult(self, res):
        ret = self.format_test(res, "Then" if self.first_res else self.indent_str + "And")
        self.first_res = False
        return ret

    def format_row(self, row_data):
        return "%s|%s|" % (self.current_indent(), "|".join(row_data))

    def visitMoreExamples(self, examples):
        ret = u"\n%sMore Examples:\n" % self.current_indent()
        
        self.indent += 1
        ret += self.format_row(examples.header) + "\n"
        for child in examples.children():
            ret += child.accept(self)
        self.indent -= 1
        return ret

    def visitExampleRow(self, example):
        return "%s (%s)\n" % (self.format_row(example.data), example.result if example.result else "Not Yet Run")


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

def run_test(bag, line, failed, arg_queue = None):
    syntax_check = check_test(bag, line)
    if not syntax_check.is_success():
        return syntax_check
    if arg_queue:
        args = [arg_queue.pop(0) for arg in syntax_check.args]
    else:
        args = syntax_check.args
    if failed:
        return Skipped(line)
    try:
        syntax_check.fn(*args)
    except Exception, e:
        return Failed("%s\nMessage: %s" % (traceback.format_exc(e), e.message), line)
    return Succeeded(line)

class Unimplemented(object):
    def __init__(self, line):
        self.line = line
    def is_success(self):
        return False
    def __str__(self):
        return "Unimplemented"

class Ambiguous(object):
    def __init__(self, matches, line):
        self.matches = matches
        self.line = line
    def is_success(self):
        return False
    def __str__(self):
        return "Ambiguous"

class WellFormed(object):
    def __init__(self, fn, args):
        self.fn = fn
        self.args = args
    def is_success(self):
        return True
    def __str__(self):
        return "Well Formed"

class WrongNumArgs(object):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
    def __str__(self):
        return "Wrong Number of Arguments: %d expected, %d listed" % (self.expected, self.actual)

class Failed(object):
    def __init__(self, reason, line):
        self.reason = reason
        self.line = line
    def is_success(self):
        return False
    def __str__(self):
        return "Failed: " + self.reason

class Succeeded(object):
    def __init__(self, line):
        self.line = line
    def is_success(self):
        return True
    def __str__(self):
        return "Succeeded"
       
class Skipped(object):
    def __init__(self, line):
        self.line = line
    def is_success(self):
        return False
    def __str__(self):
        return "Skipped"

class TestRunner(Visitor):
    def __init__(self, conditions, actions, results):
        self.cond_funcs = conditions
        self.act_funcs = actions
        self.res_funcs = results
        self.conditions_failed = False
        self.actions_failed = False

    def visitPurpose(self, purpose, arg_queue=None):
        return Succeeded(str(purpose))

    def visitGoal(self, goal, arg_queue=None):
        return Succeeded(str(goal))

    def visitRole(self, role, arg_queue=None):
        return Succeeded(str(role))

    def visitChildren(self, node, arg_queue=None):
        first_failure = None
        for child in node.children():
            result = child.accept(self, arg_queue)
            if not result.is_success() and not first_failure:
                first_failure = result
                
        if not first_failure:
            return Succeeded(str(node))
        else:
            return Failed("Child test %s" % first_failure, first_failure.line)
        

    def visitFeature(self, feature):
        feature.result = self.visitChildren(feature)
        return feature.result

    def visitScenario(self, scenario, arg_queue=None):
        self.conditions_failed = False
        self.actions_failed = False
        self.current_scenario = scenario
        scenario.result = self.visitChildren(scenario, arg_queue)
        return scenario.result

    def visitStep(self, step, arg_queue=None):
        step.result = self.visitChildren(step, arg_queue)
        return step.result

    def visitCondition(self, cond, arg_queue=None):
        cond.result = run_test(self.cond_funcs, cond.text, self.conditions_failed, arg_queue)
        self.actions_failed = self.conditions_failed = self.conditions_failed or not cond.result.is_success()
        return cond.result
    
    def visitAction(self, act, arg_queue=None):
        act.result = run_test(self.act_funcs, act.text, self.actions_failed, arg_queue)
        self.actions_failed = self.actions_failed or not act.result.is_success()
        return act.result

    def visitResult(self, res, arg_queue=None):
        res.result = run_test(self.res_funcs, res.text, self.actions_failed, arg_queue)
        return res.result

    def visitMoreExamples(self, examples, arg_queue=None):
        examples.result = self.visitChildren(examples, arg_queue)
        return examples.result

    def visitExampleRow(self, example, arg_queue):
        example.scenario = copy.deepcopy(self.current_scenario)
        example.scenario.more_examples = None
        self.visitScenario(example.scenario, copy.deepcopy(example.data))
        example.result = example.scenario.result
        return example.result
        

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
        

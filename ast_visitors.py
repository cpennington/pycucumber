import traceback

class Visitor(object):
    def __init__(self):
        pass

    def visitFeature(self, feature):
        for child in feature.children():
            child.accept(self)

    def visitScenario(self, scenario):
        self.conditions_failed = False
        for child in scenario.children():
            child.accept(self)

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

    def visitStep(self, res):
        pass


class PrettyPrinter(Visitor):
    def __init__(self):
        self.indent = 0
        self.indent_str = "  "

    def visitFeature(self, feature):
        ret = u"%sFeature: %s\n" % (self.indent_str*self.indent, feature.text)
        self.indent += 1
        for child in feature.children():
            ret += child.accept(self)
        self.indent -= 1
        return ret

    def visitPurpose(self, purpose):
        return u"%sIn order %s\n" % (self.indent_str*self.indent, purpose.text)

    def visitGoal(self, goal):
        return u"%sI want %s\n" % (self.indent_str*self.indent, goal.text)

    def visitRole(self, role):
        return "%sAs %s\n" % (self.indent_str*self.indent, role.text)

    def visitScenario(self, scenario):
        ret = u"%sScenario: %s\n" % (self.indent_str*self.indent, scenario.text)
        self.indent += 1

        self.first_cond = True
        for child in scenario.children():
            ret += child.accept(self)
        self.indent -= 1
        return ret

    def format_test(self, test, prefix):
        return u"%s%s %s (%s)\n" % (self.indent_str*self.indent,
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


def get_matches(bag, line):
    matches = []
    for (regex, fn) in bag:
        match = regex.match(line)
        if (match):
            matches.append((fn, match.groups()))
    return matches

def run_test(bag, line, failed):
    matches = get_matches(bag, line)
    if (len(matches) == 0):
        return Unimplemented()
    if (len(matches) > 1):
        return Ambiguous(matches)
    (fn, args) = matches[0]
    if failed:
        return Skipped()
    try:
        fn(*args)
    except Exception, e:
        return Failed("%s\nMessage: %s" % (traceback.format_exc(e), e.message))
    return Succeeded()

class Unimplemented(object):
    def is_success(self):
        return False
    def __str__(self):
        return "Unimplemented"

class Ambiguous(object):
    def __init__(self, matches):
        self.matches = matches
    def is_success(self):
        return False
    def __str__(self):
        return "Ambiguous"

class Failed(object):
    def __init__(self, reason):
        self.reason = reason
    def is_success(self):
        return False
    def __str__(self):
        return "Failed: " + self.reason

class Succeeded(object):
    def is_success(self):
        return True
    def __str__(self):
        return "Succeeded"
       
class Skipped(object):
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

    def visitPurpose(self, purpose):
        return Succeeded()

    def visitGoal(self, goal):
        return Succeeded()

    def visitRole(self, role):
        return Succeeded()

    def visitFeature(self, feature):
        all_passed = all([child.accept(self).is_success() for child in feature.children()])
        if all_passed:
            feature.result = Succeeded()
        else:
            feature.result = Failed(None)
        return feature.result

    def visitScenario(self, scenario):

        self.conditions_failed = False
        all_passed = all([child.accept(self).is_success() for child in scenario.children()])
        if all_passed:
            scenario.result = Succeeded()
        else:
            scenario.result = Failed(None)
        return scenario.result

    def visitStep(self, step):
        all_passed = all([child.accept(self).is_success() for child in step.children()])
        if all_passed:
            step.result = Succeeded()
        else:
            step.result = Failed(None)
        return step.result

    def visitCondition(self, cond):
        cond.result = run_test(self.cond_funcs, cond.text, self.conditions_failed)
        self.actions_failed = self.conditions_failed = self.conditions_failed or not cond.result.is_success()
        return cond.result
    
    def visitAction(self, act):
        act.result = run_test(self.act_funcs, act.text, self.actions_failed)
        self.actions_failed = self.actions_failed or not act.result.is_success()
        return act.result

    def visitResult(self, res):
        res.result = run_test(self.res_funcs, res.text, self.actions_failed)
        return res.result


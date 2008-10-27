import traceback

class Visitor(object):
    def __init__(self):
        pass

    def visitFeature(self, feature):
        pass

    def visitPurpose(self, purpose):
        pass

    def visitGoal(self, goal):
        pass

    def visitRole(self, role):
        pass

    def visitScenario(self, scenario):
        pass

    def visitCondition(self, cond):
        pass

    def visitAction(self, act):
        pass

    def visitResult(self, res):
        pass

class PreOrderTraversal(Visitor):
    def __init__(self, visitor):
        self.visitor = visitor

    def visitFeature(self, feature):
        ret = "%sFeature: %s\n" % (self.indent_str*self.indent, feature.text)
        self.indent += 1
        if feature.purpose:
            ret += feature.purpose.accept(self)
        if feature.role:
            ret += feature.role.accept(self)
        if feature.goal:
            ret += feature.goal.accept(self)
        for scenario in feature.scenarios:
            ret += scenario.accept(self)
        self.indent -= 1
        return ret

    def visitPurpose(self, purpose):
        return "%sIn order %s\n" % (self.indent_str*self.indent, purpose.text)

    def visitGoal(self, goal):
        return "%sTo %s\n" % (self.indent_str*self.indent, goal.text)

    def visitRole(self, role):
        return "%sAs %s\n" % (self.indent_str*self.indent, role.text)

    def visitScenario(self, scenario):
        ret = "%sScenario: %s\n" % (self.indent_str*self.indent, scenario.text)
        self.indent += 1

        self.first_cond = True
        for cond in scenario.conditions:
            ret += cond.accept(self)
            self.first_cond = False

        self.first_act = True
        for act in scenario.actions:
            ret += act.accept(self)
            self.first_act = False

        self.first_res = True
        for res in scenario.results:
            ret += res.accept(self)
            self.first_res = False

        self.indent -= 1
        return ret

    def format_test(self, test, prefix):
        return "%s%s %s\n (%s)" % (self.indent_str*self.indent,
                                   prefix,
                                   test.text,
                                   test.result if test.result else "Not Yet Run")

    def visitCondition(self, cond):
        return self.format_test(cond, "Given" if self.first_cond else "And")

    def visitAction(self, act):
        return self.format_test(act, "When" if self.first_act else "And")

    def visitResult(self, res):
        return self.format_test(res, "Then" if self.first_res else "And")


class PrettyPrinter(Visitor):
    def __init__(self):
        self.indent = 0
        self.indent_str = "  "

    def visitFeature(self, feature):
        ret = "%sFeature: %s\n" % (self.indent_str*self.indent, feature.text)
        self.indent += 1
        if feature.purpose:
            ret += feature.purpose.accept(self)
        if feature.role:
            ret += feature.role.accept(self)
        if feature.goal:
            ret += feature.goal.accept(self)
        for scenario in feature.scenarios:
            ret += scenario.accept(self)
        self.indent -= 1
        return ret

    def visitPurpose(self, purpose):
        return "%sIn order %s\n" % (self.indent_str*self.indent, purpose.text)

    def visitGoal(self, goal):
        return "%sTo %s\n" % (self.indent_str*self.indent, goal.text)

    def visitRole(self, role):
        return "%sAs %s\n" % (self.indent_str*self.indent, role.text)

    def visitScenario(self, scenario):
        ret = "%sScenario: %s\n" % (self.indent_str*self.indent, scenario.text)
        self.indent += 1

        self.first_cond = True
        for cond in scenario.conditions:
            ret += cond.accept(self)
            self.first_cond = False

        self.first_act = True
        for act in scenario.actions:
            ret += act.accept(self)
            self.first_act = False

        self.first_res = True
        for res in scenario.results:
            ret += res.accept(self)
            self.first_res = False

        self.indent -= 1
        return ret

    def format_test(self, test, prefix):
        return "%s%s %s\n (%s)" % (self.indent_str*self.indent,
                                   prefix,
                                   test.text,
                                   test.result if test.result else "Not Yet Run")

    def visitCondition(self, cond):
        return self.format_test(cond, "Given" if self.first_cond else "And")

    def visitAction(self, act):
        return self.format_test(act, "When" if self.first_act else "And")

    def visitResult(self, res):
        return self.format_test(res, "Then" if self.first_res else "And")


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
        return Unimplemented(line)
    if (len(matches) > 1):
        return Ambiguous(line, matches)
    (fn, args) = matches[0]
    if failed:
        return Skipped(line)
    try:
        fn(*args)
    except Exception, e:
        return Failed(line, traceback.format_exc(e))
    return Succeeded(line)

class Unimplemented(object):
    def __init__(self, line):
        self.line = line
    def is_success(self):
        return False
    def __str__(self):
        return "Unimplemented: " + self.line

class Ambiguous(object):
    def __init__(self, line, matches):
        self.line = line
        self.matches = matches
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

class TestRunner(Visitor):
    def __init__(self, conditions, actions, results):
        self.cond_funcs = conditions
        self.act_funcs = actions
        self.res_funcs = results

    def visitFeature(self, feature):
        for scenario in feature.scenarios:
            scenario.accept(self)

    def visitScenario(self, scenario):
        self.conditions_failed = False
        for cond in scenario.conditions:
            cond.accept(self)

        self.actions_failed = self.conditions_failed
        for action in scenario.actions:
            action.accept(self)

        for result in scenario.results:
            result.accept(self) 


    def visitCondition(self, cond):
        cond.result = run_test(self.cond_funcs, cond.text, self.conditions_failed)
        self.conditions_failed = self.conditions_failed or not cond.result.is_success()

    def visitAction(self, act):
        act.result = run_test(self.act_funcs, act.text, self.actions_failed)
        self.actions_failed = self.actions_failed or not act.result.is_success()

    def visitResult(self, res):
        res.result = run_test(self.res_funcs, res.text, self.actions_failed)

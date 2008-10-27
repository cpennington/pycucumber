
from pyparsing import ZeroOrMore, OneOrMore, LineStart, Optional, Suppress
from pyparsing import Group, Keyword, ParserElement, Combine, Word, printables
from pyparsing import LineEnd, White, alphanums, CharsNotIn

def create(type):
    return lambda t: [type(t)]

def prefixed_line(starts_with):
    ParserElement.setDefaultWhitespaceChars(" \t")
    
    line = (Suppress(Keyword(starts_with)) +
            Combine(ZeroOrMore(CharsNotIn(" \t\r\n") + Optional(White(" \t")))).setResultsName("text") +
            Optional(Suppress(LineEnd() + ZeroOrMore(LineStart() + LineEnd()))))

    return line

def named_type(type, expression, name = None):
    ret = expression.setResultsName(name) if name else expression
    ret = ret.setParseAction(create(type))
    return ret

def repeat(type):
    return named_type(type, prefixed_line("And"))

def grammar():
    purpose = named_type(Purpose, prefixed_line("In order"), "purpose")
    role = named_type(Role, prefixed_line("As"), "role")
    goal = named_type(Goal, prefixed_line("To"), "goal")
    header = Optional(purpose) + Optional(role) + Optional(goal)

    conditions = Group(named_type(Condition, prefixed_line("Given"))
                       + ZeroOrMore(repeat(Condition))).setResultsName("conditions")
    actions = Group(named_type(Action, prefixed_line("When"))
                    + ZeroOrMore(repeat(Action))).setResultsName("actions")
    results = Group(named_type(Result, prefixed_line("Then"))
                    + ZeroOrMore(repeat(Result))).setResultsName("results")

    scenario = named_type(Scenario, prefixed_line("Scenario:") + conditions + actions + results)

    feature = named_type(Feature, prefixed_line("Feature:") + header + 
                         OneOrMore(scenario).setResultsName("scenarios"), "feature")

    return feature

def parse(text):
    return grammar().parseString(text)["feature"][0]

class TestNode(object):
    def children(self):
        return []

class Purpose(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
    def accept(self, visitor):
        return visitor.visitPurpose(self)


class Role(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
    def accept(self, visitor):
        return visitor.visitRole(self)


class Goal(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
    def accept(self, visitor):
        return visitor.visitGoal(self)


class Condition(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
        self.result = None
    def accept(self, visitor):
        return visitor.visitCondition(self)
    

class Action(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
        self.result = None
    def accept(self, visitor):
        return visitor.visitAction(self)


class Result(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
        self.result = None
    def accept(self, visitor):
        return visitor.visitResult(self)


class Feature(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
        self.purpose = tokens["purpose"][0] if "purpose" in tokens else None
        self.role = tokens["role"][0] if "role" in tokens else None
        self.goal = tokens["goal"][0] if "goal" in tokens else None
        self.scenarios = tokens["scenarios"]
        self.result = None

    def accept(self, visitor):
        return visitor.visitFeature(self)
    
    def children(self):
        children = []
        if self.purpose:
            children.append(self.purpose)
        if self.role:
            children.append(self.role)
        if self.goal:
            children.append(self.goal)
        children.extend(self.scenarios)
        return children


class Scenario(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
        self.conditions = tokens["conditions"]
        self.actions = tokens["actions"]
        self.results = tokens["results"]
        self.result = None
    def accept(self, visitor):
        return visitor.visitScenario(self)

    def children(self):
        children = []
        children.extend(self.conditions)
        children.extend(self.actions)
        children.extend(self.results)
        return children

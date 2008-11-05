
from pyparsing import ZeroOrMore, OneOrMore, LineStart, Optional, Suppress
from pyparsing import Group, Keyword, ParserElement, Combine, Word, printables
from pyparsing import LineEnd, White, alphanums, CharsNotIn, delimitedList, Regex
from pyparsing import Or, Empty, restOfLine, StringStart, StringEnd, replaceWith, SkipTo,traceParseAction, Literal

def create(type):
    return lambda t: [type(t)]

ParserElement.setDefaultWhitespaceChars(" \t\r")

EOL = LineEnd().suppress()
empty_line = (LineStart() + Optional(White(" \t\r")) + EOL).setParseAction(replaceWith("<EMPTYLINE>")).leaveWhitespace()
comment = (Suppress("#") + SkipTo(EOL) + EOL).setParseAction(replaceWith("<COMMENT>"))
example_row = Suppress("|") + ZeroOrMore(SkipTo("|" | EOL).setParseAction(lambda t: [t[0].strip()]) + Suppress("|")) + EOL

def prefixed_line(starts_with):
    line = (Suppress(Keyword(starts_with)) +
            SkipTo(EOL).setParseAction(lambda t: [t[0].strip()]).setResultsName("text") + EOL)

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
    goal = named_type(Goal, prefixed_line("I want"), "goal")
    header = Optional(role) + Optional(goal) + Optional(purpose)

    conditions = Group(named_type(Condition, prefixed_line("Given"))
                       + ZeroOrMore(repeat(Condition))).setResultsName("conditions")
    actions = Group(named_type(Action, prefixed_line("When"))
                    + ZeroOrMore(repeat(Action))).setResultsName("actions")
    results = Group(named_type(Result, prefixed_line("Then"))
                    + ZeroOrMore(repeat(Result))).setResultsName("results")

    steps = Group(OneOrMore(named_type(Step, actions + results))).setResultsName("steps")

    more_examples = named_type(MoreExamples,
                               prefixed_line("More Examples:")
                               + example_row.setResultsName("header")
                               + OneOrMore(named_type(ExampleRow, example_row)).setResultsName("rows"),
                               "more_examples")
    
    scenario = named_type(Scenario, prefixed_line("Scenario:") + Optional(conditions) + steps + Optional(more_examples))

    feature = named_type(Feature, prefixed_line("Feature:") + header + 
                         OneOrMore(scenario).setResultsName("scenarios"), "feature")

    feature.ignore(empty_line)
    feature.ignore(comment)
    return feature

def parse(text):
    return grammar().parseString(text, True)["feature"][0]

class TestNode(object):
    def children(self):
        return []

class Purpose(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitPurpose(self, *args, **kwargs)


class Role(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitRole(self, *args, **kwargs)


class Goal(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitGoal(self, *args, **kwargs)


class Condition(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
        self.result = None
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitCondition(self, *args, **kwargs)
    

class Action(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
        self.result = None
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitAction(self, *args, **kwargs)


class Result(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
        self.result = None
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitResult(self, *args, **kwargs)


class Step(TestNode):
    def __init__(self, tokens):
        self.actions = tokens["actions"].asList()
        self.results = tokens["results"].asList()
        self.result = None
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitStep(self, *args, **kwargs)
    def children(self):
        return self.actions + self.results


class Feature(TestNode):
    def __init__(self, tokens):
        self.text = tokens["text"]
        self.purpose = tokens["purpose"][0] if "purpose" in tokens else None
        self.role = tokens["role"][0] if "role" in tokens else None
        self.goal = tokens["goal"][0] if "goal" in tokens else None
        self.scenarios = tokens["scenarios"].asList()
        self.result = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFeature(self, *args, **kwargs)
    
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
        self.conditions = tokens["conditions"].asList() if "conditions" in tokens else []
        self.steps = tokens["steps"].asList()
        self.more_examples = tokens["more_examples"][0] if "more_examples" in tokens else None
        self.result = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitScenario(self, *args, **kwargs)

    def children(self):
        children = []
        children.extend(self.conditions)
        children.extend(self.steps)
        if self.more_examples:
            children.append(self.more_examples)
        return children

class MoreExamples(TestNode):
    def __init__(self, tokens):
        self.header = tokens["header"].asList()
        self.rows = tokens["rows"].asList()
        self.result = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitMoreExamples(self, *args, **kwargs)

    def children(self):
        return self.rows


class ExampleRow(TestNode):
    def __init__(self, tokens):
        self.data = tokens.asList()
        self.result = None
        self.scenario = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitExampleRow(self, *args, **kwargs)

    def children(self):
        return []

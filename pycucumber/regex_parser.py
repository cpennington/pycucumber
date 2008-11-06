from pyparsing import (Literal, Combine, oneOf, printables, SkipTo, Word,
                       nums, operatorPrecedence, opAssoc, ParserElement, Forward,
                       Optional, Suppress)
import unittest
import string

def handleRange():
    pass

def handleLiteral():
    pass
def handleMacro():
    pass
def handleDot():
    pass
def handleRepetition():
    pass
def handleSequence(t):
    print t
def handleAlternative():
    pass

def create(type):
    return lambda t: [type(t)]

class Group(object):
    def __init__(self, tokens):
        types = {":": "non-matching", "P": "named"}
        self.type = types[tokens["option"][0]] if "option" in tokens else "standard"
        self.name = tokens["name"] if "name" in tokens else None
        self.expr = tokens["expr"]
    def __repr__(self):
        return "Group([%r])" % self.expr
    def __str__(self):
        return "(%s)" % self.expr
    def accept(self, visitor):
        return visitor.visitGroup(self)
    def children(self):
        return [self.expr]

class Repetition(object):
    def __init__(self, tokens):
        self.term = tokens[0][0]
        self.operator = tokens[0][1]
    def __repr__(self):
        return "Repetition([%r, %r])" % (self.term, self.operator)
    def __str__(self):
        return "%s%s" % (self.term, self.operator)
    def accept(self, visitor):
        return visitor.visitRepetition(self)
    def children(self):
        return [self.term]

class Sequence(object):
    def __init__(self, tokens):
        self.items = tokens[0].asList()
    def __repr__(self):
        return "Sequence([%r])" % self.items
    def __str__(self):
        return "".join((str(item) for item in self.items))
    def accept(self, visitor):
        return visitor.visitSequence(self)
    def children(self):
        return self.items

class Character(object):
    def __init__(self, tokens):
        self.char = tokens[0]
    def __repr__(self):
        return "Character([%r])" % self.char
    def __str__(self):
        return self.char
    def accept(self, visitor):
        return visitor.visitCharacter(self)
    def children(self):
        return []

class Dot(object):
    def __init__(self, tokens):
        pass
    def __repr__(self):
        return "Dot()"
    def __str__(self):
        return "."
    def accept(self, visitor):
        return visitor.visitDot(self)
    def children(self):
        return []

class Macro(object):
    def __init__(self, tokens):
        self.type = tokens[0]
    def __repr__(self):
        return "Macro(%s)" % self.type
    def __str__(self):
        return "\\%s" % self.type
    def accept(self, visitor):
        return visitor.visitMacro(self)
    def children(self):
        return []

class Range(object):
    def __init__(self, tokens):
        self.contents = tokens[0]
    def __repr__(self):
        return "Range(%s)" % self.contents
    def __str__(self):
        return "[%s]" % self.contents
    def accept(self, visitor):
        return visitor.visitRange(self)
    def children(self):
        return []

class Alternation(object):
    def __init__(self, tokens):
        self.options = tokens[0].asList()
    def __repr__(self):
        return "Alternation(%r)" % self.options
    def __str__(self):
        return "|".join((str(option) for option in self.options))
    def accept(self, visitor):
        return visitor.visitAlternation(self)
    def children(self):
        return []

class SimplifyPrinter(object):
    def __init__(self, group_labels=None):
        self.group_labels = group_labels

    def visitSequence(self, node):
        return "".join([child.accept(self) for child in node.children()])

    def visitGroup(self, node):
        if not node.type == "non-matching" and self.group_labels and len(self.group_labels):
            return self.group_labels.pop(0)
        elif node.type == "non-matching":
            return "".join([child.accept(self) for child in node.children()])
        else:
            return "".join(["("] + [child.accept(self) for child in node.children()] + [")"])
    
    def visitRepetition(self, node):
        if node.operator == "?":
            return "[%s]" % node.term.accept(self)
        else:
            return "%s%s" % (node.term.accept(self), node.operator)
    
    def visitCharacter(self, node):
        return node.char

    def visitDot(self, node):
        return str(node)
    
    def visitMacro(self, node):
        return str(node)

    def visitRange(self, node):
        return str(node)

    def visitAlternation(self, node):
        return "[%s]" % " | ".join([option.accept(self) for option in node.options])

class TreePrinter(object):
    def __init__(self, indent="  "):
        self.indent = indent
        self.indent_count = 0

    def visitNode(self, node):
        ret = self.indent*self.indent_count + str(node.__class__.__name__) + "\n"
        self.indent_count += 1
        for child in node.children():
            ret += child.accept(self)
        self.indent_count -= 1
        return ret

    def visitSequence(self, node):
        return self.visitNode(node)

    def visitGroup(self, node):
        return self.visitNode(node)
    
    def visitRepetition(self, node):
        return self.visitNode(node)
    
    def visitCharacter(self, node):
        return self.visitNode(node)

    def visitDot(self, node):
        return self.visitNode(node)

    def visitMacro(self, node):
        return self.visitNode(node)

    def visitRange(self, node):
        return self.visitNode(node)
    
    def visitAlternation(self, node):
        return self.visitNode(node)

_parser = None
def parser():
    global _parser
    if _parser is None:
        ParserElement.setDefaultWhitespaceChars("")
        
        lbrack = Literal("[")
        rbrack = Literal("]")
        lbrace = Literal("{")
        rbrace = Literal("}")
        lparen = Literal("(")
        rparen = Literal(")")
        
        reMacro = Suppress("\\") + oneOf(list("dws"))
        escapedChar = ~reMacro + Combine("\\" + oneOf(list(printables)))
        reLiteralChar = "".join(c for c in string.printable if c not in r"\[]{}().*?+|")

        reRange = Combine(lbrack.suppress() + SkipTo(rbrack,ignore=escapedChar) + rbrack.suppress())
        reLiteral = ( escapedChar | oneOf(list(reLiteralChar)) )
        reDot = Literal(".")
        repetition = (
            ( lbrace + Word(nums).setResultsName("count") + rbrace ) |
            ( lbrace + Word(nums).setResultsName("minCount")+","+ Word(nums).setResultsName("maxCount") + rbrace ) |
            oneOf(list("*+?"))
            )
        reExpr = Forward()
        reGroup = (lparen.suppress() +
                   Optional(Literal("?").suppress() + oneOf(list(":P"))).setResultsName("option") +
                   reExpr.setResultsName("expr") +
                   rparen.suppress())

        reTerm = ( reLiteral | reRange | reMacro | reDot | reGroup )
        reExpr << operatorPrecedence( reTerm,
            [
            (repetition, 1, opAssoc.LEFT, create(Repetition)),
            (None, 2, opAssoc.LEFT, create(Sequence)),
            (Suppress('|'), 2, opAssoc.LEFT, create(Alternation)),
            ]
            )

        reGroup.setParseAction(create(Group))
        reRange.setParseAction(create(Range))
        reLiteral.setParseAction(create(Character))
        reMacro.setParseAction(create(Macro))
        reDot.setParseAction(create(Dot))
        
        _parser = reExpr
        
    return _parser

def parse_regex(regex_str):
    return parser().parseString(regex_str, True)[0]

class TestParsing(unittest.TestCase):
    def test_grouping(self):
        tree = parse_regex('that I have clicked "(.*)"')
        print tree.accept(TreePrinter())
        print tree.accept(SimplifyPrinter(["<link text>"]))


if __name__ == '__main__':
    unittest.main()

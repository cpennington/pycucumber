from ast_nodes import prefixed_line, named_type, empty_line, comment, example_row
from pyparsing import ZeroOrMore, SkipTo
import unittest

class TestParsing(unittest.TestCase):
    def test_empty_line(self):
        self.assertEqual(ZeroOrMore(empty_line).parseString("\n   \n", True).asList(),
                         ['<EMPTYLINE>', '<EMPTYLINE>', '<EMPTYLINE>'])
        self.assertEqual(ZeroOrMore(empty_line).parseString(" \t  ", True).asList(),
                         ['<EMPTYLINE>'])
        self.assertEqual(ZeroOrMore(empty_line).parseString(" \t  \n", True).asList(),
                         ['<EMPTYLINE>', '<EMPTYLINE>'])
        self.assertEqual(ZeroOrMore(empty_line).parseString(" \n ", True).asList(),
                         ['<EMPTYLINE>', '<EMPTYLINE>'])
        self.assertEqual(ZeroOrMore(empty_line).parseString("\n\n", True).asList(),
                         ['<EMPTYLINE>', '<EMPTYLINE>', '<EMPTYLINE>'])
        self.assertEqual(ZeroOrMore(empty_line).parseString("    \n     \n\n\n", True).asList(),
                         ['<EMPTYLINE>', '<EMPTYLINE>', '<EMPTYLINE>', '<EMPTYLINE>', '<EMPTYLINE>'])
        self.assertEqual(ZeroOrMore(empty_line).parseString(" \n ", True).asList(),
                         ['<EMPTYLINE>', '<EMPTYLINE>'])
        self.assertEqual(ZeroOrMore(empty_line).parseString(" \n \n", True).asList(),
                         ['<EMPTYLINE>', '<EMPTYLINE>', '<EMPTYLINE>'])
        self.assertEqual(ZeroOrMore(empty_line).parseString(" \n  \n", True).asList(),
                         ['<EMPTYLINE>', '<EMPTYLINE>', '<EMPTYLINE>'])

    def test_comment(self):
        self.assertEqual(comment.parseString("#foo", True).asList(),
                         ["<COMMENT>"])
        self.assertEqual(comment.parseString("  #bar", True).asList(),
                         ["<COMMENT>"])
        self.assertEqual(comment.parseString("  #bar\n", True).asList(),
                         ["<COMMENT>"])

    def test_prefixed_line(self):

        parser = ZeroOrMore(comment | empty_line) + prefixed_line("Foo:") + ZeroOrMore(comment | empty_line)

        foo = prefixed_line("Foo:")
        self.assertEqual(parser.parseString("Foo: bar\n\n\n", True).asList(),
                         ["bar", "<EMPTYLINE>", "<EMPTYLINE>", "<EMPTYLINE>"])
        self.assertEqual(parser.parseString("Foo: bar    \n\n\n", True).asList(),
                         ["bar", "<EMPTYLINE>", "<EMPTYLINE>", "<EMPTYLINE>"])
        self.assertEqual(parser.parseString("Foo: bar    baz\n\n\n", True).asList(),
                         ["bar    baz", "<EMPTYLINE>", "<EMPTYLINE>", "<EMPTYLINE>"])
        self.assertEqual(parser.parseString("Foo: bar    \n      \n", True).asList(),
                         ["bar", "<EMPTYLINE>", "<EMPTYLINE>"])
        self.assertEqual(parser.parseString("Foo: bar    \n#baz\n  #spam\n", True).asList(),
                         ["bar", "<COMMENT>", "<COMMENT>", "<EMPTYLINE>"])
        
        bar = parser + prefixed_line("Bar:") + ZeroOrMore(comment | empty_line)
        self.assertEqual(bar.parseString("Foo: bar    \n#baz\nBar: baz spam\n  #spam\n", True).asList(),
                         ["bar", "<COMMENT>", "baz spam", "<COMMENT>", "<EMPTYLINE>"])
        
    def test_example_row(self):
        self.assertEqual(example_row.parseString("| a | b | c |", True).asList(),
                         ["a", "b", "c"])

    def test_skip_to(self):
        self.assertEqual(SkipTo("a").parseString("ccca").asList(), ["ccc"])
        self.assertEqual(SkipTo("a", failOn="b").parseString("ccca").asList(), ["ccc"])
        self.assertEqual(SkipTo("a", failOn="b").parseString("cbca").asList(), ["ccc"])


if __name__ == '__main__':
    unittest.main()

from ast_nodes import prefixed_line, named_type
import unittest

class TestParsing(unittest.TestCase):
    def test_prefixed_line(self):
        self.assertEqual(prefixed_line("Foo:").parseString("Foo: bar\n\n\n").asDict(),
                         {"text": "bar"})


if __name__ == '__main__':
    unittest.main()

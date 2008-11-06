from __future__ import with_statement
from optparse import OptionParser
from pycucumber import Test, display_results, display_implemented_commands

def file_list_callback(option, opt_str, value, parser):
    assert value is None
    done = 0
    value = []
    rargs = parser.rargs
    while rargs:
        arg = rargs[0]

        # Stop if we hit an arg like "--foo", "-a", "-fx", "--file=f",
        # etc.  Note that this also stops on "-3" or "-3.0", so if
        # your option takes numeric values, you will need to handle
        # this.
        if ((arg[:2] == "--" and len(arg) > 2) or
            (arg[:1] == "-" and len(arg) > 1 and arg[1] != "-")):
            break
        else:
            value.append(arg)
            del rargs[0]
    
        setattr(parser.values, option.dest, value)

def add_parse_options(parser):
    parser.add_option("-r", "--rules", action="callback", callback=file_list_callback, dest="rules")
    parser.add_option("-f", "--features", action="callback", callback=file_list_callback, dest="features")
    parser.add_option("-l", "--list", action="store_const", const="list", dest="command")
    parser.add_option("-s", "--check-syntax", action="store_const", const="check", dest="command")
    

def load_rules(rules):
    for rule in rules:
        globals = {}
        execfile(rule, globals)

def main():
    parser = OptionParser()
    add_parse_options(parser)
    (options, args) = parser.parse_args()
    load_rules(options.rules)
    if options.command == "list":
        display_implemented_commands()
        return 0
    else:
        succeeded = True
        for feature_file in options.features:
            with open(feature_file) as file:
                if options.command == "check":
                    results = CheckSyntax(file.read())
                else:
                    results = Test(file.read())
                    succeeded = succeeded and results.result.is_success()
                display_results(results)
        return not succeeded

if __name__ == "__main__":
    int(main())

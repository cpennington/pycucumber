from __future__ import with_statement

import sys
import pprint
from pycucumber import Test, display_results, display_implemented_commands, CheckSyntax
from argparse import ArgumentParser

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
        if ((arg[:2] == '--' and len(arg) > 2) or
            (arg[:1] == '-' and len(arg) > 1 and arg[1] != '-')):
            break
        else:
            value.append(arg)
            del rargs[0]
    
        setattr(parser.values, option.dest, value)

rule_args = []
callbacks = []

def load_rules(rules):
    global_dir = {}
    for rule in rules:
        execfile(rule, global_dir)

    try:
        rule_args.extend(global_dir['sys'].modules['pycucumber.runner'].rule_args)
    except KeyError:
        pass
    
    try:
        callbacks.extend(global_dir['sys'].modules['pycucumber.runner'].callbacks)
    except KeyError:
        pass
    

def AddOption(*args, **kwargs):
    """Add additional options to the commandline runner.
    Uses same syntax as ArgumentParser.add_argument"""
    rule_args.append((args, kwargs))

def RegisterConfigCallback(fn):
    """Register a function to be called with the parsed options before any actions are executed"""
    callbacks.append(fn)

def main():
    
    global rule_args

    rules = []
    args = sys.argv[1:]
    while args and args[0] not in ['list', 'run', 'check']:
        rules.append(args.pop(0))

    if not rules:
        print 'Must specify at least one rule file'
        return 1

    load_rules(rules)
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    parser_list = subparsers.add_parser('list', help='list all commands implemented in the rule files')
    parser_check = subparsers.add_parser('check', help='check the syntax of the specified feature files')
    parser_check.add_argument('feature', nargs='+')
    parser_run = subparsers.add_parser('run', help='run the specified feature files')
    parser_run.add_argument('feature', nargs='+')
    if rule_args:
        from_rules = parser_run.add_argument_group('from rules')
        for (stored_args, stored_kwargs) in rule_args:
            from_rules.add_argument(*stored_args, **stored_kwargs)

    args = parser.parse_args(args)
    if args.command == 'run':
        for fn in callbacks:
            fn(args)

    if args.command == 'list':
        display_implemented_commands()
        return 0
    else:
        succeeded = True
        for feature_file in args.feature:
            with open(feature_file) as file:
                if args.command == 'check':
                    results = CheckSyntax(file.read())
                else:
                    results = Test(file.read())
                    succeeded = succeeded and results.result.is_success()
                display_results(results)
        return not succeeded

if __name__ == '__main__':
    int(main())

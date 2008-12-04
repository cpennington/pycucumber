from __future__ import with_statement

import sys
import pprint
import os
from pycucumber import Test, display_results, display_implemented_commands, CheckSyntax, package_globals
from argparse import ArgumentParser

def load_rules(rules):
    for rule in rules:
        old_path = sys.path
        sys.path.append(os.path.abspath(os.path.dirname(rule)))
        __import__(os.path.basename(rule).replace('.py', ''))
        sys.path = old_path

#    try:
#        rule_args.extend(global_dir['sys'].modules['pycucumber.runner'].rule_args)
#    except KeyError:
#        pass
    
#    try:
#        callbacks.extend(global_dir['sys'].modules['pycucumber.runner'].callbacks)
#    except KeyError:
#        pass
    

def AddOption(*args, **kwargs):
    """Add additional options to the commandline runner.
    Uses same syntax as ArgumentParser.add_argument"""
    package_globals.rule_args.append((args, kwargs))

def RegisterConfigCallback(fn):
    """Register a function to be called with the parsed options before any actions are executed"""
    package_globals.callbacks.append(fn)

def main():
    
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
    if package_globals.rule_args:
        from_rules = parser_run.add_argument_group('from rules')
        for (stored_args, stored_kwargs) in package_globals.rule_args:
            from_rules.add_argument(*stored_args, **stored_kwargs)

    args = parser.parse_args(args)
    if args.command == 'run':
        for fn in package_globals.callbacks:
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
    exit(int(main()))

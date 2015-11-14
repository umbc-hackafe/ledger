#!/usr/bin/env python3
import sys
import datetime
import subprocess
import argparse

def main(args):
    ledger_args = {
            'ledger': args.ledger,
            'file': args.file,
            'month': args.month,
    }
    budget_output = subprocess.check_output(
            args.budget_cmd.format(**ledger_args).split()
    ).decode('utf-8')
    debt_output = {}

    for person in args.people:
        ledger_args['person'] = person
        debt_output[person] = subprocess.check_output(
            args.debt_cmd.format(**ledger_args).split()
        ).decode('utf-8')

    if args.action == 'print':
        print(budget_output)
        for person in args.people:
            print()
            print('-'*len(person))
            print(person)
            print(debt_output[person])

def parse(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['print'])
    parser.add_argument('people', nargs='+')
    parser.add_argument('--ledger', default='ledger')
    parser.add_argument('--budget-cmd',
        default='{ledger} -f {file} -p {month} budget ^Expenses')
    parser.add_argument('--debt-cmd',
        default='{ledger} -f {file} balance {person}')
    parser.add_argument('--month',
        default=datetime.datetime.now().strftime('%Y/%m'))
    parser.add_argument('--file', default='sheet.ledger')
    return parser.parse_args(args)

if __name__ == "__main__":
    sys.exit(main(parse(sys.argv[1:])))

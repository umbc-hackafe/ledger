#!/usr/bin/env python3
import sys
import datetime
import subprocess
import argparse

import textwrap

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

    report = \
"""{intro_text}
{column_information}
 - Actual purchases
 - Maximum monthly budget
 - Percent of budget expended
 - Category

{budget_report}

{owe_text}

{owe_addendum}

{owe_report}
""".format(
    intro_text = textwrap.fill("""This is the monthly Hackafé finance report. The
following table shows our expenses plotted against our budget, grouped by
category.""", width = args.width),
    column_information = textwrap.fill("""The columns from left to right
        are:""", width = args.width),
    budget_report = budget_output,
    owe_text = textwrap.fill("""The amount that you owe is shown below. It is the
sum of Hackafé's liabilities to you (amounts you have paid on our behalf that
have not been repaid by others), assets (amounts you owe as result of a purchase
on your behalf) and income (amounts you have paid to others).""",
        width = args.width),
    owe_addendum = textwrap.fill("""If the amount is negative, Hackafé owes you
money.""", width = args.width),
    owe_report = "{owe_report}")

    if args.action == 'print':
        for person in args.people:
            print('- {} {}'.format(person,
                '-' * (args.width - len(person) - 3)))
            print(report.format(owe_report = debt_output[person]))

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
    parser.add_argument('--width', type=int, default=78)
    parser.add_argument('--file', default='sheet.ledger')
    return parser.parse_args(args)

if __name__ == "__main__":
    sys.exit(main(parse(sys.argv[1:])))

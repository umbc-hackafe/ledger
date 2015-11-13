#!/usr/bin/env python3

import sys
import csv
import datetime
import argparse
from decimal import Decimal

class Transaction(object):
    def __str__(self):
        if not self.valid:
            return "<Transaction INVALID>"
        else:
            return str(vars(self))

    # Iterate over each element of the transformation, a list of tuples.
    def fill_from_row(self, row, transform):
        self.var_failures = {}
        for attribute, column, f in transform:
            # Fill f with the identity function if not given
            if not f: f = lambda x: x
            # Get the value column from the row.
            colval = row[column]
            # Catch any exception caused by external function, and record it as
            # a variable failure.
            try:
                # Calculate the value of our variable.
                val = f(colval)
            except Exception as e:
                self.var_failures[attribute] = e
                return
            setattr(self, attribute, f(row[column]))

    def ledger(self):
        return '\n'.join([
            "{date_fmt} {memo}",
            '\n'.join([
                "    {0: <40}{1}".format(*li) for li in self.lineitems
            ])
        ]).format(date_fmt = self.date.strftime('%Y-%m-%d'), **vars(self))

class Purchase(Transaction):
    _categories = {
            'R': 'Rent',
            'U': 'Utilities',
            'F': 'Food',
            'H': 'Home'
    }

    _row_transform = [
        ('date', 'Date', lambda s: datetime.datetime.strptime(s, '%Y-%m-%d')),
        ('purchaser', 'Paid By', None),
        ('purchasees', 'Purchased For', lambda s: s.split(',')),
        ('category', 'Category', lambda s: Purchase._categories[s]),
        ('amount', 'Amount', lambda s: Decimal(s.strip('$').replace(',', ''))),
        ('memo', 'Description', None),
    ]

    def __init__(self, row, allow_future=False, allow_empty=False):
        # Start by assuming it's False
        self.valid = False

        # Fill in row data
        self.fill_from_row(row, self._row_transform)

        # If any rows fail, or other constraints fail, return early with
        # self.valid set to False
        if \
               len(self.var_failures) > 0 \
            or not allow_empty and not self.purchasees \
            or not allow_future and self.date > datetime.datetime.today():
            return

        self.valid = True

        self.lineitems = [
            ("Expenses:{}".format(self.category),
                "${}".format(self.amount)),
            ("Liabilities:People:{}".format(self.purchaser),
                "$-{}".format(self.amount))
            ]
        self.lineitems.extend(
            (("(Assets:People:{})".format(purchasee),
                "(${} / {})".format(self.amount, len(self.purchasees)))
                for purchasee in self.purchasees)
        )
        return

class Payment(Transaction):
    _row_transform = [
        ('date', 'Date', lambda s: datetime.datetime.strptime(s, '%Y-%m-%d')),
        ('payer', 'From', None),
        ('payee', 'To', None),
        ('amount', 'Amount', lambda s: Decimal(s.strip('$').replace(',', ''))),
        ('memo', 'To', None),
    ]

    def __init__(self, row, allow_future=False, allow_empty=False):
        # Start by assuming it's False
        self.valid = False

        # Fill in row data
        self.fill_from_row(row, self._row_transform)

        # If any rows fail, or other constraints fail, return early with
        # self.valid set to False
        if \
               len(self.var_failures) > 0 \
            or not allow_empty and not self.purchasees \
            or not allow_future and self.date > datetime.datetime.today():
            return

        self.valid = True

        self.lineitems = [
            ("Liabilities:People:{}".format(self.payee),
                '${}'.format(self.amount)),
            ("Income:People:{}".format(self.payer),
                '${}'.format(-self.amount))
        ]
        return

def main(args):
    # Open the outfile if it's a path, or use it directly.
    out = args.output
    with open(out, 'w') if type(out) == str else out as of:
        # Print the contents of the header file.
        if args.header:
            try:
                with open(args.header, 'r') as f:
                    for line in f:
                        print(line, end='', file=of)
                print(file=of)

            except FileNotFoundError:
                print("Could not open header file, skipping: {}"
                        .format(args.header),
                        file=os.stderr)

        ts = []

        # Read the purchases file
        with open(args.purchases, 'r') as f:
            # Discard the first two lines, which are garbage.
            next(f)
            next(f)

            # Read the purchases
            ts.extend((Purchase(row) for row in csv.DictReader(f)))

        # Read the payments file
        with open(args.payments, 'r') as f:
            # Read the transactions
            ts.extend((Payment(row) for row in csv.DictReader(f)))

        # Remove invalid transactions.
        ts = filter(lambda t: t.valid, ts)

        for t in sorted(ts, key=lambda t: t.date):
            # Print the transaction and its ledger translation
            print(t.ledger(), file=of)
            print(file=of)

def parse(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--purchases", "--pu", "-p", default="purchases.csv")
    parser.add_argument("--payments", "--pay", "--pa", "-P", default="payments.csv")
    parser.add_argument("--output", "-o", default=sys.stdout)
    parser.add_argument("--header", "-H", default="header.ledger")

    return parser.parse_args(args)

if __name__ == "__main__":
    sys.exit(main(parse(sys.argv[1:])))

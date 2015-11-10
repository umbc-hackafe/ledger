#!/usr/bin/env python3

import sys
import csv
import datetime
import argparse
from decimal import Decimal

class Transaction(object):
    _categories = {
            'R': 'Rent',
            'U': 'Utilities',
            'F': 'Food',
            'H': 'Home'
    }
    def __init__(self, row, kind):
        self.valid = False

        # Ensure that the transaction has a date.
        if not row['Date']:
            return
        self.date = datetime.datetime.strptime(row['Date'], '%Y-%m-%d')

        # Discard transactions in the future
        if datetime.datetime.today() < self.date:
            return

        if kind == 'purchase':
            self.purchaser = row['Paid By']
            self.purchasees = row['Purchased For'].split(',')

            # Ensure that the list of purchasees is not corrupt.
            if len(self.purchasees) != int(row['Split Over']):
                return

            self.category = self._categories[row['Category']]

            self.memo = row['Description']
            self.amount = Decimal(row['Amount'].strip('$').replace(',', ''))

            self.lineitems = [
                    ("[Expenses:{}]".format(self.category),
                        "${}".format(self.amount)),
                    ("[Assets:Bank]", "$-{}".format(self.amount)),
                    ("Liabilities:People:{}".format(self.purchaser),
                        "$-{}".format(self.amount))
                    ]
            self.lineitems.extend(
                (("Assets:People:{}".format(purchasee),
                    "(${} / {})".format(self.amount, len(self.purchasees)))
                    for purchasee in self.purchasees)
                )
            self.valid = True
        elif kind == 'payment':
            if (not row['From']) or (not row['To']) or (not row['Amount']):
                return
            self.payer = row['From']
            self.payee = row['To']
            self.memo = 'Payment'
            self.amount = Decimal(row['Amount'].strip('$').replace(',', ''))

            self.lineitems = [
                    ("Liabilities:People:{}".format(self.payee),
                        '${}'.format(self.amount)),
                    ("Assets:People:{}".format(self.payer),
                        "$-{}".format(self.amount))
                    ]
            self.valid = True

    def __str__(self):
        if not self.valid:
            return "<Transaction INVALID>"
        else:
            return str(vars(self))

    def ledger(self):
        return '\n'.join([
            "{date_fmt} {memo}",
            '\n'.join([
                "    {0: <40}{1}".format(*li) for li in self.lineitems
            ])
        ]).format(date_fmt = self.date.strftime('%Y-%m-%d'), **vars(self))


def main(args):
    # Print the contents of the header file.
    if args.header:
        with open(args.header, 'r') as f:
            for line in f:
                print(line)

    # Read the purchases file
    with open(args.purchases, 'r') as f:
        # Discard the first two lines, which are garbage.
        next(f)
        next(f)

        # Read the transactions
        ts = (Transaction(row, "purchase") for row in csv.DictReader(f))
        for t in ts:
            # Skip invalid transaction records
            if not t.valid: continue

            # Print the transaction and its ledger translation
            print(t.ledger())
            print()

    # Read the payments file
    with open(args.payments, 'r') as f:
        # Read the transactions
        ts = (Transaction(row, "payment") for row in csv.DictReader(f))
        for t in ts:
            # Skip invalid transaction records
            if not t.valid: continue

            # Print the transaction and its ledger translation
            print(t.ledger())
            print()

def parse(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--purchases", default="purchases.csv")
    parser.add_argument("--payments", default="payments.csv")
    parser.add_argument("--header", default="header.ledger")

    return parser.parse_args(args)

if __name__ == "__main__":
    sys.exit(main(parse(sys.argv[1:])))

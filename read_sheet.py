#!/usr/bin/env python3

import sys
import csv
import datetime
import argparse
from decimal import Decimal

# Minimal implementation of translation layer for our CSV to Ledger
from transaction import *

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

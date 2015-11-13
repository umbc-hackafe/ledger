import datetime
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
            or not allow_empty and (not self.payer or not self.payee) \
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

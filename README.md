# Spreadsheet Reader

Hackafé maintains a spreadsheet for purchases and payments. Oftentimes, one
roommate will make a large purchase meant to be shared by others. We record
these in a spreadsheet, which we the `read_sheet.py` tool can read and translate
into a [Ledger][] journal. One can then produce reports automatically using
Ledger.

To see a sample report, run the following command to generate the journal
```
read_sheet.py --purchases purchases.csv.sample \
              --payments payments.csv.sample   \
              --header header.ledger.sample    \
              > sample.ledger
```
To create reports, try some of the following.
```
ledger -f sample.ledger balance
ledger -f sample.ledger balance Assets:People:Alice Liabilities:People:Alice
ledger -f sample.ledger register
```

## Producing Reports

Ledger can generate an of very interesting [reports][Ledger reports]. Some
useful ones are as follows.

### Show How Much Alice is Owed
The value will be negative if she is owed money.
```
ledger -f sample.ledger balance Assets:People:Alice Liabilities:People:Alice
```

### Show Purchase History
```
ledger -f sample.ledger register ^Expenses
```

## Automatic Modifiers, Budgeting, and the Header File

Ledger has the ability to modify transactions automatically, forecast costs, and
do other magic.  This can be implemented by writing Ledger-format [automated
transactions][Ledger automatic] and [periodic transactions][Ledger periodic] in
the static header file, which can be included in the output ledger file using
the `--header` option. (By default, this is `header.ledger`.)

[Ledger]: http://ledger-cli.org
[Ledger reports]: http://ledger-cli.org/3.0/doc/ledger3.html#Building-Reports
[Ledger automatic]: http://ledger-cli.org/3.0/doc/ledger3.html#Automated-Transactions
[Ledger periodic]: http://ledger-cli.org/3.0/doc/ledger3.html#Periodic-Transactions

# Spreadsheet Reader

Hackafé maintains a spreadsheet for purchases and payments. Oftentimes, one
roommate will make a large purchase meant to be shared by others. We record
these in a spreadsheet, which we the `read_sheet.py` tool can read and translate
into a [Ledger][] journal. One can then produce reports automatically using
Ledger.

To see a sample report, run the following command to generate the journal
```
read_sheet.py --purchases purchases.csv.sample --payments payments.csv.sample > sample.ledger
```
To create reports, try some of the following.
```
ledger -f sample.ledger balance
ledger -f sample.ledger balance Alice
ledger -f sample.ledger register
```

## Producing Reports

Ledger can generate an of very interesting [reports][Ledger reports]. Some
useful ones are as follows.

### Show How Much Alice is Owed
The value will be negative if she is owed money.
```
ledger -f sample.ledger balance Alice
```

### Show Purchase History
```
ledger -f sample.ledger register ^Expenses
```

[Ledger]: http://ledger-cli.org

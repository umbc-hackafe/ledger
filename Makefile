sheet.ledger: read_sheet.py purchases.csv payments.csv header.ledger
	./read_sheet.py --output sheet.ledger

sample.ledger: read_sheet.py purchases.csv.sample payments.csv.sample header.ledger.sample
	./read_sheet.py --purchases purchases.csv.sample \
	                --payments  payments.csv.sample \
	                --header    header.ledger.sample \
	                --output    $@

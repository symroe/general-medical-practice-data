UNAMENDED_CSV=$(shell find input/ -name 'epraccur_*.csv')
AMENDMENT_CSVS=$(shell find input/monthly_amendments -name 'egpam_*.csv')
AMENDMENT_PRACTICE_CSV=build/combined-amendments-only-gp-practices.csv

FINAL_JSON=lists/nhsuk/general-medical-practices.json

all: $(FINAL_JSON) lists/epraccur.csv

$(AMENDMENT_PRACTICE_CSV): $(AMENDMENT_CSVS)
	cat $(AMENDMENT_CSVS) | grep -v -e '^"G[0-9]\{7\}' > $(AMENDMENT_PRACTICE_CSV)

.PHONY: $(FINAL_JSON)
$(FINAL_JSON): $(UNAMENDED_CSV) $(AMENDMENT_PRACTICE_CSV)
	mkdir -p lists/nhsuk
	./process/convert.py $(UNAMENDED_CSV) $(AMENDMENT_PRACTICE_CSV) > $(FINAL_JSON)


EPRACCUR_URL=https://digital.nhs.uk/media/372/epraccur/zip/epraccur
lists/epraccur.csv:
	mkdir -p cache && curl -o cache/epraccur.zip "$(EPRACCUR_URL)"
	unzip -o cache/epraccur.zip epraccur.csv -d lists/epraccur/

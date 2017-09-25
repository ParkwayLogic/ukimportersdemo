# ukimportersdemo

No license at present for use, modify or share.

1 Download uktradeinfo zip files and extract to ex/import_names_unzipped_running

2 Run read_uktradeinfo_names.py, generates three different files

... then either skip bracketed steps, or
(
3 Download companies house DB files

4 Run read_companies_house.py, generates summary file for next step

5 Run fuzzynames.py, generates a list of best-matches
--> if recalculate_companies=True, it generates another file with added columns

6 Filter the best-matches list (in Excel or other) to remove low scores, save as ex/importers_matched.csv

7 Run join_tables.py
)

8 Run trade_summarise.py

"""
Make summary of SIC codes and HS codes from Ex/Import_combined.csv
(Uses the output of joint_tables.py)
"""

import pandas as pd

def main(action='Ex'):
	assert ((action=='Ex') | (action=='Im'))
	infile = action+'port_combined.csv'
	outsummfile = action+'port_combined_summary_2.csv'

	trades = pd.read_csv(infile, sep='\t', dtype='str',
		index_col=0, nrows=10000)  # usecols=cols_to_use
	
	# Count number of months per HS code per company
	index_cols = [' CompanyNumber','RegAddress.PostCode','Postcode',
	'HScode','co_name','Name','SICCode.SicText_1']
	tmp = pd.DataFrame(trades.groupby(by=index_cols).size())
	tmp.rename(columns={0: 'MonthCount'}, inplace=True)
	# print(tmp.head(20))
	# print(len(tmp))
	print('Saving counts with company details to {0}'.format(outsummfile))
	# cols_to_write = [
	# ' CompanyNumber','HScode','MonthCount','co_name','Name','Postcode',
	# 'SICCode.SicText_1'
	# ]
	tmp.to_csv(outsummfile, sep='\t')  # , columns=cols_to_write



if __name__ == '__main__':
	main()

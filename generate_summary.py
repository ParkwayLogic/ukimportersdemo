"""
Process from xxporters_vertical.csv to xxport_combined_summary.csv
Currently skips SIC codes, etc. from companies house, and therefore
contains exporters that do not appear in companies house
TODO: add switch to add SIC codes, etc. using fuzzy match (additively)
"""

import pandas as pd


def main(action='Im'):
	assert ((action=='Ex') | (action=='Im'))
	tradesfile = action+'porters_vertical.csv'
	outsummfile = action+'port_combined_summary_test.csv'

	print('Loading trades from {0}'.format(tradesfile))
	trades = pd.read_csv(tradesfile, sep='\t', dtype='str',
		index_col=0)  # nrows=10000 when testing
	# print('trades =', trades.head())
	# print('dropping un-used columns')
	trades.drop(['Add3','Add4','Add5','HSitem','HS6'], 
		axis=1, inplace=True)
	# usecols=['Month','Name','Add1','Add2','Postcode','HScode','HS2','HS4']

	index_cols = ['Postcode','HScode','Name']
	tmp = pd.DataFrame(trades.groupby(by=index_cols).size())
	tmp.rename(columns={0: 'MonthCount'}, inplace=True)

	print('Saving counts with company details to {0}'.format(outsummfile))
	tmp.to_csv(outsummfile, sep='\t')  # , columns=cols_to_write


if __name__ == '__main__':
	main()



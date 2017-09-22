"""
Compiles a joint table of companies with SIC codes, HS codes, HS chapter
Reads in three files:
Im/Exporters_HScode_months.csv has the HS codes
companies_house_selected_cols.csv has the SIC codes
Im/Exporters_matched.csv has the fuzzy name matching results
"""
import pandas as pd

def main(action='Ex'):
	assert ((action=='Ex') | (action=='Im'))
	matchfile = action+'porters_matched.csv'
	tradesfile = action+'porters_vertical.csv'
	outfullfile = action+'port_combined.csv'
	
	print('Loading name matches from {0}'.format(matchfile))
	if action=='Im':
		print('NOT IMPLEMENTED')
		raise
	else:
		names_match = pd.read_csv(matchfile, header=0).set_index(
			'ex_name', inplace=False)
	
	print('Loading trades from {0}'.format(tradesfile))
	trade_details = pd.read_csv(tradesfile, sep='\t', dtype='str',
		index_col=0)  # nrows=10000 when testing
	# print('dropping un-used columns')
	trade_details.drop(['Add3','Add4','Add5','HSitem','HS6'], 
		axis=1, inplace=True)
	# usecols=['Month','Name','Add1','Add2','Postcode','HScode','HS2','HS4']
	
	print('Loading companies house info')
	companies = (pd.read_csv('companies_house_selected_cols.csv')
		.set_index('CompanyName', inplace=False))
	# TODO: also get Mortgages.NumMortOutstanding from source files

	print('Joining tables')
	# First append the fuzzy name match results
	tmp = pd.merge(trade_details, names_match, how='inner',
		left_on='Name', right_index=True)
	del trade_details, names_match
	# Now append the companies house info
	new = pd.merge(tmp, companies, how='left',
		left_on='co_name', right_index=True)
	del companies, tmp
	# print('new', new.head())

	print('Saving full table with company names to {0}'.format(outfullfile))
	cols_to_write = [
	' CompanyNumber','RegAddress.PostCode','Postcode',
	'Month','HScode','HS2','HS4',
	'co_name','Name','SICCode.SicText_1','SICCode.SicText_2',
	'SICCode.SicText_3','SICCode.SicText_4','Add1'
	]
	new.to_csv(outfullfile, sep='\t', columns=cols_to_write)
	print('Done.')


if __name__ == '__main__':
	main()



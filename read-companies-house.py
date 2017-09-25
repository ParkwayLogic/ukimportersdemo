"""
Read Companies House info
"""

import os
import pandas as pd

def main():
	sourcedirectory = 'Companies House/downloads'
	files_list = list(set(os.listdir(sourcedirectory)))
	print('Reading files...')
	colstochoose = ['CompanyName', ' CompanyNumber', 'RegAddress.PostCode',
	'SICCode.SicText_1', 'SICCode.SicText_2', 'SICCode.SicText_3', 'SICCode.SicText_4']
	for i, sourcefilename in enumerate(files_list):
		print('Trying {0}'.format(sourcefilename), end=' ')
		if str(sourcefilename)[:6] == 'BasicC':
			if i==0:
				tmp = pd.read_csv(''.join([sourcedirectory,'/',sourcefilename]))
				shortcos = tmp.loc[:,colstochoose]
				# optional step omitted - remove inactive companies
				# CompanyStatus == 'Active' or 'Active - Proposal to Strike off'
			else:
				tmp = pd.read_csv(''.join([sourcedirectory,'/',sourcefilename]))
				# optional step omitted - remove inactive companies
				shortcos = pd.concat([shortcos, tmp.loc[:,colstochoose]], ignore_index=True)
			print('done.')
		else:
			print('skipped.')
	
	shortcos.to_csv('companies_house_selected_cols.csv')
	print('Saved to companies_house_selected_cols.csv')

if __name__ == '__main__':
	main()
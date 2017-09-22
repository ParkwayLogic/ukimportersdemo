"""
Stacks a tab-delimited data table formatted according to the UKTradeInfo
 Exporters so that there is only one HS code per row.
Saves it to an output file, also tab-delimited.
Looks for source data in a subdirectory called 'Exporters'
"""
import os
import pandas as pd
# action = 'Ex' or 'Im'
def main(action='Ex'):
	assert ((action=='Ex') | (action=='Im'))
	souredirectory = action+'porter_names_unzipped_running'
	# outputfile0 = action+'porters_uniques.csv'
	outputfile1 = action+'porters_vertical.csv'
	outputfile2 = action+'porters_HScode_months.csv'
	outputfile3 = action+'porters_HScode_width.csv'
	sourcefilenamestart = action.lower()+'port'

	indexcols = ['Month','Lines','Name','Add1','Add2','Add3','Add4',
	'Add5','Postcode']
	datacols = ['HS'+str(n) for n in list(range(1, 51))]
	colnames = indexcols + datacols
	files_list = list(set(os.listdir(souredirectory)))
	# print('Reading files...')
	for i, sourcefilename in enumerate(files_list):
		if str(sourcefilename)[:6] == sourcefilenamestart:
			if i==0:
				tmp_count = 1
				mydata = pd.read_csv(''.join(
					[souredirectory, '/', sourcefilename]),
					sep='\t', header=None, names=colnames, dtype='str')
				print('\rReading files... '+sourcefilename, end='')
			else:
				tmp_count += 1
				mydata = mydata.append(
					pd.read_csv(''.join(
					[souredirectory, '/', sourcefilename]), sep='\t',
					header=None, names=colnames, dtype='str'), 
					ignore_index=True)
				print('\rReading files... '+sourcefilename, end='')
	print('\rRead {0:,} rows from {1} files               '.format(mydata.shape[0], tmp_count))
	# print('Converting shape')
	# mydata = pd.melt(mydata.reset_index(), 
	# 	id_vars=indexcols, value_vars=datacols,
	# 	var_name='HSitem', value_name='HScode')
	# replace melt - it retains only one company row
	mydata = mydata.set_index(indexcols)
	# prevents stack() function below from collapsing these fields
	mydata = mydata.stack()  # reshapes with one shipment per row
	mydata = mydata.reset_index().rename(
		columns={'level_9':'HSitem',0:'HScode'})
	# print(mydata.head(100))
	mydata.drop('Lines', axis=1, inplace=True)
	# print('cleaning up')
	# Insert leading zero for HS chapters 1 to 9:
	print('\rCleaning up 1/6', end='')
	mydata['HScode'] = mydata['HScode'].map(
		lambda x: '0'+str(x) if len(str(x))==7 else x
		)
	# Insert leading zero for HS chapters 1 to 9 where code is anonymised
	print('\rCleaning up 2/6', end='')
	mydata['HScode'] = mydata['HScode'].map(
		lambda x: '0'+str(x) if len(str(x))==1 else x
		)
	# Now insert trailing zeros for anonymised HS (chapter) codes
	print('\rCleaning up 3/6', end='')
	mydata['HScode'] = mydata['HScode'].map(
		lambda x: str(x)[:2]+'000000' if len(str(x))==2 else x
		)
	# Industrial plant comcodes, starting 9880
	# Suppressed commodity codes, starting 990
	# --> next two digits are HS2 (chapter), HS4+ not defined:
	print('\rCleaning up 4/6', end='')
	mydata['HS2'] = mydata['HScode'].map(
		lambda x: str(x)[4:6] if str(x)[:4]=='9980' 
		else (str(x)[3:5] if str(x)[:3]=='990' 
		else str(x)[:2])
		)
	print('\rCleaning up 5/6', end='')
	mydata['HS4'] = mydata['HScode'].map(
		lambda x: '00' if str(x)[:4]=='9980' 
		else ('00' if str(x)[:3]=='990' 
		else str(x)[2:4])
		)
	print('\rCleaning up 6/6')
	mydata['HS6'] = mydata['HScode'].map(
		lambda x: '00' if str(x)[:4]=='9980' 
		else ('00' if str(x)[:3]=='990' 
		else str(x)[4:6])
		)
	# # Remove special codes
	# mydata = mydata[mydata['HScode']!=99209900] # Parcel post
	# mydata = mydata[mydata['HScode']!=99302400] # Ships & Aircraft stores
	# mydata = mydata[mydata['HScode']!=99302700] # Ships & Aircraft stores
	# mydata = mydata[mydata['HScode']!=99309900] # Ships & Aircraft stores
	# mydata = mydata[mydata['HScode']!=99500000] # Low value trade
	# mydata = mydata[mydata['HScode']!=99909908] # Continental shelf

	# print('\rSaving unique list of traders to {0}'.format(outputfile0))
	# mydata.drop_duplicates('Name', keep='first').to_csv(
	# 	outputfile0, sep='\t', columns=['Month','Name','Add1','Add2','Postcode']
	# 	)

	print('Saving full list to {0}'.format(outputfile1))
	mydata.to_csv(outputfile1, sep='\t', header=True) # one shipment per row

	print('Saving month count per CN code per company as {0}'.format(outputfile2))
	# TODO: rename doesn't work ??
	pd.read_csv(outputfile1, sep='\t', dtype='str'
		).groupby(by='Name')['HScode'].value_counts(
		).rename(columns={'HScode': 'HScode', 0: 'Monthcount'}, inplace=True
		).to_csv(outputfile2, sep='\t', header=True)

	print('Saving list of unique company names as {0}'.format(outputfile3))
	# TODO: rename doesn't work ??
	pd.read_csv(outputfile2, sep='\t'
		).groupby(by='Name').size(
		).rename(columns={0: 'HSwidth'}, inplace=False
		).to_csv(outputfile3, sep='\t', header=True)
	print('Done')
	

if __name__ == '__main__':
	main()
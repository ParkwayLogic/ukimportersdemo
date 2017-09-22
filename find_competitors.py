"""
Return exporters with overlapping most frequent commodity codes
"""
import sys
sys.path.insert(0,'lib')
import csv, utils
import networkx as nx
import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.externals import joblib
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_top_nodes(Gph, company, howmany=2):
    """Generate top-most commodities: returns sorted list of (u, v, d)"""
    all_edges = Gph.edges_iter(nbunch=[company], data='monthcount')
    sorted_edges = sorted(all_edges, key=lambda tup: -int(tup[howmany]))
    return sorted_edges


def load_data(sourcedata):
    """Reads in from tab separated file"""
    Gph = nx.Graph()
    with open(sourcedata, 'r') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t')
        # Adjust row[] indices depending on if sourcedata has
        # EITHER 5, 3, 5, 3, 7
        # [' CompanyNumber', 'RegAddress.PostCode', 'Postcode', 'HScode',
        # 'co_name', 'Name', 'SICCode.SicText_1', 'MonthCount']
        # OR 2, 1, 2, 1, 3 for
        # ['Postcode', 'HScode', 'Name', 'MonthCount']
        for i, row in enumerate(tsvin):
            Gph.add_node(row[2], type='Name')
            Gph.add_node(row[1], type='Commodity')
            Gph.add_edge(row[2], row[1], monthcount=row[3])
            # if i < 20: print(Gph.edges())
    return Gph
    

@app.route('/', methods=['GET'])
def main():
    """Runs the main program"""
    rg = dict(request.args.items())
    print('rg =', rg)
    print('Loading trader data ...')
    action = rg['exim']
    assert ((action=='Ex') | (action=='Im'))
    sourcedata=action+'port_combined_summary_test.csv'
    Gph = load_data(sourcedata)

    if ('cn1' in rg) and ('cn2' in rg):  # given two commodity codes
        common_HS = [rg['cn1'], rg['cn2']]
    elif 'name' in rg:  # given a company name
        print('searching for comcodes traded by', rg['name'])
        tops = [t for t in get_top_nodes(Gph, rg['name'])]
        if len(tops) > 1:
            top1, top2 = tops[:2]
        else:
            print('Not enough comcodes found, searching by SIC code instead')
            """
            1. Look up SIC code from company name
            2. Lookup top two HS codes for SIC code, from table to be created
            """
            print('SIC-based search not implemented')
            raise NotImplementedError
        common_HS = [top1[1], top2[1]]
    else:
        print('No valid search paramters given. Proceeding with default.')
        common_HS=['94033019','94034090']
    
    print('Identified', common_HS[0], common_HS[1], 'as two top comcodes')
    # c1 = utils.get_desc_by_CN(common_HS[0])
    # c2 = utils.get_desc_by_CN(common_HS[1])
    # print('Preparing subgraph for\n{0} - {1}\nand\n{2} - {3}'.format(
    #     common_HS[0], c1['Self-Explanatory text (English)'].values[0],
    #     common_HS[1], c2['Self-Explanatory text (English)'].values[0]
    # ))
    # nodes1 = Gph.subgraph(find_common_codes(Gph, common_HS))
    # nx.write_gexf(nodes1,'common_subgraph.gexf')
    # Generate text response
    names = [n for n in nx.common_neighbors(Gph, common_HS[0], common_HS[1])]
    retdict = {}
    for name in names:
        cmdties = dict([(c[1], c[2]) for c in get_top_nodes(Gph, name)])
        retdict[name] = cmdties
    print('Returning result as json object')
    return jsonify({'competitors': dict(retdict)}), 200


@app.errorhandler(500)
def server_error(e):
   return """
   An internal error occurred: <pre>{}</pre>
   See logs for full stacktrace.
   """.format(e), 500


if __name__ == '__main__':
    print('Server running...')
    app.run(host='127.0.0.1', port=8080, debug=True)

# 84118280 84119900
# 94033019 94034090
# 82121090 84191100

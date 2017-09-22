"""
Network of exporters details and commodity codes
"""

import csv
import networkx as nx

def load_data(sourcedata, company=None):
    """Reads in from tab separated file"""
    Gph = nx.Graph()
    with open(sourcedata, 'r') as tsvfile:
        tsvin = csv.reader(tsvfile, delimiter='\t')
        # [' CompanyNumber', 'RegAddress.PostCode', 'Postcode', 'HScode',
        # 'co_name', 'Name', 'SICCode.SicText_1', 'MonthCount']
        for i, row in enumerate(tsvin):
            Gph.add_node(row[4], type='Name')
            Gph.add_node(row[3], type='Commodity')
            Gph.add_edge(row[4], row[3], monthcount=row[7])
    
    if company==None:
        return Gph
    else:
        all_edges = Gph.edges_iter(nbunch=company, data='monthcount')
        edg1, edg2 = sorted(all_edges, key=lambda tup: tup[1])[:2]  # 2 highest monthcounts
        top_cmdties = [edg1[1], edg2[1]]
        # print(top_cmdties)
        return Gph, top_cmdties


def get_top_nodes(Gph, howmany=5000, excltop=1000):
    """
    Generate top-most companies according to variety of commodity codes exported
    TODO: get degrees of 'Name' nodes only, not Commodity nodes
    """
    HS_width = nx.degree(Gph).items()
    sorted_degrees = sorted(HS_width, key=lambda tup: tup[1])  # TODO: check the key lambda
    if excltop==0:
        for (name, degree) in sorted_degrees[-howmany:]:
            yield name
    else:
        for (name, degree) in sorted_degrees[-howmany:-excltop:]:
            yield name


def find_common_codes(Gph, common_HS):
    """
    Generator of companies and commodities that export a common set of commodities
    """
    u, v = common_HS
    # print(u, v)
    name_gen = nx.common_neighbors(Gph, u, v)
    # name_gen = [w for w in Gph[u] if w in Gph[v] and w not in (u, v)]
    # only company names are neighbours of commodity codes
    selected_nodes = []
    for name in name_gen:
        yield name
        cmdty_gen = nx.all_neighbors(Gph, name)
        # only commodity nodes are neighbours of company (name) nodes
        for cmdty_node in cmdty_gen:
            yield cmdty_node


def main(*args):
    """Runs the main program"""
    rg = []
    for i, r in enumerate(*args):
        rg.append(r)
    print('Loading main graph ...')
    sourcedata='Export_combined_summary.csv'

    if len(rg)==4:
        common_HS = [rg[2], rg[3]]
        Gph = load_data(sourcedata)
    elif len(rg)==3:
        Gph, common_HS = load_data(sourcedata, rg[2])
    else:
        print('No valid search paramters given. Proceeding with default.')
        common_HS=['94033019','94034090']

    # print('and saving.')
    # nx.write_gexf(Gph, 'exporters.gexf')
    print('Preparing subgraphs')
    # nx.write_gexf(Gph.subgraph(get_top_nodes(Gph)),'topnodes.gexf')
    nodes1 = Gph.subgraph(find_common_codes(Gph, common_HS))
    nx.write_gexf(nodes1,'common_subgraph.gexf')
    for node in nodes1:
        print(node)


if __name__ == '__main__':
    import sys
    main(sys.argv)

# 84118280 84119900
# 94033019 94034090
# 82121090 84191100


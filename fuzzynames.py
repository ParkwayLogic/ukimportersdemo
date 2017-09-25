import time
import csv
import pandas as pd
import cProfile, pstats

common_alts = [
    ['ltd', 'limited'],
    ['uk', 'united kingdom'],
    ['and', '&'],
    ['itl', 'international'],
    ['co', 'company'] # consider adding 
]
# Items that should not count towards similarity score
zero_scores = ['ltd', 'plc', 'the', 'srl'] # consider adding 'inc', 'itl', 'uk'
outlist = []  # stores the matched company names

def check_eq_list(w1, w2):
    """
    Takes two strings, returns a 1/0 (instead of actual boolean)
    """
    # BROKEN??: entire string should be in list, should not accept substring (e.g. 'arm' in 'farm')
    global common_alts
    result = 0
    if w1==w2:
        result = 1
    else:
        for equivs_list in common_alts:
            if (w1 in equivs_list) & (w2 in equivs_list):
                result = 1
            else:
                pass
    return result

def are_same(shortokens, longtokens):
    """Find exact matches, or tokens deemed equivalent, returns score between zero and one"""
    same_count = 0
    max_count = 0
    global zero_scores
    for k, (w1, w2) in enumerate(zip(longtokens, shortokens)): # check pair-wise in strict order
        if k < 2:  # give more weight to the first 2 words in the name
            weight = 3
        else:
            weight = 1
        word1 = w1
        word2 = w2
        if (w1 in zero_scores) & (w2 in zero_scores): # skip common items like 'ltd' from scoring
            pass
        else: # w1 or w2 not in zero_score
            max_count += weight
            same_count += check_eq_list(word1, word2) * weight
    return same_count/max_count  # safer to apply max(0,min(1,...)) but they are slow function calls

def char_order(str1, str2, verbose=False):
    """Takes two character lists, returns a number between zero and one"""
    # TODO: make another version enforcing relative ordering of the letters
    l1, l2 = len(str1), len(str2)
    pytop = abs(l1 - l2) # the for loop below stops at the shorter of the two strings - don't ignore
    top = pytop  # TODO: is this needed?
    accum = 0
    for k, (i, j) in enumerate(zip(str1, str2)):
        if k < 5: # we will give higher weight to the first 5 characters
            weight = 2
        else:
            weight = 1
        top += weight
        if i == j:
            accum += weight
        else:
            if k<=2: accum -= 3 # extra penalty for early characters' mismatch
    return accum / top  # safer to apply max(0,min(1,...)) but they are slow function calls

def lower_and_standard(longname):
    # Replace known strings with standard form (e.g. United Kingdom to UK)
    global common_alts
    longname = longname.strip().casefold() # remove any leading&trailing whitespace, make lowercase
    for equivs_list in common_alts:
        for item in equivs_list:
            if item in longname:
                longname = longname.replace(item, equivs_list[0], 1)
    return longname

def only_alphanum(tk):
    """Strip out non-alphanumeric characters from an arbitrary sting. Leaves spaces untouched."""
    tmp = ''.join(ch for ch in tk if (ch.isalnum() | (ch=='&') | (ch==' ')))
    if tmp[0]!=tk[0]: # don't throw away initial character, even if it is not alphanumeric
        return ''.join((tk[0],tmp))
    else:
        return tmp
    
def only_alphanumseq(tk):
    """Strip out non-alphanumeric characters from an arbitrary sting"""
    tmp = ''.join(ch for ch in tk if (ch.isalnum() | (ch=='&')))
    if tmp[0]!=tk[0]: # don't throw away initial character, even if it is not alphanumeric
        return ''.join((tk[0],tmp))
    else:
        return tmp

def pre_process(longname):
    try:
        # Returns standardised text as a list of tokens (words)
        longname1 = lower_and_standard(longname)
        # Strip out non-alphanumeric characters, to ignore periods, hyphens and other punctuations
        return only_alphanum(longname1)
    except:
        print('renamed name in tokens list', longname)
        return 'companyskipped'

def pre_process_nospace(longname):
    try:
        # Returns standardised text as a space-less list of characters
        longname1 = lower_and_standard(longname)
        # Strip out non-alphanumeric characters, to ignore periods, hyphens and other punctuations
        return only_alphanumseq(longname1)
    except:
        print('renamed name in nospace list', longname)
        return 'companyskipped'

def similarity(ex_tokens, ex_clean, co_tokens, co_clean):
    """
    First tries to find exact matches (within equivalence classes)
    Then looks for near matches
    """
    score1 = are_same(ex_tokens, co_tokens)
    # TODO: add abbreviation (with or without full stop) to equiv classes
    # similarity ignoring spaces and non-alphanums - just checking sequence of letters
    score2 = char_order(ex_clean, co_clean)
    score = (score1 + 3*score2)/4
    return score

def update_progress_bar(progress, time_elapsed, prefix="", suffix=""): # remcount
    """progress from zero+ to one"""
    togo = time_elapsed*(1-progress)/progress/60
    if togo > 240:
        print("\rProgress: [{0:.<20s}] {1:.2f}%, {2:,}s elapsed, ~{3:,} hrs to go{4}".format(
                '#'*int(progress*20), progress*100, int(time_elapsed), int(togo/60), str(suffix)
            ), end='')
    else:
        print("\rProgress: [{0:.<20s}] {1:.2f}%, {2:,}s elapsed, ~{3:,} mins to go{4}".format(
                '#'*int(progress*20), progress*100, int(time_elapsed), togo, str(suffix)
            ), end='')


def matchnames(recalculate_companies=False, thoroughness="fast"):

    import csv
    global outlist
    global cexporters
    global companies
    maxexporters = len(cexporters)  # min(100, len(cexporters))

    if recalculate_companies:
        raw_got = pd.read_csv('companies_house_selected_cols.csv', sep=',')
        global companies
        companies = pd.Series(data=raw_got['CompanyName'], name='comps', dtype='str')
        # print('companies is\n{0}'.format(companies.head()))
        del raw_got
        print('Loaded companies db')
        maxcompanies = len(companies)
    
        print('Pre-processing and storing')
        # # Do slow pre-processing of the large list once and store
        cleanSeries = pd.Series(data=[pre_process(x) for x in companies],
                               index=companies, name='clean', dtype='str')
        nospaceSeries = pd.Series(data=[pre_process_nospace(x) for x in companies],
                               index=companies, name='nospace', dtype='str')
        print('step 1/3 preprocessing done')
        # Find starting characters
        startCharSeries = pd.Series(data=[str(x[0]) for x in nospaceSeries],
                                   index=companies, name='startchar', dtype='str')
        compsremaining = pd.concat([cleanSeries, nospaceSeries, startCharSeries],axis=1)
        print('step 2/3 preprocessing done')
        startcharset = set(startCharSeries)  # use set() so we check each character only once
        del cleanSeries, nospaceSeries, startCharSeries
        for ch in startcharset:
            tmp = pd.Series(data=[(x==ch) for x in compsremaining['startchar']],
                                      index=companies, name=str(ch))  # boolean
            compsremaining = pd.concat([compsremaining, tmp], axis=1)
            del tmp
        print('step 3/3 preprocessing done, saving preprocessed to file')
        compsremaining.to_csv('companies_house_with_helper_cols.csv', index=True)
        del startcharset
    else:
        print('Loading companies with pre-calculated helper columns')
        compsremaining = pd.read_csv('companies_house_with_helper_cols.csv', index_col=False)
        print('Done.')
        maxcompanies = len(compsremaining)

    print('Taking {0:,} of {1:,} exporters, and {2:,} of {3:,} companies'.format(
            maxexporters, len(cexporters), maxcompanies, len(compsremaining)))
    # Gather all cross-scores and store the highest scoring match pairs
    print('{0:,} x {1:,} = {2:,} cross-checks to go'.format(maxexporters, 
            maxcompanies, maxexporters*maxcompanies))
    
    startloop = time.time()
    timetrace = []
    bucket_quick_success = 0
    bucket_slow_success = 0
    for i, ex_name in enumerate(cexporters):  # check for each exporter
        if i < maxexporters:
            ex_tokens = pre_process(ex_name).split()
            ex_clean = pre_process_nospace(ex_name)
            char1 = ex_clean[0] # initial letter of ex_name
            # Find top matches, store them in temptop
            temptop = {'co_name': 'empty', 'ex_name': ex_name, 'score': 0}
            # check exporters database
            # First try searching in sub-list with the same starting character
            shorlist = compsremaining.loc[compsremaining.loc[:,'startchar']==char1,:]
            for co_name, co_clean, co_nospace in zip(shorlist['comps'], shorlist['clean'], 
                shorlist['nospace']):
                try:
                    score = similarity(ex_tokens, ex_clean, co_clean.split(' '), co_nospace)
                except AttributeError:
                    pass
                except:
                    raise
                if score > temptop['score']:
                    temptop['co_name'] = co_name
                    temptop['score'] = score  
                    if score>=0.75:
                        bucket_quick_success += 1
                        break
            else: # a good match was not found: the for loop went to the end and did not break
                del shorlist
                if thoroughness=='thorough': # now keep searching the rest of the list
                    longlist = compsremaining.loc[compsremaining.loc[:,'startchar']!=char1,:]
                    for co_name, co_clean, co_nospace in zip(longlist['comps'], longlist['clean'],
                        longlist['nospace']):
                        try:
                            score = similarity(ex_tokens, ex_clean, co_clean.split(' '), co_nospace)
                        except AttributeError:
                            pass
                        except:
                            raise
                        if score > temptop['score']:
                            temptop['co_name'] = co_name
                            temptop['score'] = score  
                            if score>=0.75:
                                bucket_slow_success += 1
                                break
            # Append company most closely matching the exporter, then go to the next exporter
            outlist.append(temptop)
            t = time.time()-startloop
            with open('find_xxporters_temp.csv', 'a') as csvfile:
                csvlogger = csv.writer(csvfile)
                csvlogger.writerow([
                    str(temptop['co_name']),
                    str(temptop['ex_name']),
                    str(temptop['score'])
                    ])
            update_progress_bar(progress=(i+1)/maxexporters, time_elapsed=t,
                                suffix=', matched {0:,} fast + {1:,} slow, out of {2:,}'.format(
                                bucket_quick_success, bucket_slow_success, i+1)
                               )
            timetrace.append([i,t,bucket_quick_success,bucket_slow_success])
            
    print("")
    
    with open('timetrace.csv', 'w', newline='') as csvfile:
        tracewriter = csv.writer(csvfile, delimiter=',')
        tracewriter.writerows(timetrace)
    return outlist
    

def main():

    global action
    action = 'Im'
    raw_got = pd.read_csv(action+'porters_HScode_width.csv', sep='\t') # exporters list
    global cexporters
    cexporters = raw_got['Name']
    print('Loaded {0}porters db'.format(action))
    del raw_got

    global outlist
    outlist = matchnames(recalculate_companies=False, thoroughness="fast")
    
    outlist = pd.DataFrame(outlist)
    outlist.to_csv('find_{0}porters.csv'.format(action))
    # TODO: join tables and export to CSV


if __name__ == '__main__':
    main()

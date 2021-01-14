#!/usr/bin/python

import random
import sys
import diff_file_parser
from download_diff import DIFF_FILE_PATH
import nltk
from nltk.stem.porter import PorterStemmer


def extract(commit_info,configVariableList):

    commit_info = commit_info.split('$$$')
    commit_url = commit_info[0]
    commit_title = commit_info[1]
    commit_time = commit_info[2]
    commit_sha = commit_url.split('/')
    commit_sha = commit_sha[-1]

    desc_contain_keyword = False #whether commit description contains the configuration keyword
    is_merge_commit = False
    diff_contain_config = False #whether diff touches configuration

    titile_words = commit_title.split(' ')
    for word in titile_words:
        if word.lower() == 'option' or word.lower() == 'parameter':
            commit_title = commit_title.replace(word, "**" + word.upper() + "**")
            desc_contain_keyword = True
        st = PorterStemmer()
        word_stemmed = st.stem(word).lower()
        if word_stemmed in {'config','configure'}:
            commit_title = commit_title.replace(word_stemmed, "**" + word_stemmed.upper() + "**")
            desc_contain_keyword = True

    
    commit_titleword = commit_title.lower().split(' ')
    for word in {'merge','merging','checkstyle','findbugs'}:
        if word in commit_titleword:
            is_merge_commit = True
            break
    
    code_result = []
    diff_file_path = DIFF_FILE_PATH + '/' + commit_sha + '.diff'
    if is_merge_commit == False:
        code_result = diff_file_parser.diff_selection(diff_file_path, configVariableList)

    config_file_touched = False

    config_load_touched = False

    config_set_touched = False

    config_variable_touched = False

    config_message_touched = False

    if code_result:
        
        config_file_touched = code_result[0]

        config_load_touched = code_result[1]

        config_set_touched = code_result[2]

        config_variable_touched = code_result[3]

        config_message_touched = code_result[4]

        #the set of touched configuration option
        touched_config_file = code_result[5]

        #the set of touched configuration load function
        touched_config_load_func = code_result[6]

        #the set of touched configuration set function
        touched_config_set_func = code_result[7]

        #the set of touched configuration variables
        touched_variable = code_result[8]

        #the set of touched meesgae keyword
        touched_message = code_result[9]

    if True in (config_file_touched,config_load_touched,config_set_touched,config_variable_touched,config_message_touched):
        diff_contain_config = True


    if (is_merge_commit == False) and (desc_contain_keyword == True or diff_contain_config == True):
        print("find a candidate commit!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        file = open('commit_selected.txt', 'a')
        file.write("###############################################################################" + '\n')
        file.write(commit_title + '\n' + commit_url + '\n' + commit_time + '\n')
        file.write('Commit message touches config:' + str(desc_contain_keyword) + '\n')
        file.write('Diff touches config define:' + str(config_file_touched) + '\n')
        file.write('Diff touches config loading:' + str(config_load_touched) + '\n')
        file.write('Diff touches config setting:' + str(config_set_touched) + '\n')
        file.write('Diff touches config variable (data flow):' + str(config_variable_touched) + '\n')
        file.write('Diff touches config message:' + str(config_message_touched) + '\n')
        
        file.write('\n_________________touchedConfigDefine_____________________\n\n')
        if config_file_touched:
            for config_file in touched_config_file:
                file.write(config_file)
                file.write('\n')
        else:
            file.write('Null\n')

        file.write('\n___________________touchedConfigLoad___________________\n\n')
        if config_load_touched:
            for config_load_func in touched_config_load_func:
                file.write(config_load_func + '\n')
        else:
            file.write('Null\n')
            
        file.write('\n___________________touchedConfigSet______________________\n\n')
        if config_set_touched:
            for config_set_func in touched_config_set_func:
                file.write(config_set_func + '\n')
        else:
            file.write('Null\n')

        file.write('\n___________________touchedConfigVariable_____________________\n\n')
        if config_variable_touched:
            for param in touched_variable:
                file.write(param + '\n')
        else:
            file.write('Null\n')

        file.write('\n____________________touchedMessage________________________\n\n')
        if config_message_touched:
            for keyword in touched_message:
                file.write('"' + keyword + '"' + '\n')
        else:
            file.write('Null\n')

        file.write('\n')

        file.close()








            

    


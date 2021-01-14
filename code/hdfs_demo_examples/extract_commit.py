#!/usr/bin/python

import random
import sys
import diff_file_parser
from download_diff import DIFF_FILE_PATH
import nltk
from nltk.stem.porter import PorterStemmer


def extract(commit_info,configParamList):

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
        if word_stemmed in {'config','configur'}:
            commit_title = commit_title.replace(word_stemmed, "**" + word_stemmed.upper() + "**")
            desc_contain_keyword = True

    
    commit_titleword = commit_title.lower().split(' ')
    for word in {'merge','merging','checkstyle','findbugs'}:
        if word in commit_titleword:
            is_merge_commit = True
            break
    
    codeResult = []
    diff_file_path = DIFF_FILE_PATH + '/' + commit_sha + '.diff'
    if is_merge_commit == False:
        codeResult = diff_file_parser.diffSelection(diff_file_path, configParamList)

    #Wheter a diff touches configuration file
    configFileTouched = False

    #Wheter a diff touches configuration load function
    configLoadTouched = False

    #Wheter a diff touches configuration set function
    configSetTouched = False

    #Wheter a diff touches configuration parameter
    configParamTouched = False

    #Whether a diff touches configuration message
    configMessageTouched = False

    if codeResult:
        
        configFileTouched = codeResult[0]

        configLoadTouched = codeResult[1]

        configSetTouched = codeResult[2]

        configParamTouched = codeResult[3]

        configMessageTouched = codeResult[4]

        #the set of touched file
        touchedFile = codeResult[5]

        #the set of touched configuration load function
        touchedLoadFunc = codeResult[6]

        #the set of touched configuration set function
        touchedSetFunc = codeResult[7]

        #the set of touched configuration parameter
        touchedParam = codeResult[8]

        #the set of touched meesgae
        touchedMessage = codeResult[9]

    if True in (configFileTouched,configLoadTouched,configSetTouched,configParamTouched,configMessageTouched):
        diff_contain_config = True

    if (is_merge_commit == False) and (desc_contain_keyword == True or diff_contain_config == True):
        print("find a candidate commit!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        file = open('commit_selected.txt', 'a')
        file.write("###############################################################################" + '\n')
        file.write(commit_title + '\n' + commit_url + '\n' + commit_time + '\n')
        file.write('Commit message touches config:' + str(desc_contain_keyword) + '\n')
        file.write('Diff touches config define:' + str(configFileTouched) + '\n')
        file.write('Diff touches config loading:' + str(configLoadTouched) + '\n')
        file.write('Diff touches config setting:' + str(configSetTouched) + '\n')
        file.write('Diff touches config variable (data flow):' + str(configParamTouched) + '\n')
        file.write('Diff touches config message:' + str(configMessageTouched) + '\n')
        
        file.write('\n_________________touchedConfigDefine_____________________\n\n')
        if configFileTouched:
            for fileName in touchedFile:
                file.write(fileName + ' ')
            file.write('\n')
        else:
            file.write('Null\n')

        file.write('\n___________________touchedConfigLoad___________________\n\n')
        if configLoadTouched:
            for loadFunc in touchedLoadFunc:
                file.write(loadFunc + '\n')
        else:
            file.write('Null\n')

        file.write('\n___________________touchedConfigSet____________________\n\n')
        if configSetTouched:
            for setFunc in touchedSetFunc:
                file.write(setFunc + '\n')
        else:
            file.write('Null\n')

        file.write('\n___________________touchedConfigVariable_____________________\n\n')
        if configParamTouched:
            for param in touchedParam:
                file.write(param + '\n')
        else:
            file.write('Null\n')

        file.write('\n___________________touchedMessage_____________________\n\n')
        if configMessageTouched:
            for keyword in touchedMessage:
                file.write('"' + keyword + '"' + '\n')
        else:
            file.write('Null\n')

        file.write('\n')

        file.close()








            

    


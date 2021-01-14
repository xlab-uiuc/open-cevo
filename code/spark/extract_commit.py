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
    if len(commit_info)>=3:
        commit_time = commit_info[2]
    commit_sha = commit_url.split('/')
    commit_sha = commit_sha[-1]

    desc_contain_keyword = False #whether commit description contains the configuration keyword
    irrelevant_commit = False
    diff_contain_config = False #whether diff touches configuration

    commit_title.replace('## What changes were proposed in this pull request?','')
    titile_words = commit_title.split(' ')
    count = 0
    for word in titile_words:
        if count > 20:
            break
        if word.lower() == 'option' or word.lower() == 'parameter':
            commit_title = commit_title.replace(word, "**" + word.upper() + "**")
            desc_contain_keyword = True
        st = PorterStemmer()
        word_stemmed = st.stem(word).lower()
        if 'config' in word.lower():
            commit_title = commit_title.replace(word, "**" + word.upper() + "**")
            desc_contain_keyword = True
        count = count + 1

    
    commit_titleword = commit_title.lower().split(' ')
    for word in {'merge','merging','checkstyle'}:
        if word in commit_titleword:
            irrelevant_commit = True
            break
    
    codeResult = []
    diff_file_path = DIFF_FILE_PATH + '/' + commit_sha + '.diff'
    if irrelevant_commit == False:
        codeResult = diff_file_parser.diff_selection(diff_file_path, configVariableList)

    #Whether a diff touches configuration doc
    configDocTouched = False

    #Whether a diff touches configuration build
    configBuildTouched = False

    #Whether a diff touches configuration load function
    configLoadTouched = False

    #Whether a diff touches configuration set function
    configSetTouched = False

    #Whether a diff touches configuration Variable
    configVariableTouched = False

    #Whether a diff touches configuration message
    configMessageTouched = False

    if codeResult:
        
        configDocTouched = codeResult[0]

        configBuildTouched = codeResult[1]

        configLoadTouched = codeResult[2]

        configSetTouched = codeResult[3]

        configVariableTouched = codeResult[4]

        configMessageTouched = codeResult[5]

        #the set of touched build function
        touchedBuildFunc = codeResult[6]

        #the set of touched configuration load function
        touchedConfigLoadFunc = codeResult[7]

        #the set of touched configuration set function
        touchedConfigSetFunc = codeResult[8]

        #the set of touched configuration variables
        touchedVariable = codeResult[9]

        #the set of touched meesgae keyword
        touchedMessage = codeResult[10]

    if True in (configDocTouched,configBuildTouched,configLoadTouched,configSetTouched,configVariableTouched,configMessageTouched):
        diff_contain_config = True

    if (irrelevant_commit == False) and (desc_contain_keyword == True or diff_contain_config == True):
        print("find a candidate commit!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        file = open('commit_selected.txt', 'a')
        file.write("###############################################################################" + '\n')
        file.write(commit_title + '\n' + commit_url + '\n' + commit_time + '\n')
        file.write('Commit message touches config:' + str(desc_contain_keyword) + '\n')
        file.write('Diff touches config define(doc):' + str(configDocTouched) + '\n')
        file.write('Diff touches config define(buildFunc):' + str(configBuildTouched) + '\n')
        file.write('Diff touches config loading:' + str(configLoadTouched) + '\n')
        file.write('Diff touches config setting:' + str(configSetTouched) + '\n')
        file.write('Diff touches config variable (data flow):' + str(configVariableTouched) + '\n')
        file.write('Diff touches config message:' + str(configMessageTouched) + '\n')
        
        file.write('\n_________________touchedConfigDefine(Doc)_____________________\n\n')
        if configDocTouched:
            file.write('configuration.md' + ' ')
            file.write('\n')
        else:
            file.write('Null\n')

        file.write('\n_________________touchedConfigDefine(Build)_____________________\n\n')
        if configBuildTouched:
            for builFunc in touchedBuildFunc:
                file.write(builFunc + ' ')
            file.write('\n')
        else:
            file.write('Null\n')

        file.write('\n___________________touchedConfigLoad___________________\n\n')
        if configLoadTouched:
            for configLoadFunc in touchedConfigLoadFunc:
                file.write(configLoadFunc + '\n')
        else:
            file.write('Null\n')

        file.write('\n___________________touchedConfigSet____________________\n\n')
        if configSetTouched:
            for setFunc in touchedConfigSetFunc:
                file.write(setFunc + '\n')
        else:
            file.write('Null\n')

        file.write('\n___________________touchedConfigVariable_____________________\n\n')
        if configVariableTouched:
            for variable in touchedVariable:
                file.write(variable + '\n')
        else:
            file.write('Null\n')
        
        file.write('\n_______________________touchedMessage________________________\n\n')
        if configMessageTouched:
            for keyword in touchedMessage:
                file.write('"' + keyword + '"' + '\n')
        else:
            file.write('Null\n')

        file.write('\n')

        file.close()








            

    


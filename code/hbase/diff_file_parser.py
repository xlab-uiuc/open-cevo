import re
import download_diff
from pathlib import Path

BASE_URL = "https://github.com/apache/hbase/commit/"

#configFile name for HBase
HBASE_CONFIG_FILE_RE = '[a-zA-Z\.\_\-]*-default.xml'

#RE for config Load in HBase
HBASE_CONFIG_LOAD_FUNC_RE = '[a-zA-Z\.\_\-]*[cC]onf[ig]*[\(\)]*[\s]*[\n]*[\s]*\.[\s]*[\n]*[\s]*get[a-zA-Z]*\([^;<>]+\)'

#RE for config assign in HBase
HBASE_CONFIG_ASSIGN_RE = '[a-zA-Z\.\_\-]+[\s]*=[\s]*[\n]*[\s]*' + HBASE_CONFIG_LOAD_FUNC_RE

#RE for config set in HBase
HBASE_CONFIG_SET_FUNC_RE = '[a-zA-Z\.\_\-]*[cC]onf[ig]*[\(\)]*[\s]*[\n]*[\s]*\.[\s]*[\n]*[\s]*set[a-zA-Z]*\([^;<>]+\)'

#RE for system parameter load in HBase
HBASE_SYS_PARAM_LOAD_FUNC_RE = 'System\.get(?:Property|env)\([^)^;]+\)'

#RE for system parameter assign in HBase
HBASE_SYS_PARAM_ASSIGN_FUNC_RE = '[a-zA-Z\.\_\-]+[\s]*=[\s]*[\n]*[\s]*' + HBASE_SYS_PARAM_LOAD_FUNC_RE

#RE for system parameter set in HBase
HBASE_SYS_PARAM_SET_FUNC_RE = 'System\.set(?:Property|env)\([^)^;]+\)'
    
#RE for message in program
MESSAGE_RE = '".+"'

class DiffElement:
    def __init__(self):
        self.diff_class = '' #class that this diff belongs to 
        self.diff_method = '' #method that this diff belongs to 
        self.diff_snippet = '' #changed code in this diff
        self.diff_change_mode = '' #'+' or '-'

class CodeElement:
    def __init__(self):
        self.code_class = '' #class that this diff belongs to 
        self.code_snippet = '' #changed code in this diff

class ConfigVariable:
    def __init__(self):
        self.variable_name = ''  #Variable name
        self.variable_class = '' #class that this Variable belongs to 
        self.variable_func = '' #function that assign this Variable

def add_diff_snippet(code_snippet,changed_class,change_mode,changed_method):
    code_element = DiffElement()
    code_element.diff_snippet = code_snippet
    code_element.diff_class = changed_class
    code_element.diff_change_mode = change_mode
    code_element.diff_method = changed_method
    return code_element

def collect_config_variable(assign_obj,code_element,config_variable_list):
    """collect variables that assgined by Cassandra configuration/system properties"""
    assign_obj = assign_obj.replace('\n','').replace(' ','').replace('this.','')

    #extract Variable that assigned
    m_variable = ConfigVariable()
    m_variable.variable_class = code_element.code_class
    m_variable.variable_func = assign_obj
    variable_name = assign_obj.split('=')
    variable_name = variable_name[0]
    m_variable.variable_name = variable_name
                            
    #if this Variable is a new Variable, add it into configVariable set
    duplicate_flag = 0
    for variable in config_variable_list:
        if m_variable.variable_name == variable.variable_name and m_variable.variable_class == variable.variable_class:
            duplicate_flag =1
            break
    if duplicate_flag == 0 and len(m_variable.variable_name)>=3 and m_variable.variable_class != 'null':
        config_variable_list.append(m_variable)
        file = open('config_variable.txt','a')
        file.write(m_variable.variable_name + '##' + m_variable.variable_class + '##' + m_variable.variable_func + '\n')
        file.close()

def diff_file_parser(url):
    """parse the diff_file, return the whole code and changed code (codeSet, diffSet)"""
    try:
        diff_file = open(url,'r')
    except (Exception) as e:
#        print (e)
        if Path(url).is_file() == False:
            commit_sha = url.replace('.diff','').split('/')
            download_diff.download(BASE_URL + commit_sha[-1])
            diff_file = open(url,'r')
        else:
            print (e)
            return
    
    #get code snippets, correlated class
    code_set = []
    code_snippet = ''
    code_class = ''
    for line in diff_file:
        if line:
            line = line.strip('\n')
            if len(line) > 1:
                if '+++' in line or '---' in line:
                    if code_snippet:
                        code_element = CodeElement()
                        code_element.code_snippet = code_snippet
                        code_element.code_class = code_class
                        code_set.append(code_element)
                        code_snippet = ''
                    if '/dev/null' not in line:
                        line = line.split('/')
                        code_class = line[-1]
                else:
                    if line[0] == '+':
                        line = line.replace('+','',1)
                    if line[0] == '-':
                        line = line.replace('-','',1)
                    code_snippet = code_snippet + line
    if code_snippet:
        code_element = CodeElement()
        code_element.code_snippet = code_snippet
        code_element.code_class = code_class
        code_set.append(code_element)
        code_snippet = ''

    diff_file.close()   

    #get diff snippets, correlated changed class and method
    try:
        diff_file2 = open(url,'r')
    except (Exception) as e:
        print (e)
        return

    diff_set = [] 
    changed_class = ''
    changed_method = ''
    add_snippet = ''
    add_flag = 0
    minus_snippet = ''
    minus_flag = 0
    for line in diff_file2:
        if line:
            line = line.strip('\n')
            if '@@' in line:
                line = line.split('@@')
                if len(line) >= 3:
                    changed_method = line[2]
            elif '+++' in line or '---' in line:
                if '/dev/null' not in line:
                    if 'test' in line:
                        changed_class = 'test'
                    else:
                        line = line.split('/')
                        changed_class = line[-1]
            else:
                if line[0] == '+':
                    line = line.replace('+','',1)
                    if add_flag == 0:
                        add_snippet = ''
                    if 'import' not in line:
                        add_snippet = add_snippet + line + '\n'                 
                    add_flag = 1
                elif line[0] == '-':
                    line = line.replace('-','',1)
                    if minus_flag == 0:
                        minus_snippet = ''
                    if 'import' not in line:
                        minus_snippet = minus_snippet + line + '\n'                 
                    minus_flag = 1
                else:
                    if add_flag == 1:
                        if add_snippet:
                            if changed_class != 'test':
                                add_element = add_diff_snippet(add_snippet,changed_class,'+',changed_method)
                                diff_set.append(add_element)
                    add_flag = 0
                    if minus_flag == 1:
                        if minus_snippet:
                            if changed_class != 'test':
                                minus_element = add_diff_snippet(minus_snippet,changed_class,'-',changed_method)
                                diff_set.append(minus_element)
                    minus_flag = 0
    #if file end with diffline
    if add_flag == 1:
        if add_snippet:
            if changed_class != 'test':
                add_element = add_diff_snippet(add_snippet,changed_class,'+',changed_method)
                diff_set.append(add_element)

    if minus_flag == 1:
        if minus_snippet:
            if changed_class != 'test':
                minus_element = add_diff_snippet(minus_snippet,changed_class,'-',changed_method)
                diff_set.append(minus_element)

    diff_file2.close()

    return code_set,diff_set

def diffSelection(url,configVariableList):
    
    diff = diff_file_parser(url)

    if diff:
        codeSet = diff[0]
        diffSet = diff[1]
    else:
        codeSet = 0
        diffSet = 0

    #Wheter a diff touches configuration file
    configFileTouched = False

    #Wheter a diff touches configuration load function
    configLoadTouched = False

    #Wheter a diff touches configuration set function
    configSetTouched = False

    #Wheter a diff touches configuration Variableeter
    configVariableTouched = False

    #whether a diff touches configuration message(log, error message)
    configMessageTouched = False

    #the set of touched file
    touchedFile = []

    #the set of touched configuration load function
    touchedLoadFunc = []

    #the set of touched configuration set function
    touchedSetFunc = []

    #the set of touched configuration Variable
    touchedVariable = []

    #the set of touched configuration message
    touchedMessage = []

    if codeSet and diffSet:

        #collect configuration variables in code snippet(not diff snippet)
        for codeElement in codeSet:
            configAssignObj = re.findall(HBASE_CONFIG_ASSIGN_RE,codeElement.code_snippet,re.M | re.I)
            if configAssignObj:
                for assignObj in configAssignObj:
                    collect_config_variable(assignObj,codeElement,configVariableList)

            sysParamAssignObj = re.findall(HBASE_SYS_PARAM_ASSIGN_FUNC_RE,codeElement.code_snippet,re.M | re.I)
            if sysParamAssignObj:
                for assignObj in sysParamAssignObj:
                    collect_config_variable(assignObj,codeElement,configVariableList)

        for diffElement in diffSet:

            #check whether diff touches config file
            configFileObj = re.findall(HBASE_CONFIG_FILE_RE,diffElement.diff_class,re.M | re.I)
            if configFileObj:
                configFileTouched = True
                for fileObj in configFileObj:
                    touchedFile.append(diffElement.diff_change_mode + fileObj)

            #check whether diff touches config load function
            configLoadObj = re.findall(HBASE_CONFIG_LOAD_FUNC_RE,diffElement.diff_snippet,re.M | re.I)
            if configLoadObj:
                for loadObj in configLoadObj:
                    loadObjStr = diffElement.diff_change_mode + loadObj.replace(' ','').replace('\n','')
                    if diffElement.diff_change_mode == '+':
                        reverseMode = '-'
                    else:
                        reverseMode = '+'
                    reverseFlag = False
                    for Func in touchedLoadFunc:
                        if Func == reverseMode + loadObj.replace(' ','').replace('\n',''):
                            touchedLoadFunc.remove(Func)
                            reverseFlag = True
                            break
                    if reverseFlag == False:
                        touchedLoadFunc.append(diffElement.diff_change_mode + loadObj.replace(' ','').replace('\n',''))

            sysParamLoadObj = re.findall(HBASE_SYS_PARAM_LOAD_FUNC_RE,diffElement.diff_snippet,re.M | re.I)
            if sysParamLoadObj:
                for loadObj in sysParamLoadObj:
                    loadObjStr = diffElement.diff_change_mode + loadObj.replace(' ','').replace('\n','')
                    if diffElement.diff_change_mode == '+':
                        reverseMode = '-'
                    else:
                        reverseMode = '+'
                    reverseFlag = False
                    for Func in touchedLoadFunc:
                        if Func == reverseMode + loadObj.replace(' ','').replace('\n',''):
                            touchedLoadFunc.remove(Func)
                            reverseFlag = True
                            break
                    if reverseFlag == False:
                        touchedLoadFunc.append(diffElement.diff_change_mode + loadObj.replace(' ','').replace('\n',''))
            
            
            #check whether diff touches config set function
            configSetObj = re.findall(HBASE_CONFIG_SET_FUNC_RE,diffElement.diff_snippet,re.M | re.I)
            if configSetObj:
                for setObj in configSetObj:
                    setObjStr = diffElement.diff_change_mode + setObj.replace(' ','').replace('\n','')
                    if diffElement.diff_change_mode == '+':
                        reverseMode = '-'
                    else:
                        reverseMode = '+'
                    reverseFlag = False
                    for Func in touchedSetFunc:
                        if Func == reverseMode + setObj.replace(' ','').replace('\n',''):
                            touchedSetFunc.remove(Func)
                            reverseFlag = True
                            break
                    if reverseFlag == False:
                        touchedSetFunc.append(diffElement.diff_change_mode + setObj.replace(' ','').replace('\n',''))

            sysParamSetObj = re.findall(HBASE_SYS_PARAM_SET_FUNC_RE,diffElement.diff_snippet,re.M | re.I)
            if sysParamSetObj:
                for setObj in sysParamSetObj:
                    setObjStr = diffElement.diff_change_mode + setObj.replace(' ','').replace('\n','')
                    if diffElement.diff_change_mode == '+':
                        reverseMode = '-'
                    else:
                        reverseMode = '+'
                    reverseFlag = False
                    for Func in touchedSetFunc:
                        if Func == reverseMode + setObj.replace(' ','').replace('\n',''):
                            touchedSetFunc.remove(Func)
                            reverseFlag = True
                            break
                    if reverseFlag == False:
                        touchedSetFunc.append(diffElement.diff_change_mode + setObj.replace(' ','').replace('\n',''))
            

            #check whether diff touches config related Variable
            for Variable in configVariableList:
                if Variable.variable_name in diffElement.diff_snippet and Variable.variable_class == diffElement.diff_class:
                    variableStr = diffElement.diff_change_mode + Variable.variable_name + ' ' + Variable.variable_class
                    if diffElement.diff_change_mode == '+':
                        reverseMode = '-'
                    else:
                        reverseMode = '+'
                    reverseFlag = False
                    for var in touchedVariable:
                        if var == reverseMode + Variable.variable_name + ' ' + Variable.variable_class:
                            touchedVariable.remove(var)
                            reverseFlag = True
                            break
                    if reverseFlag == False:
                        touchedVariable.append(variableStr)

            #check whether diff touches configuration message
            messageObj = re.findall(MESSAGE_RE,diffElement.diff_snippet,re.M | re.I)
            if messageObj:
                for messages in messageObj:
                    messages = messages.split('"')
                    for message in messages:
                        words = message.lower().split(" ")
                        if len(words) > 3:
                            if 'option' in words or 'parameter' in words or 'config' in message.lower():
                                configMessageTouched = True
                                touchedMessage.append(diffElement.diff_change_mode + message)


        if touchedLoadFunc != []:
            configLoadTouched = True

        if touchedSetFunc != []:
            configSetTouched = True

        if touchedVariable != []:
            configVariableTouched = True


        return configFileTouched,configLoadTouched,configSetTouched,configVariableTouched,configMessageTouched,touchedFile,touchedLoadFunc,touchedSetFunc,touchedVariable,touchedMessage
    
    else:
        return False





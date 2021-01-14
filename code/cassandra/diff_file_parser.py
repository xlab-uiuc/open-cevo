import re
import download_diff
from pathlib import Path

BASE_URL = "https://github.com/apache/cassandra/commit/"

#configFile/class in Cassandra
CASSANDRA_CONFIG_FILE_RE = ['cassandra.yaml', 'Config.java']

#RE for configuration param load in Cassandra
CASSANDRA_CONFIG_OPTION_LOAD_FUNC_RE = 'DatabaseDescriptor\.[a-zA-Z]+\(\)'

#RE for configuration param assign in Cassandra
CASSANDRA_CONFIG_OPTION_ASSIGN_FUNC_RE = '[a-zA-Z\.\_\-]+[\s]*=[\s]*[\n]*[\s]*' + CASSANDRA_CONFIG_OPTION_LOAD_FUNC_RE

#RE for configuraiton param set in Cassandra
CASSANDRA_CONFIG_OPTION_SET_FUNC_RE = 'DatabaseDescriptor.set[a-zA-Z]*\([^)^;]+\)'

#RE for class param load in Cassandra
CASSANDRA_CLASS_OPTION_LOAD_FUNC_RE = 'options\.get\([^;]+\)'

#RE for class param assign in Cassandra
CASSANDRA_CLASS_OPTION_ASSIGN_FUNC_RE = '[a-zA-Z\.\_\-]+[\s]*=[\s]*[\n]*[\s]*' + CASSANDRA_CLASS_OPTION_LOAD_FUNC_RE

#RE for class param set in Cassandra
CASSANDRA_CLASS_OPTION_SET_FUNC_RE = 'options.put\([^;]+\)'

#RE for system param load in Cassandra
CASSANDRA_SYS_PARAM_LOAD_FUNC_RE = '(?:System|Integer|Boolean|Long)\.get(?:Property|Integer|Boolean|Long)\([^;]+\)'

#RE for system param assign in Cassandra
CASSANDRA_SYS_PARAM_ASSIGN_FUNC_RE = '[a-zA-Z\.\_\-]+[\s]*=[\s]*[\n]*[\s]*' + CASSANDRA_SYS_PARAM_LOAD_FUNC_RE

#RE for system param set in Cassandra
CASSANDRA_SYS_PARAM_SET_FUNC_RE = 'System.setProperty\([^;]+\)'

#Message in source code
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

def add_diff_snippet(code_snippet, changed_class, change_mode, changed_method):
    code_element = DiffElement()
    code_element.diff_snippet = code_snippet
    code_element.diff_class = changed_class
    code_element.diff_change_mode = change_mode
    code_element.diff_method = changed_method
    return code_element

def collect_config_variable(assign_obj, code_element, config_variable_list):
    """collect variables that assgined by Cassandra configuration/system properties"""
    assign_obj = assign_obj.replace('\n', '').replace(' ', '').replace('this.', '')

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
                                add_element = add_diff_snippet(add_snippet, changed_class,'+',changed_method)
                                diff_set.append(add_element)
                    add_flag = 0
                    if minus_flag == 1:
                        if minus_snippet:
                            if changed_class != 'test':
                                minus_element = add_diff_snippet(minus_snippet, changed_class,'-',changed_method)
                                diff_set.append(minus_element)
                    minus_flag = 0
    #if file end with diffline
    if add_flag == 1:
        if add_snippet:
            if changed_class != 'test':
                add_element = add_diff_snippet(add_snippet, changed_class,'+',changed_method)
                diff_set.append(add_element)

    if minus_flag == 1:
        if minus_snippet:
            if changed_class != 'test':
                minus_element = add_diff_snippet(minus_snippet, changed_class,'-',changed_method)
                diff_set.append(minus_element)

    diff_file2.close()

    return code_set, diff_set

def diff_selection(url, config_variable_list):
    """Check whether the diff commit is configuration-related"""
    
    diff = diff_file_parser(url)

    if diff:
        code_set = diff[0]
        diff_set = diff[1]
    else:
        code_set = 0
        diff_set = 0

    #Whether a diff touches configuration file
    config_file_touched = False

    #Whether a diff touches configuration load
    config_load_touched = False

    #Whether a diff touches configuration set
    config_set_touched = False

    #Whether a diff touches configuration Variable
    config_variable_touched = False

    #whether a diff touches configuration message(log, error message)
    config_message_touched = False

    #the set of touched configuration file
    touched_config_file = []

    #the set of touched configuration load function(configuration option, class option, system parameter)
    touched_load_func = []

    #the set of touched configuration set function(configuration option, class option, system parameter)
    touched_set_func = []

    #the set of touched configuration variable
    touched_variable = []

    #the set of touched configuration message
    touched_message = []

    if code_set and diff_set:

        #collect configuration variables in code snippet(not diff snippet)
        for code_element in code_set:

            config_option_assign_obj = re.findall(CASSANDRA_CONFIG_OPTION_ASSIGN_FUNC_RE, code_element.code_snippet, re.M | re.I)
            if config_option_assign_obj:
                for assign_obj in config_option_assign_obj:
                    collect_config_variable(assign_obj, code_element, config_variable_list)

            class_option_assign_obj = re.findall(CASSANDRA_CLASS_OPTION_ASSIGN_FUNC_RE, code_element.code_snippet, re.M | re.I)
            if class_option_assign_obj:
                for assign_obj in class_option_assign_obj:
                    collect_config_variable(assign_obj, code_element, config_variable_list)

            sys_param_assign_obj = re.findall(CASSANDRA_SYS_PARAM_ASSIGN_FUNC_RE, code_element.code_snippet, re.M | re.I)
            if sys_param_assign_obj:
                for assign_obj in sys_param_assign_obj:
                    collect_config_variable(assign_obj, code_element, config_variable_list)

        #identify whether the diffs touch configuraton related code
        for diff_element in diff_set:

            #check whether diff touches config file
            for config_file in CASSANDRA_CONFIG_FILE_RE:
                if config_file == diff_element.diff_class:
                    config_file_touched = True
                    touched_config_file.append(config_file)

            #check whether diff touches config load function
            config_load_obj = re.findall(CASSANDRA_CONFIG_OPTION_LOAD_FUNC_RE, diff_element.diff_snippet, re.M | re.I)
            if config_load_obj:
                for load_obj in config_load_obj:
                    load_obj_str = diff_element.diff_change_mode + load_obj.replace(' ','').replace('\n','')
                    if diff_element.diff_change_mode == '+':
                        reverse_mode = '-'
                    else:
                        reverse_mode = '+'
                    reverse_flag = False
                    for func in touched_load_func:
                        if func == reverse_mode + load_obj.replace(' ','').replace('\n',''):
                            touched_load_func.remove(func)
                            reverse_flag = True
                            break
                    if reverse_flag == False:
                        touched_load_func.append(load_obj_str)

            #check whether diff touches config load function
            config_load_obj = re.findall(CASSANDRA_CLASS_OPTION_LOAD_FUNC_RE, diff_element.diff_snippet, re.M | re.I)
            if config_load_obj:
                for load_obj in config_load_obj:
                    load_obj_str = diff_element.diff_change_mode + load_obj.replace(' ','').replace('\n','')
                    if diff_element.diff_change_mode == '+':
                        reverse_mode = '-'
                    else:
                        reverse_mode = '+'
                    reverse_flag = False
                    for func in touched_load_func:
                        if func == reverse_mode + load_obj.replace(' ','').replace('\n',''):
                            touched_load_func.remove(func)
                            reverse_flag = True
                            break
                    if reverse_flag == False:
                        touched_load_func.append(load_obj_str)

            sys_param_load_obj = re.findall(CASSANDRA_SYS_PARAM_LOAD_FUNC_RE, diff_element.diff_snippet, re.M | re.I)
            if sys_param_load_obj:
                for load_obj in sys_param_load_obj:
                    load_obj_str = diff_element.diff_change_mode + load_obj.replace(' ','').replace('\n','')
                    if diff_element.diff_change_mode == '+':
                        reverse_mode = '-'
                    else:
                        reverse_mode = '+'
                    reverse_flag = False
                    for func in touched_load_func:
                        if func == reverse_mode + load_obj.replace(' ','').replace('\n',''):
                            touched_load_func.remove(func)
                            reverse_flag = True
                            break
                    if reverse_flag == False:
                        touched_load_func.append(load_obj_str)
            
            
            #check whether diff touches config set function
            config_set_obj = re.findall(CASSANDRA_CONFIG_OPTION_SET_FUNC_RE, diff_element.diff_snippet, re.M | re.I)
            if config_set_obj:
                for set_obj in config_set_obj:
                    set_obj_str = diff_element.diff_change_mode + set_obj.replace(' ','').replace('\n','')
                    if diff_element.diff_change_mode == '+':
                        reverse_mode = '-'
                    else:
                        reverse_mode = '+'
                    reverse_flag = False
                    for func in touched_set_func:
                        if func == reverse_mode + set_obj.replace(' ','').replace('\n',''):
                            touched_set_func.remove(func)
                            reverse_flag = True
                            break
                    if reverse_flag == False:
                        touched_set_func.append(set_obj_str)

            option_set_obj = re.findall(CASSANDRA_CLASS_OPTION_SET_FUNC_RE, diff_element.diff_snippet, re.M | re.I)
            if option_set_obj:
                for set_obj in option_set_obj:
                    set_obj_str = diff_element.diff_change_mode + set_obj.replace(' ','').replace('\n','')
                    if diff_element.diff_change_mode == '+':
                        reverse_mode = '-'
                    else:
                        reverse_mode = '+'
                    reverse_flag = False
                    for func in touched_set_func:
                        if func == reverse_mode + set_obj.replace(' ','').replace('\n',''):
                            touched_set_func.remove(func)
                            reverse_flag = True
                            break
                    if reverse_flag == False:
                        touched_set_func.append(set_obj_str)

            sys_param_set_obj = re.findall(CASSANDRA_SYS_PARAM_SET_FUNC_RE, diff_element.diff_snippet, re.M | re.I)
            if sys_param_set_obj:
                for set_obj in sys_param_set_obj:
                    set_obj_str = diff_element.diff_change_mode + set_obj.replace(' ','').replace('\n','')
                    if diff_element.diff_change_mode == '+':
                        reverse_mode = '-'
                    else:
                        reverse_mode = '+'
                    reverse_flag = False
                    for func in touched_set_func:
                        if func == reverse_mode + set_obj.replace(' ','').replace('\n',''):
                            touched_set_func.remove(func)
                            reverse_flag = True
                            break
                    if reverse_flag == False:
                        touched_set_func.append(set_obj_str)

            #check whether diff touches config related Variable
            for variable in config_variable_list:
                if variable.variable_name in diff_element.diff_snippet and variable.variable_class == diff_element.diff_class:
                    variable_str = diff_element.diff_change_mode + variable.variable_name + ' ' + variable.variable_class
                    if diff_element.diff_change_mode == '+':
                        reverse_mode = '-'
                    else:
                        reverse_mode = '+'
                    reverse_flag = False
                    for var in touched_variable:
                        if var == reverse_mode + variable.variable_name + ' ' + variable.variable_class:
                            touched_variable.remove(var)
                            reverse_flag = True
                            break
                    if reverse_flag == False:
                        touched_variable.append(variable_str)

            #check whether diff touches configuration message
            message_obj = re.findall(MESSAGE_RE, diff_element.diff_snippet, re.M | re.I)
            if message_obj:
                for messages in message_obj:
                    messages = messages.split('"')
                    for message in messages:
                        words = message.lower().split(" ")
                        if len(words) > 3:
                            if 'option' in words or 'parameter' in words or 'config' in message.lower():
                                message_str = diff_element.diff_change_mode + ' ' + message
                                if diff_element.diff_change_mode == '+':
                                    reverse_mode = '-'
                                else:
                                    reverse_mode = '+'
                                reverse_flag = False
                                for msg in touched_message:
                                    if msg == reverse_mode + ' ' + message:
                                        touched_message.remove(msg)
                                        reverse_flag = True
                                        break
                                if reverse_flag == False:
                                    touched_message.append(message_str)

        if touched_load_func != []:
            config_load_touched = True

        if touched_set_func != []:
            config_set_touched = True

        if touched_variable != []:
            config_variable_touched = True

        if touched_message != []:
            config_message_touched = True

        return config_file_touched, config_load_touched, config_set_touched, config_variable_touched, config_message_touched, touched_config_file, touched_load_func, touched_set_func, touched_variable, touched_message
    
    else:
        return False





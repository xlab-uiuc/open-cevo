#!/usr/bin/python

import time
import random
import threading

import extract_commit


class ConfigParam:
    def __init__(self):
        self.param_name = ''  #param name
        self.param_class = '' #class that this param belongs to 
        self.param_func = '' #function that assign this param

def main():
    config_variable_list = []
    searched_commit_num = 0

    commit_info_file = open('commit_info.txt','r')
    for commit_info in commit_info_file:
        commit_info = commit_info.strip('\n')
        extract_commit.extract(commit_info,config_variable_list)
        searched_commit_num = searched_commit_num + 1
        print (searched_commit_num)


if __name__ == '__main__':
    main()


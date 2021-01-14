#!/usr/bin/python

import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
import random
import os
from pathlib import Path

BASE_URL = "https://github.com"
DIFF_FILE_PATH = "/Users/zhangbuzhang/Desktop/diffs/Cassandra"
headers = [{"User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"},\
            {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
            {"User-Agent": "Mozilla/5.0 (Linux; X11)"},\
            {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5)"},\
            {'User-Agent':'node.js-v0.8.8'}]

#Download diff file of the commit
def download(url):
    commit_sha = url.split('/')
    commit_sha = commit_sha[-1]
    h = random.randint(0,4)
    diff_response = urlopen(url + '.diff')
    diff = diff_response.read().decode('UTF-8')
    diff_file = open(DIFF_FILE_PATH + '/' + commit_sha + '.diff', 'w')
    diff_file.write(diff)
    diff_file.close()

#Get all the information of the commit
def extract(url):

    url = BASE_URL + url
    
    try:
        c = random.randint(0,4)
        req = urllib.request.Request(url = url,headers = headers[c])
        commit_reponse = urlopen(req)
    except (Exception) as e:
        return

    soup = BeautifulSoup(commit_reponse.read(), features = "html.parser")

    commit_title = ''
    p_list = soup.find_all('p')
    for p in p_list:
        name = p.get('class')
        if name:
            if name[0] == 'commit-title':
                commit_title = p.text
    
    commit_description = ''
    div_list = soup.find_all('div')
    for div in div_list:
        name = div.get('class')
        if name:
            if name[0] == 'commit-desc':
                commit_description = div.text

    commit_time_tag = soup.find('relative-time')
    if commit_time_tag:
        commit_time = commit_time_tag.get('datetime')
        print (url) 
        print (commit_time)
    else:
        commit_time = 'commit_time_tag not exist'

    commit_sha = url.split('/')
    commit_sha = commit_sha[-1]
    commit_file = Path(DIFF_FILE_PATH + '/' + commit_sha + '.diff')
    if commit_file.is_file():
        print ("The diff file of " + commit_sha + " is already downloaded")
    else:
        commit_info_file = open('commit_info.txt','a')
        commit_info_file.write(url + '$$$' + commit_title.replace('\n','').strip() + commit_description.replace('\n','').strip() + '$$$' + commit_time + '\n')
        commit_info_file.close()
        try:
            download(url)
        except (Exception) as e:
            print (e)
            return
        
            
    
            

    


#!/usr/bin/python

import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
import http.client
import time
import random
import threading

import download_diff


def get_commits(url,searched_commit_num):
    headers = [{"User-Agent": "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)"},\
            {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
            {"User-Agent": "Mozilla/5.0 (Linux; X11)"},\
            {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.5)"},\
            {'User-Agent':'node.js-v0.8.8'}]
    try:
        c = random.randint(0,4)
        req = urllib.request.Request(url=url,headers=headers[c])
        response = urlopen(req)
    except (Exception) as e:
        print (e)
        time.sleep(60)
    soup = BeautifulSoup(response.read(), features = "html.parser")
    a_list = soup.find_all('a')
    commit_list = []
    older_href = ''
    for a in a_list:
        data = a.get('data-pjax')
        if data:
            if data == 'true':
                href = a.get('href')
                if href not in commit_list:
                    commit_list.append(href)
        if a.text == 'Older':
            older_href = a.get('href')

    for commit in commit_list:
        searched_commit_num = searched_commit_num + 1
        try:
            while threading.activeCount() > 25:
                #print threading.activeCount()
                pass
            t = threading.Thread(target = download_diff.extract, args = (commit,))
            t.start()
        except (Exception) as e:
            print ("multiprocessing error")
            print (e.message)
        interval = random.uniform(1,2)
        time.sleep(interval)

#    print (older_href)
    file = open('download_log.txt','a')
    file.write(older_href + '\n')
    file.write("Already downloaded " + str(searched_commit_num) + " commits." + '\n')
    print ("Already downloaded " + str(searched_commit_num) + " commits.")
    file.close()
    out = open('commit_url.txt','w')
    out.write(older_href)
    out.close()

    get_commits(older_href,searched_commit_num)


def main():
    #change the file(commit_url.txt) to get other software's commits
    fin = open('commit_url.txt','r')
    url = fin.readline()
    fin.close()

    searched_commit_num = 0

    try:
        get_commits(url,searched_commit_num)
    except (Exception) as e:
        print (e)


if __name__ == '__main__':
    http.client.HTTPConnection._http_vsn = 10  
    http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
    main()


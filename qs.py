#!/usr/bin/env python
#coding:utf-8
'''
For summary all jobs through qstat command
'''

import os
import sys
import psutil
from collections import defaultdict
from commands import getstatusoutput

def style(string, mode = '', fore = '', back = ''):
    STYLE = {
    'fore':{'black':30,'red':31,'green':32,'yellow':33,'blue':34,'purple':35,'cyan':36,'white':37},
    'back':{'black':40,'red':41,'green':42,'yellow':43,'blue':44,'purple':45,'cyan':46,'white':47},
    'mode':{'mormal':0,'bold':1,'underline':4,'blink':5,'invert':7,'hide':8},
    'default':{'end':0},
    }
    mode  = '%s' % STYLE["mode"].get(mode,"")
    fore  = '%s' % STYLE['fore'].get(fore,"")
    back  = '%s' % STYLE['back'].get(back,"")
    style = ';'.join([s for s in [mode, fore, back] if s])
    style = '\033[%sm' % style if style else ''
    end   = '\033[%sm' % STYLE['default']['end'] if style else ''
    return '%s%s%s' % (style, string, end)
    
def main():
    has_qstat = True if getstatusoutput('command -v qstat')[0] == 0 else False
    username = os.environ["USER"]
    if has_qstat:
        alljobs = os.popen("qstat -u \* | grep -P '^\d'").read().strip().split("\n")
        jobs = {}
        for j in alljobs:
            j = j.split()
            jobs.setdefault(j[3],defaultdict(int))[j[4]] += 1
        print style("-"*47,mode="bold")
        print style("{0:<20} {1:>8} {2:>8} {3:>8}".format("user","jobs","run","queue"),mode="bold")
        print style("-"*47,mode="bold")
        for u in sorted(jobs.items(),key=lambda x:sum(x[1].values()),reverse=True):
            user = u[0]
            job = sum(u[1].values())
            run = u[1]["r"]
            qw = u[1]["qw"]
            if user == username:
                print style("{0:<20} {1:>8} {2:>8} {3:>8}".format(user,job,run,qw),fore="red",mode="bold")
            else:
                print style("{0:<20} {1:>8} {2:>8} {3:>8}".format(user,job,run,qw))
        print style("-"*47,mode="bold")
    else:
        users = map(lambda x:os.path.basename(x),os.popen('ls -d /home/*').read().split())
        allpids = psutil.pids()
        jobs = {}
        for p in allpids:
            try:
                j = psutil.Process(p)
                if j.username() not in users:
                    continue
                jobs.setdefault(j.username(),defaultdict(int))[j.status()] += 1
            except:
                continue                
        print style("-"*52,mode="bold")
        print style("{0:<20} {1:>7} {2:>5} {3:>5} {4:>5} {5:>5}".format("user","process","R","S","D","Z"),mode="bold")
        print style("-"*52,mode="bold")
        for u in sorted(jobs.items(),key=lambda x:sum(x[1].values()),reverse=True):
            user = u[0]
            job = sum(u[1].values())
            if user == username:
                print style("{0:<20} {1:>7} {2:>5} {3:>5} {4:>5} {5:>5}".format(user,job,u[1].get("running",0),u[1].get("sleeping",0),u[1].get("dead",0),u[1].get("zombie",0)),fore="red",mode="bold")
            else:
                print style("{0:<20} {1:>7} {2:>5} {3:>5} {4:>5} {5:>5}".format(user,job,u[1].get("running",0),u[1].get("sleeping",0),u[1].get("dead",0),u[1].get("zombie",0)))
        print style("-"*52,mode="bold")
        
if __name__ == "__main__":
    main()
    

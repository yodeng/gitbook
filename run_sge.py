#!/usr/bin/env python
#coding:utf-8
#### 投递任务，将任务散播到集群SGE,并等待所有任务执行完成时退出。

import sys,os,time
import argparse
from subprocess import call,PIPE
from threading import Thread
from Queue import Queue

def not_empty(s):
  return s and s.strip() and (not s.strip().startswith("#"))

def parserArg():
    pid = os.getpid()
    parser = argparse.ArgumentParser(description= "For qsub your jobs in a job file.")
    parser.add_argument("-q","--queue",type=str,help="the queue your job running, default: baseline.q",default="baseline.q",metavar="queue")
    parser.add_argument("-m","--memory",type=int,help="the memory used per command (GB), default: 1",default=1,metavar="int")
    parser.add_argument("-c","--cpu",type=int,help="the cpu numbers you job used, default: 1",default=1,metavar="int")
    parser.add_argument("-wd","--workdir",type=str,help="work dir, default: %s"%os.path.abspath(os.getcwd()),default=os.path.abspath(os.getcwd()),metavar="workdir")
    parser.add_argument("-N","--jobname",type=str,help="job name",metavar="jobname")
    parser.add_argument("-o","--logdir",type=str,help="the output log dir",metavar="logdir")
    parser.add_argument("-n","--num",type=int,help="the max job number runing at the same time. default: all in you job file",metavar="int")
    parser.add_argument("-b","--block",action="store_true",default=False,help="if passed, block when submitted you job, default: off")
    parser.add_argument("jobfile",type=str,help="the input jobfile")
    progargs = parser.parse_args()
    if progargs.logdir is None:
        progargs.logdir = os.path.join(os.path.abspath(os.path.dirname(progargs.jobfile)),"qsub.out."+os.path.basename(progargs.jobfile))
    if not os.path.isdir(progargs.logdir):
        os.makedirs(progargs.logdir)
    if progargs.jobname is None:
        progargs.jobname = os.path.basename(progargs.jobfile) + "_" + str(pid) if not os.path.basename(progargs.jobfile)[0].isdigit() else "job_" + os.path.basename(progargs.jobfile) + "_" +  str(pid)
    else:
        #progargs.jobname += "_" + str(pid)
        pass
    with open(progargs.jobfile) as fi:
        allcmds = fi.readlines()
    allcmds = filter(not_empty,allcmds)
    progargs.alljobs = len(allcmds)
    if progargs.num is None:
        progargs.num = progargs.alljobs
    return progargs                 
           
def qsubCheck(jobname,num,block,sec = 1):
    # pid = os.getpid()
    while flag:
        time.sleep(sec)   ### check per 1 seconds
        qs = 0
        # qs = os.popen('qstat | grep %s | wc -l'%jobname[:10]).read().strip()
        qs = os.popen('qstat -xml | grep %s | wc -l'%jobname).read().strip()
        qs = int(qs)
        if 0 < qs < num and (not block):
            [q.put(qs) for _ in range(num-qs)]
        elif qs == 0 and block:
            [q.put(qs) for _ in range(num)]
        else:
            continue              
    
def main():
    args = parserArg()
    jobnums = 0
    jobfile = args.jobfile   
    global q,flag
    q = Queue()
    flag = True
    with open(jobfile) as fi:
        for n,line in enumerate(fi):
            line = line.strip()
            if line and not line.startswith("#"):
                logfile = os.path.join(args.logdir,os.path.basename(jobfile)+".line") + str(n+1) +".log"
                with open(logfile,"w") as logcmd:
                    logcmd.write(line+"\n")
                cmd = 'qsub -q %s -wd %s -N %s -o %s -j y -l vf=%dg,p=%d <<< "%s"'%(args.queue,
                    args.workdir,args.jobname,logfile,args.memory,args.cpu,line
                )
                call(cmd,shell = True,stdout=PIPE)
                jobnums += 1
                if jobnums == args.num:
                    if args.alljobs == args.num:
                        flag = False
                    break                    
        else:
            flag = False
        if flag:
            p = Thread(target=qsubCheck,args=(args.jobname,args.num,args.block))
            p.setDaemon(True)
            p.start()
        while flag:
            try:
                line = fi.next()
                n += 1
                op = q.get(block=True,timeout=1080000)   # 300 hours
            except StopIteration:
                flag = False
                break
            except:
                continue
            line = line.strip()
            if line and not line.startswith("^#"):
                logfile = os.path.join(args.logdir,os.path.basename(jobfile)+".line") + str(n+1) +".log"
                with open(logfile,"w") as logcmd:
                    logcmd.write(line+"\n")
                cmd = 'qsub -q %s -wd %s -N %s -o %s -j y -l vf=%dg,p=%d <<< "%s"'%(args.queue,
                    args.workdir,args.jobname,logfile,args.memory,args.cpu,line
                )            
                call(cmd,shell = True,stdout=PIPE)
                # jobnums += 1 
    time.sleep(1)
    while True:
        time.sleep(2)   ### check per 1 seconds            
        qs = os.popen('qstat -xml | grep %s | wc -l'%args.jobname).read().strip()
        qs = int(qs)
        if qs == 0:
            # '''
            # 此处可添加操作，所有任务完成之后进行的处理可写在这部分
            # '''            
            break  
    return
                    
if __name__ == "__main__":
    main()



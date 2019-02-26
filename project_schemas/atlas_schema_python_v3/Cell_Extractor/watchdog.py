#!/usr/bin/env python3

from os.path import isfile,getmtime
from glob import glob
from time import sleep,time
from os import system
from subprocess import Popen,PIPE
import sys

sys.path.append('/home/ubuntu/shapeology_code/scripts')

from lib.utils import *

config = configuration(os.environ['yaml'])
params=config.getParams()

scripts_dir=params['paths']['scripts_dir']

local_data=params['paths']['data_dir']
script='process_file.py'
exec_dir=params['paths']['exec_dir']

def runPipe(command):
    print('cmd=',command)
    p=Popen(command.split(),stdout=PIPE,stderr=PIPE)
    L=p.communicate()
    stdout=L[0].decode("utf-8").split('\n')
    stderr=L[1].decode("utf-8").split('\n')
    return stdout,stderr

def run(command,out):
    print('cmd=',command,'out=',out)
    outfile=open(out,'w')
    Popen(command.split(),stdout=outfile,stderr=outfile)

def Last_Modified(file_name):
    try:
        mtime = getmtime(file_name)
    except OSError:
        mtime = 0
    return(mtime)

if __name__=='__main__':
    Recent=False
    for logfile in glob(exec_dir+'/Controller*.log'):
        gap=time() - Last_Modified(logfile)
        if gap <120: # allow 2 minute idle
            print(logfile,'gap is %6.1f'%gap)
            Recent=True
            break
    if(not Recent):
        # Check that another 'controller' is not running
        stdout,stderr = runPipe('ps aux')
        Other_controller=False
        for line in stdout:
            if 'PopulateExtractedCells.py' in line:
                Other_controller=True
                break
        
        if Other_controller:
            print('Other PopulateExtractedCells.py is running')
        else:
            command='python3 {0}/PopulateExtractedCells.py'.format(exec_dir)
            output='{0}/logs/Controller-{1}.log'.format(exec_dir,int(time()))
            print('about to run',command,'withoutput=',output)
            run(command,output)

            # Controller.py [-h] scripts_dir script s3location local_data

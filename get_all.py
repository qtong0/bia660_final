from subprocess import call
import os.path,subprocess
import time

def run(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    return p

states = ["New_Jersey"]
cities = ["Hoboken"]

#echo ${#cities[@]}

if not os.path.exists("output"):
    os.makedirs("output")

search_what = "--term='restaurants'"
max_row = "--maxrow=20"
#for city,state in zip(cities,states):
off = 1
retrive_max = 2000
for off in range(1,retrive_max,20):
    loc = "--location="+"hoboken"
    writeto = "--writeto=output/"+"nj"+"_1"
    offset = "--offset="+str(off)
    cmd = "./main.py" + \
          " " + loc +             \
          " " + search_what +     \
          " " + max_row +         \
          " " + writeto +         \
          " " + str(off)
    print cmd
    #result = run(cmd)
    p = subprocess.Popen(["./main.py",offset,loc,search_what,max_row,writeto], stdout=subprocess.PIPE)
    p.wait()
    time.sleep(5)


#python 2 version
#terminal running: python2 txt2analysis.py [-i inputdir]
#[] means optional
#if not state -i, then use default value
import sys

import re
import glob

def main():
    c=0;total=0
    for file in file_list:
        with open(file,'r') as f:
            for line in f:
                if line !="\n":
                    total+=1
                line=line.replace("\n","")
                # a=re.findall("^As [an|a|the]+[A-Za-z0-9,;:_.()*<>@#$%&/'\"\\s-]+[.?!]$",line)
                a=re.findall("^As [an|a|the]+.+,? ?I.+",line)
                if len(a)==1 and a[0] is line:
                    print(line)
                    c+=1

    print ("total number of sentences is "+str(total))
    print ("matched number of sentences is "+str(c))
    print ("pattern percentage is "+str((float(c)/total)*100)+"%") #python2 needs float


if __name__=="__main__":
    if len(sys.argv)==3:#python2 txt2analysis.py -i inputdir
        inputdir=sys.argv[2]
    elif len(sys.argv)==1:#python2 txt2analysis.py
        pp=sys.argv[0] #this is "path/txt2analysis.py"
        nn=pp.split("/")[-1] #"txt2analysis.py"
        path=pp.replace(nn,'') #get the path of txt2analysis.py 
        inputdir=path+"/"
    else:
        print ("Please retry command. Format is python2 txt2analysis.py -i inputdir.")

    file_list=glob.glob(inputdir+"/"+"*.txt") #all txt files in a directory
    #"/" needed, when user does not type "/" after inputdir name
    #if user types "/", not matter because "//" function same as "/"
    
    #print file_list    
    main()

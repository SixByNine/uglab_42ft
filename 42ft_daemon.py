#!/usr/bin/env python
import datetime
import os
import subprocess
import urllib.request
import urllib.parse
import signal
import time
import process_one_observation


def run():
    go=True
    print("START")
    count=0
    while go:
        check_index()
        check_for_jobs()
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            go=False


def check_for_jobs():
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    check_url="http://psrweb.jb.man.ac.uk/lab/42ft/get_jobs.php"
    done_url="http://psrweb.jb.man.ac.uk/lab/42ft/done_job.php"
    with urllib.request.urlopen(check_url, context=ctx) as req:
        for line in req.readlines():
            e=line.decode().split()
            date=e[0]
            ut=e[1]
            psr=e[2]
            job_id=e[3]
            fname = process_one_observation.process_one_observation(psr,date,ut)
            print(fname)
            rsync_cmd=["rsync",fname,"ugweb:public_html/42ft/data/"]
            print(" ".join(rsync_cmd))
            subprocess.call(rsync_cmd)
            jid=urllib.parse.quote(job_id)
            print(done_url+"?jid="+jid)
            rr = urllib.request.urlopen(done_url+"?jid="+jid,context=ctx)
            

def check_index():
    try:
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime("index.txt"))
        age = datetime.datetime.now() - mtime
    except FileNotFoundError:
        age=datetime.timedelta(days=100)
    print("index age:",age)
    if age > datetime.timedelta(seconds=600):
        make_index()

def make_index(ndays=60):
    print("Rebuild index...")
    nidx=0
    today = datetime.date.today()
    rootdir="/vraid1/psrdata/cobra2"
    with open("index.txt","w") as f:

        for i in range(ndays):
            d = today-datetime.timedelta(days=i)
            day=d.strftime("%Y%m%d")
            daydir=os.path.join(rootdir,day)
            try:
                for pdir in os.listdir(daydir):
                    try:
                        e=pdir.split("_")
                        psr=e[1]
                        ut=e[0]
                        #print(day,ut,psr)
                        print(day,ut,psr,file=f)
                        nidx+=1
                    except Exception as e:
                        print(e)
                        continue
            except Exception as e:
                print(e)
                continue

    print("rsync index")
    rsync_cmd=["rsync","index.txt","ugweb:public_html/42ft/"]
    subprocess.call(rsync_cmd)
    print("Indexed {} observations".format(nidx))

if __name__ == "__main__":
    run()

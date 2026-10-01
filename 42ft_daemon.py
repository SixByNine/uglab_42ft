#!/usr/bin/env python
import datetime
import os
import pathlib
import subprocess
import sys
import urllib.request
import urllib.parse
import signal
import time

SCRIPT_DIR = pathlib.Path(__file__).parent.resolve()
CACHE_DIR = os.path.join(SCRIPT_DIR,"cache")


def run():
    go=True
    print("START")
    while go:
        check_index()
        check_for_jobs()
        try:
            time.sleep(10)
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
            try:
                process_job(date,ut,psr)
            except Exception as ex:
                print("Error processing job {}: {}".format(job_id,ex))
            jid=urllib.parse.quote(job_id)
            print(done_url+"?jid="+jid)
            rr = urllib.request.urlopen(done_url+"?jid="+jid,context=ctx)


def process_job(date,ut,psr):
    uid="{}_{}_{}".format(date,ut,psr)
    os.makedirs(CACHE_DIR,exist_ok=True)
    script=os.path.join(SCRIPT_DIR,"process_one_observation.py")
    result = subprocess.run(
        [sys.executable,script,"--psr",psr,"--date",date,"--utc",ut],
        capture_output=True,text=True)
    print(result.stdout)
    print(result.stderr,file=sys.stderr)

    if result.returncode != 0:
        print("Processing failed for {} (returncode {})".format(uid,result.returncode))
        mark_failed(uid)
        return

    outfname=None
    data_type=None
    for resline in result.stdout.splitlines():
        if resline.startswith("RESULT "):
            parts=resline.split()
            outfname=parts[1]
            data_type=parts[2]
    if outfname is None or not os.path.exists(outfname):
        print("Processing reported success but no output found for {}".format(uid))
        mark_failed(uid)
        return

    rsync_cmd=["rsync",outfname,"ugweb:public_html/42ft/data/"]
    print(" ".join(rsync_cmd))
    subprocess.call(rsync_cmd)

    type_file=os.path.join(CACHE_DIR,"{}.type".format(uid))
    with open(type_file,"w") as f:
        f.write(data_type)
    rsync_cmd=["rsync",type_file,"ugweb:public_html/42ft/data/{}.type".format(uid)]
    print(" ".join(rsync_cmd))
    subprocess.call(rsync_cmd)


def mark_failed(uid):
    failed_file=os.path.join(CACHE_DIR,"{}.failed".format(uid))
    with open(failed_file,"w") as f:
        f.write("Processing failed\n")
    rsync_cmd=["rsync",failed_file,"ugweb:public_html/42ft/data/{}.failed".format(uid)]
    print(" ".join(rsync_cmd))
    subprocess.call(rsync_cmd)
            

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

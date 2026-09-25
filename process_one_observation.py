#!/usr/bin/env python

import psrchive
import numpy as np
import os
import sys
import pathlib
import argparse
import datetime
import tempfile
from astropy.time import Time
import subprocess

def process_one_observation(psr,d,ut):
    root="/vraid1/psrdata/cobra2"
    cache=os.path.join(pathlib.Path(__file__).parent.resolve(),"cache")
    dname="{}_{}".format(ut,psr)
    path = os.path.join(root,d,dname)
    print(path)
    fp_fn="{}_{}_{}.cln".format(d,ut,psr)
    inf=os.path.join(path,fp_fn)
    if not os.path.exists(inf):
        fp_fn="{}_{}_{}.ar".format(d,ut,psr)
        inf=os.path.join(path,fp_fn)
    if not os.path.exists(inf):
        fp_fn="{}_{}_{}.clng".format(d,ut,psr)
        inf=os.path.join(path,fp_fn)
    if not os.path.exists(inf):
        print("Can't find observation")
    print(inf)
    fp_ar = psrchive.Archive.load(inf)
    #fp_ar.dedisperse()
    fp_ar.pscrunch()
    print("tscrunch by a factor of 10")
    fp_ar.tscrunch(10)
    fp_ar.remove_baseline()
    print("Out subints:",len(fp_ar))
    orig_period=get_period(fp_ar,round=None)
    
    ephfile = set_approx_ephemeris(psr,d,fp_ar)
    if ephfile is not None:
        print("Using ephemeris file {}".format(ephfile))
        fp_ar.set_ephemeris(ephfile)
    fp_ar.unload(os.path.join(cache,fp_fn))
    data = fp_ar.get_data()
    print(data.shape)
    data = data[:,0,:,:] ## Remove polarisation dimension

    nsub,nchan,nbin=data.shape
    mjds = fp_ar.get_mjds()
    cfreq = fp_ar.get_centre_frequency()
    bw = fp_ar.get_bandwidth()
    freqs = (np.arange(nchan)-nchan/2+0.5)*(bw/nchan)+cfreq
    approx_period=get_period(fp_ar)
    header=print_header(fp_ar)
    print(header)
    src=fp_ar.get_source()

    outfname=os.path.join(cache,"{}_{}_{}.npz".format(d,ut,psr))
    np.savez(outfname,times=mjds,freqs=freqs,cfreq=cfreq,bw=bw,data=data,approx_period=approx_period,header=header,source_name=src)
    with open(os.path.join(cache,"{}_{}_{}.txt".format(d,ut,psr)),"w") as f:
        print(print_header(fp_ar),file=f)
        print("Original period: {}".format(orig_period),file=f)
    return outfname


def get_period(ar,round=9):
    f0 = float(ar.get_ephemeris().get_value("F0").replace("D","E"))
    f1 = float(ar.get_ephemeris().get_value("F1").replace("D","E"))
    f2str = ar.get_ephemeris().get_value("F2").replace("D","E")
    try:
        f2 = float(f2str)
    except:
        f2=0
    pepoch = float(ar.get_ephemeris().get_value("PEPOCH").replace("D","E"))

    obsepoch = (ar.start_time().in_days() + ar.end_time().in_days())/2.0
    x = (obsepoch - pepoch)*86400.0
    spinfreq_correct = f0+f1*x+f2*x**2
    if round is None:
        return 1.0/spinfreq_correct
    else:
        return np.round(1.0/spinfreq_correct,round)



def set_approx_ephemeris(psr,d,ar):
    """
    For specific pulsars, i.e. the crab B0531+21, we install an ephemeris that is fixed for the duration of the lab expeiremnt.
    """
    if psr=="B0531+21":

        # determine the reference epoch from observation date 'd' which is in format YYYYMMDD.
        # Reference epoch depends on the date ranges, based on teaching semesters.
        # Semester 1 (Sep 1 to Nov 30)  = Saturday closest to Nov 1.
        # Semester 2 (Feb 1 to Apr 30) = Saturday closest to Mar 7.
        # These dates may need to be adjusted.
        # Intra-semester Dec-Jan is Jan 1
        # May-June is Jun 1
        # July-Aug is Aug 1

        year = int(d[0:4])
        month = int(d[4:6])

        def closest_saturday(target):
            # Saturday.weekday() == 5
            diff = (5 - target.weekday()) % 7
            if diff > 3:
                diff -= 7
            return target + datetime.timedelta(days=diff)

        if month in (9,10,11):
            # Semester 1.
            ref_date = closest_saturday(datetime.date(year,11,1))
            description=f"Sem1_{year}"
        elif month in (2,3,4):
            # Semester 2.
            ref_date = closest_saturday(datetime.date(year,3,7))
            description=f"Sem2_{year}"
        elif month == 12:
            # Dec belongs to the semester-1 cohort, so reference the following Jan 1.
            ref_date = datetime.date(year+1,1,1)
            description=f"DecJan_{year+1}"
        elif month == 1:
            ref_date = datetime.date(year,1,1)
            description=f"DecJan_{year}"
        elif month in (5,6):
            description=f"MayJun_{year}"
            ref_date = datetime.date(year,6,1)
        elif month in (7,8):
            description=f"JulAug_{year}"
            ref_date = datetime.date(year,8,1)
        else:
            raise ValueError("Unrecognised month '{}' in date '{}'".format(month,d))

        ref_mjd = Time(ref_date.isoformat()).mjd

        int_mjd=int(ref_mjd)
        ephdir=os.path.join(pathlib.Path(__file__).parent.resolve(),"temp_ephemerides")
        ephfile=os.path.join(ephdir,"{}_{}_{}.par".format(psr,int_mjd,description))
        os.makedirs(ephdir,exist_ok=True)
        if not os.path.exists(ephfile):
            print("Creating ephemeris file for {} at {}".format(psr,ephfile))

            f0 = float(ar.get_ephemeris().get_value("F0").replace("D","E"))
            f1 = float(ar.get_ephemeris().get_value("F1").replace("D","E"))
            f2str = ar.get_ephemeris().get_value("F2").replace("D","E")
            try:
                f2 = float(f2str)
            except:
                f2=0
            pepoch = float(ar.get_ephemeris().get_value("PEPOCH").replace("D","E"))

            x = (int_mjd - pepoch)*86400.0
            new_f0 = f0+f1*x+f2*x**2
            tmpfile=os.path.join(ephdir,"{}_{}_{}.tmp".format(psr,int_mjd,description))

            ar.get_ephemeris().unload(tmpfile)
            with open(tmpfile,"r") as f, open(ephfile,"w") as eph:
                for line in f:
                    if line.startswith("F0"):
                        eph.write("F0             {:.16e}\n".format(new_f0))
                    elif line.startswith("F1"):
                        eph.write("F1             {:.12e}\n".format(0.0))
                    elif line.startswith("F2"):
                        eph.write("F2             {:.12e}\n".format(0.0))
                    elif line.startswith("F"):
                        continue
                    else:
                        eph.write(line)
            os.remove(tmpfile)
        return ephfile
    else:
        return None




def print_header(ar):
    ret=[]
    def pprint(key,val):
        return "{:30s}: {}".format(key,val)

    ret.append(pprint("Filename",os.path.basename(ar.get_filename())))
    ret.append(pprint("Source Name",ar.get_source()))
    ret.append(pprint("Number of channels",ar.get_nchan()))
    ret.append(pprint("Number of phase bins",ar.get_nbin()))
    ret.append(pprint("Number of sub-integrations",ar.get_nsubint()))
    ret.append(pprint("Centre Freq (MHz)",ar.get_centre_frequency()))
    ret.append(pprint("Bandwidth (MHz)",ar.get_bandwidth()))
    ret.append(pprint("Integration Time (s)",ar.integration_length()))
    ret.append(pprint("Telescope",ar.get_telescope()))
    return "\n".join(ret)



if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Process one observation')
    parser.add_argument("--psr","-p",required=True)
    parser.add_argument("--date","-d",required=True)
    parser.add_argument("--utc","-u",required=True)
    args = parser.parse_args()
    process_one_observation(args.psr,args.date,args.utc)

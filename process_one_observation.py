#!/usr/bin/env python

import psrchive
import numpy as np
import os
import sys
import pathlib
import argparse

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

    fp_ar.unload(os.path.join(cache,fp_fn))
    data = fp_ar.get_data()
    print(data.shape)
    data = data[:,0,:,:] ## Remove polarisation dimension

    nsub,nchan,nbin=data.shape
    mjds = fp_ar.get_mjds()
    cfreq = fp_ar.get_centre_frequency()
    bw = fp_ar.get_bandwidth()
    freqs = (np.arange(nchan)-nchan/2+0.5)*(bw/nchan)+cfreq
    approx_period=get_approx_period(fp_ar)
    header=print_header(fp_ar)
    print(header)
    src=fp_ar.get_source()

    outfname=os.path.join(cache,"{}_{}_{}.npz".format(d,ut,psr))
    np.savez(outfname,times=mjds,freqs=freqs,cfreq=cfreq,bw=bw,data=data,approx_period=approx_period,header=header,source_name=src)
    return outfname


def get_approx_period(ar):
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
    timeperturn = 1.5*3600.0
    return np.round(1.0/(spinfreq_correct+1.0/timeperturn),9)

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

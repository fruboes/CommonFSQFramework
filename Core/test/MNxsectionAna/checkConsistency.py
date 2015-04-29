#! /usr/bin/env python
import ROOT
ROOT.gROOT.SetBatch(True)

import glob
import sys

sample2type2cnt = {}

for f in glob.glob("*.root"):
    if f.count("_") == 1 : continue
    spl = f.split("_")
    anaType = spl.pop(1)
    spl.pop(0)
    sample = "_".join(spl).replace(".root", "")

    sample2type2cnt.setdefault(sample, {})
    try:
        infile = ROOT.TFile(f) 
        histSkim = infile.Get(sample+"/CFFEventsSeenSkim")
        histProof = infile.Get(sample+"/CFFEventsSeenProof")
        #print anaType, sample, hist.GetBinContent(1)
        cnt = histProof.GetBinContent(1)
        cntFromSkim = histSkim.GetBinContent(2)
        if cnt != cntFromSkim:
            print "Warning - different events seen by tree producer and py analyzer:", cntFromSkim, cnt, "(r =", cntFromSkim/cnt, ")"
            print "   (",sample, anaType,  ")"

        
        sample2type2cnt[sample][anaType]=cnt
    except:
        print "Some problem with", anaType, sample


allAnaTypes = set(reduce(list.__add__, [sample2type2cnt[s].keys() for s in sample2type2cnt]))
#print allAnaTypes

for s in sample2type2cnt:
    typesForThisSample = set(sample2type2cnt[s].keys())
    if len(allAnaTypes-typesForThisSample) != 0:
        print "Warning - missing ana for", s, "-", " ".join(allAnaTypes-typesForThisSample)

    cnts = [sample2type2cnt[s][t] for t in sample2type2cnt[s]]
    cntsSet = set(cnts)
    if len(cntsSet)>1 or len(cntsSet)==1 and list(cntsSet)[0]==0:
        print "Problem: ", s, " ".join(map(str,cntsSet))
        for tt in sample2type2cnt[s]:
            print "    ",tt, sample2type2cnt[s][tt], cnts.count(sample2type2cnt[s][tt])



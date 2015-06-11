#!/usr/bin/env python

import ROOT
ROOT.gROOT.SetBatch(True)
from ROOT import *

import os,re,sys,math

import CommonFSQFramework.Core.Util
import CommonFSQFramework.Core.Style

from array import array

from optparse import OptionParser

ROOT.gSystem.Load("libRooUnfold.so")
from HistosHelper import getHistos


from mnDraw import DrawMNPlots 

optionsReg = {}

def getPrettyName(v):
    ret = ""
    if v.startswith("MN"):
        ret += "M.N. like, "
    elif v.startswith("Incl"):
        ret += "Inclusive, "

    dd = {  "Asym" : "asymetric",
           "Basic" : "basic",
          "Window" : "window"}

    for  d in dd:
        if v.endswith(d): return ret + dd[d]

def compareVariants(name, variants, mc):
    histos = {}
    for v in variants:
        histos[v] = getHistos("plotsMNxs_{}.root".format(v))

    c = ROOT.TCanvas()
    extractedGenHistos = {}
    for v in variants:
        gen = histos[v][mc]["detaGen_central_jet15"].Clone()
        gen.SetDirectory(0)
        gen2 = histos[v][mc]["detaGen_central_dj15fb"]
        gen.Add(gen2)
        extractedGenHistos[v] = gen

    hmax = max([h.GetMaximum() for h in extractedGenHistos.itervalues()])*1.07
    first = True
    colors = [46, 8, 9]
    cnt = 0
    xOff = 0.45
    leg = ROOT.TLegend(0.2+xOff, 0.35, 0.5+xOff, 0.5)
    mc = "Pythia6" if "Pyth" in name else "Herwig++"
    mc += " MC:"
    leg.SetHeader(mc)

    for v in extractedGenHistos:
        extractedGenHistos[v].SetMaximum(hmax)
        if first:
            first = False
            extractedGenHistos[v].Draw("H")
            extractedGenHistos[v].GetXaxis().SetTitle(DrawMNPlots.xLabels()["xs"])
            extractedGenHistos[v].GetYaxis().SetTitleOffset(1.8)
            extractedGenHistos[v].GetYaxis().SetTitle(DrawMNPlots.yLabels()["xsAsPB"])
        else:
            extractedGenHistos[v].Draw("H SAME")

        color = colors[cnt]
        cnt += 1 
        extractedGenHistos[v].SetMarkerColor(color)
        extractedGenHistos[v].SetLineColor(color)
        leg.AddEntry(extractedGenHistos[v], getPrettyName(v), "l")

    ROOT.gPad.SetTopMargin(0.095)
    #from mergeUnfoldedResult import getExtra, nextFreeLine
    #extra = getExtra(variant, isSim=True)
    #extra["insteadOfPreliminary"] = "simulations"
    #DrawMNPlots.banner(extra)
    leg.Draw("SAME")

    c.Print(optionsReg["odir"]+"/" + name+ ".png")
    DrawMNPlots.toPDF(c, optionsReg["odir"]+"/" + name+ ".pdf")


def main():
    CommonFSQFramework.Core.Style.setTDRStyle()

    variantsIncl = ["InclusiveAsym",
    "InclusiveBasic",
    "InclusiveWindow"]
    variantsMN = ["MNAsym",
    "MNBasic",
    "MNWindow"]

    odir = "~/tmp/compareVariants/"
    os.system("mkdir -p "+odir)
    global optionsReg
    optionsReg["odir"] = odir

    herwig = "QCD_Pt-15to1000_TuneEE3C_Flat_7TeV_herwigpp"
    pythia = "QCD_Pt-15to3000_TuneZ2star_Flat_HFshowerLibrary_7TeV_pythia6"
    
    compareVariants("mnHerw", variantsMN, herwig)
    compareVariants("inclHerw", variantsIncl, herwig)
    compareVariants("mnPyth", variantsMN, pythia)
    compareVariants("inclPyth", variantsIncl, pythia)

if __name__ == "__main__":
    # note http://indico.cern.ch/event/107747/session/1/material/slides/1?contribId=72, s.19
    main()


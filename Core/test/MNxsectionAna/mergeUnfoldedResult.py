#!/usr/bin/env python
import ROOT
ROOT.gROOT.SetBatch(True)

from HistosHelper import getHistos

from CommonFSQFramework.Core.DrawPlots import DrawPlots

import  CommonFSQFramework.Core.Style

from mnDraw import DrawMNPlots 
from array import array
from optparse import OptionParser
import math

import sys, os
def getRivetName(variant, normalization):
    from do import todoCatAll
    if len(todoCatAll) != 6:
        raise Exception("Error: inconsistent number of categories in todoCatAll")
    rivetNum = todoCatAll.index(variant)+1
    if "area" == normalization:
        rivetNum += 10
    numAsStr = str(rivetNum)
    if len (numAsStr) == 1:
        numAsStr = "0"+numAsStr

    rivetName = "d"+numAsStr+"-x01-y01"
    print normalization, rivetNum, rivetName
    return rivetName

def getHistoFromYoda(yodaFile, histoName):
    y2a = "/cvmfs/cms.cern.ch/slc6_amd64_gcc481/external/yoda/1.3.0-cms/bin/yoda2aida"
    a2r = "/cvmfs/cms.cern.ch/slc6_amd64_gcc481/external/rivet/1.8.2-cms8/bin/aida2root"
    os.system(y2a+ " "+ yodaFile + " /tmp/rivetImport.aida")
    os.system(a2r+ " /tmp/rivetImport.aida")
    f = ROOT.TFile("rivetImport.root")
    for i in xrange(1,4):
        hh = f.Get(histoName+";"+str(i))
        axMax =  hh.GetXaxis().GetXmax() 
        if axMax > 9 and axMax < 10:
            break

    h = hh.Clone()
    h.SetDirectory(0)
    return h

def nextFreeLine(extra):
    for i in xrange(0,5):
        name = "line"+str(i)
        if name not in extra:return name
    return None

def getExtra(variant, isSim = False):    
    extra = {}
    j1t = 35
    j2t = 35
    if variant.endswith("Asym"):
        j2t = 45
    if variant.endswith("Window"):
        j2t = 55


    #extra["afterLumi"] = ",\,\\mathrm{p^{jet1}_T>"+str(j1t)+"\,GeV}" 
    #extra["afterLumi"] += ",\,\\mathrm{p^{jet2}_T>"+str(j2t)+"\,GeV}"
        
    if isSim:
        extra["insteadOfPreliminary"] = "simulations"
    else:
        extra["insteadOfPreliminary"] = "preliminary"

    if not isSim:
        #extra[nextFreeLine(extra)] = "5.36\,\\mathrm{pb}^{-1}\,(7\,\\mathrm{TeV})"
        extra[nextFreeLine(extra)] = "5.4\,\\mathrm{pb}^{-1}\,(7\,\\mathrm{TeV})"

    cur = nextFreeLine(extra)
    extra[cur] = "\,\\mathrm{p^{jet1}_T>"+str(j1t)+"\,GeV}" 
    extra[cur] += ",\,\\mathrm{p^{jet2}_T>"+str(j2t)+"\,GeV}"
    if variant.endswith("Window"):
        extra[nextFreeLine(extra)] = ",\,\\mathrm{"+str(j1t)+"\,GeV<p^{jet1,jet2}_T<"+str(j2t)+"\,GeV}"

    #extra["bottomLeft"] = "Inclusive"
    #if variant.startswith("MN"):
    #    extra["bottomLeft"] = "Mueller-Navelet like"
    selType = "\\mathrm{inclusive~analysis}"
    if variant.startswith("MN"):
       selType  = "\\mathrm{M.-N.~like~analysis}"

    extra["selType"] = selType

    #extra["afterLumi"]+= ", "+selType
    extra[nextFreeLine(extra)] = selType
    return extra

def main():
    CommonFSQFramework.Core.Style.setTDRStyle()


    parser = OptionParser(usage="usage: %prog [options] filename",
                            version="%prog 1.0")

    parser.add_option("-v", "--variant",   action="store", dest="variant", type="string", \
                                help="choose analysis variant")
    parser.add_option("-n", "--normalization",   action="store", dest="normalization", type="string", \
                                help="how should I normalize the plots?")
    parser.add_option("-b", "--normalizeToBinWidth",   action="store_true", dest="normalizeToBinWidth")
    parser.add_option("-s", type="float", dest="scaleExtra")   

    (options, args) = parser.parse_args()
    scaleExtra = 1.
    if options.scaleExtra:
        scaleExtra = 1./options.scaleExtra

    normalizeToBinWidth = False
    if options.normalizeToBinWidth:
        normalizeToBinWidth = True

    if not options.variant:
        print "Provide analysis variant"
        sys.exit()

    if not options.normalization:
        print "Provide normalization variant"
        sys.exit()

    norms = ["xs", "area"]
    if options.normalization not in norms:
        print "Normalization not known. Possible choices: " + " ".join(norms)
        sys.exit()



    (options, args) = parser.parse_args()
    if not options.variant:
        print "Provide analysis variant"
        sys.exit()

    indir = "~/tmp/unfolded_{}/".format(options.variant)
    #oodir = indir.replace("/unfolded_", "/merged_")
    oodir = indir
    import os
    os.system("mkdir -p "+ oodir)
    histofile = "plotsMNxs_{}.root".format(options.variant)


    lumiUncertainty = 0.04
    herwigIn=indir+"/mnxsHistos_unfolded_herwigOnData.root"
    pythiaIn=indir+"/mnxsHistos_unfolded_pythiaOnData.root"
    ofileName = indir+"/mnxsHistos_unfolded_onData_merged.root"


    histos = {}
    histos["herwig"]=getHistos(herwigIn)
    histos["pythia"]=getHistos(pythiaIn)
    #print histos["herwig"]["_jet15"].keys()
    #sys.exit()
    # TODO: test that dirs have the same contents

    # ['xsunfolded_central_jet15', 'xsunfolded_jecDown_jet15', 'xs_central_jet15', 'xsunfolded_jerDown_jet15', 'xsunfolded_jecUp_jet15', 'xsunfolded_jerUp_jet15']
    finalSet = {}

    todo = ["_jet15", "_dj15fb"]
    #todo = ["_jet15"]
    for t in todo:
        finalSet[t] = {}
        for hName in histos["herwig"][t]:
            if hName.startswith("xs_"): continue # skip detector level histogram
            if hName.startswith("chi2scan"): continue 

            hAvg = histos["herwig"][t][hName].Clone()

            hAvg.Add(histos["pythia"][t][hName])
            hAvg.Scale(0.5)
            finalSet[t][hName]=hAvg

            # add herwig/pythia central histo as variations
            #  in case we would have more than two MC - for every MC
            #   add a central value as "up" variation, as a "down"
            #   variation use the averaged histogram
            #    this way we have consistent list of up/down variations,
            #    where the down variation doesnt enlarge uncertainty band
            if "_central_" in hName:
                newNameHerwig = hName.replace("_central_", "_modelUp_")
                newNamePythia = hName.replace("_central_", "_modelDown_")
                finalSet[t][newNameHerwig] = histos["herwig"][t][hName].Clone(newNameHerwig)
                finalSet[t][newNamePythia] = histos["pythia"][t][hName].Clone(newNamePythia)

                # at the same point - use the averaged histogram to add lumi uncertainy
                #  BTW: should we do it here??
                newNameAvgUp = hName.replace("_central_", "_lumiUp_")
                newNameAvgDown = hName.replace("_central_", "_lumiDown_")
                finalSet[t][newNameAvgUp] = hAvg.Clone(newNameAvgUp)
                finalSet[t][newNameAvgDown] = hAvg.Clone(newNameAvgDown)
                finalSet[t][newNameAvgUp].Scale(1.+lumiUncertainty)
                finalSet[t][newNameAvgDown].Scale(1.-lumiUncertainty)



    # add jet15 and dj15 histos
    # note: histo binning should be the same from beginning!
    finalSet["merged"] = {}
    for t in finalSet["_jet15"]:
        newName = t.replace("_jet15", "_jet15andDJ15FB")
        finalHisto = finalSet["_jet15"][t].Clone(newName)
        finalHisto.Add(finalSet["_dj15fb"][t.replace("_jet15", "_dj15fb")].Clone())
        if options.normalization == "area":
            finalHisto.Scale(1./finalHisto.Integral())
        if normalizeToBinWidth:
            finalHisto.Scale(1., "width")

        finalHisto.Scale(scaleExtra)

        finalSet["merged"][newName] = finalHisto
            



    # save all to file
    ofile = ROOT.TFile(ofileName, "RECREATE")
    for dirName in finalSet:
        odir = ofile.mkdir(dirName)
        for h in finalSet[dirName]:
            odir.WriteTObject(finalSet[dirName][h])


    # make final plot, including uncertainty band
    central = [ finalSet["merged"][hName] for hName in finalSet["merged"].keys() if "_central_" in hName ]
    if len(central) != 1:

        raise Exception("Error: {} central histo(s) found: ".format(len(central))+ " ".join([ h.GetName() for h in central  ]))
    central = central[0]
    central.GetXaxis().SetTitle("#Delta#eta")
    unit = "[pb]"
    oneOverN = ""
    if options.normalization == "area":
        #unit = "[a.u.]"
        unit = ""
        oneOverN = "#frac{1}{N} "

    if normalizeToBinWidth:
        central.GetYaxis().SetTitle(oneOverN+"#frac{d#sigma}{d(#Delta#eta)} "+unit)
    else:
        central.GetYaxis().SetTitle(oneOverN+"#sigma "+unit)

    uncert  = [finalSet["merged"][hName] for hName in finalSet["merged"].keys() if "_central_" not in hName ]


    uncResult= DrawPlots.getUncertaintyBand(uncert, central)
    unc = uncResult["band"]

    uncertaintySplitUp = {}
    uncertaintySplitUp["total"] = unc

    # interulde - make plot of single  uncertainty contributions
    variations =  list(set([v.split("_")[1].replace("Up","").replace("Down","") \
                        for v in  finalSet["merged"].keys() if  "_central_" not in v]))

    toyMCDone = False
    for v in variations:
        isToyMC = v.startswith("toyMC")
        if not isToyMC:
            partialUncertHistos = [finalSet["merged"][hName] for hName in finalSet["merged"].keys() if "_"+v  in hName ]
        else: # here we want to have just one entry for all toyMC variations
            if toyMCDone: continue
            toyMCDone = True
            partialUncertHistos = [finalSet["merged"][hName] for hName in finalSet["merged"].keys() if "_"+"toyMC"  in hName ]
            v = "toyMC"

        if not isToyMC and len(partialUncertHistos) != 2 or isToyMC and len(partialUncertHistos) != 6:
            raise Exception("Found wrong ({})number of uncertainties for {}".format(len(partialUncertHistos), v)  )
        partialUncert = DrawPlots.getUncertaintyBand(partialUncertHistos, central)["band"]
        uncertaintySplitUp[v] = partialUncert


    cc = ROOT.TCanvas()
    cc.SetCanvasSize(cc.GetWw()*2, cc.GetWh())
    #cc.SetTopMargin(0.1)

    cc.Divide(1,2)
    cc.cd(1)
    split = 0.9
    margin = 0.005
    ROOT.gPad.SetPad(.005, split+margin, .995, .995)
    cc.cd(2)
    ROOT.gPad.SetPad(.005, .005, .995, split)
    cur=cc.cd(1)

    # warning: brainfuck.
    fr = cur.DrawFrame(0,0,1,1)
    fr.SetAxisColor(0,"X")
    fr.SetAxisColor(0,"Y")
    fr.GetXaxis().SetLabelColor(0)
    fr.GetYaxis().SetLabelColor(0)
    latexCMS = ROOT.TLatex()
    latexCMS.SetNDC()
    latexCMS.SetTextAlign(31) 
    latexCMS.SetTextFont(42)
    latexCMS.SetTextSize(0.5)
    #print labels["lumi"]
    labels = getExtra(options.variant)
    norm = ",\,"+labels["selType"].replace("~","\,") 
    
    if options.normalization == "xs":
        norm += ",\,\\mathrm{cross\,section}"
    else:
        norm += ",\,\\mathrm{shape}"

    latexCMS.DrawLatex( 1-cur.GetRightMargin(), 0.15, labels["line0"]+norm)
    latexCMS.SetTextAlign(11) 
    #latexCMS.DrawLatex( 0.08, 0.15, "\\mathrm{CMS}\,"+labels["preliminary"])
    latexCMS.DrawLatex( 0.025, 0.15, "\\mathrm{CMS}\,"+labels["insteadOfPreliminary"])

    cur.Update()


    #ROOT.gPad.SetPad(.005, 0.05+0.1, .995, .995-0.1)
    # GetWh
    #cc.SetCanvasSize(cc.GetWw(), int(cc.GetWh()*1.3))
    todoVar = sorted(uncertaintySplitUp.keys())
    todoVar.remove("total")
    #todoVar.insert(0, "total") # plot first
    #cc.Divide(1,len(todoVar))
    padsCC = cc.cd(2)
    padsCC.Divide(2, (len(todoVar)+1)/2)
    gcFix = []
    prettyNames = {}
    prettyNames["jec"] = "JEC"
    prettyNames["jer"] = "JER"
    prettyNames["lumi"] = "lumi"
    prettyNames["model"] = "model dep."
    prettyNames["pu"] = "PU"
    prettyNames["toyMC"] = "MC stat."

    for i,v in enumerate(todoVar):
        yUp = array('d')
        yDown = array('d')
        x = array('d')
        y = array('d')
        xDown = array('d')
        xUp = array('d')
        padsCC.cd(i+1)
        print i,v
        for iPoint in xrange(uncertaintySplitUp[v].GetN()):
            totalUp = uncertaintySplitUp["total"].GetErrorYhigh(iPoint)
            totalDown = uncertaintySplitUp["total"].GetErrorYlow(iPoint)
            partUp = uncertaintySplitUp[v].GetErrorYhigh(iPoint)
            partDown = uncertaintySplitUp[v].GetErrorYlow(iPoint)
            #rUp, rDown = (1.,1.)
            rUp, rDown = (0.,0.)
            if totalUp > 0: rUp = partUp/totalUp
            if totalDown > 0: rDown = partDown/totalDown
            x.append(uncertaintySplitUp["total"].GetX()[iPoint])
            #y.append(1)
            y.append(0)
            #print iPoint, uncertaintySplitUp["total"].GetX()[iPoint], totalUp, totalDown, partUp, partDown, "|", rUp, rDown
            xDown.append(uncertaintySplitUp["total"].GetErrorXlow(iPoint))
            xUp.append(uncertaintySplitUp["total"].GetErrorXhigh(iPoint))
            yUp.append(rUp)
            yDown.append(rDown)
        uncRatio =     ROOT.TGraphAsymmErrors(len(x), x, y, xDown, xUp, yDown, yUp)
        frame = ROOT.gPad.DrawFrame(central.GetXaxis().GetXmin(), -1.1, central.GetXaxis().GetXmax(), 1.1)
        frame.GetYaxis().SetNdivisions(505)
        frame.GetXaxis().SetTitle(central.GetXaxis().GetTitle())
        frame.GetYaxis().SetTitle("#frac{#sigma_{"+prettyNames[v]+"}}{#sigma_{total}}")
        frame.GetXaxis().SetTitleOffset(3)
        frame.GetYaxis().SetTitleOffset(2)
        frame.Draw()
        ROOT.gPad.SetBottomMargin(0.2)
        ROOT.gPad.SetGridy()
        DrawPlots.uniformFont(frame)
        gcFix.append(uncRatio)
        #uncRatio.SetFillStyle(3001);
        uncRatio.SetFillColor(ROOT.kOrange-2)
        uncRatio.SetLineColor(ROOT.kOrange-2)
        uncRatio.Draw("2SAME")
        frame.Draw("AXIS SAME")
        #uncRatio.Draw("A2")
        #uncertaintySplitUp[v].Draw("2SAME")
        #uncertaintySplitUp[v].Draw("A2")
        #print i,v

    cc.Print(oodir+"/unc_{}.png".format(options.normalization))
    DrawMNPlots.toPDF(cc, oodir+"/unc_{}.pdf".format(options.normalization))

    #%%c.cd(1)
    #sys.exit()


        
    # get GEN level distributions
    histosFromPyAnalyzer = getHistos(histofile)
    herwigDir = "QCD_Pt-15to1000_TuneEE3C_Flat_7TeV_herwigpp"
    pythiaDir =  "QCD_Pt-15to3000_TuneZ2star_Flat_HFshowerLibrary_7TeV_pythia6"
    genHistoHerwig = histosFromPyAnalyzer[herwigDir]["detaGen_central_jet15"].Clone()
    genHistoHerwig.Add(histosFromPyAnalyzer[herwigDir]["detaGen_central_dj15fb"])
    genHistoPythia = histosFromPyAnalyzer[pythiaDir]["detaGen_central_jet15"].Clone()
    genHistoPythia.Add(histosFromPyAnalyzer[pythiaDir]["detaGen_central_dj15fb"])

    if options.normalization == "area":
        map(lambda h: h.Scale(1./h.Integral()), [genHistoPythia, genHistoHerwig] )
    if normalizeToBinWidth:
        map(lambda h: h.Scale(1, "width"), [genHistoPythia, genHistoHerwig] )
    map(lambda h: h.Scale(scaleExtra), [genHistoPythia, genHistoHerwig] )

    rivetName = getRivetName(options.variant, options.normalization)
    hej =  getHistoFromYoda("fromRivet/hej_hepmc-jets-jetptmin=25-extraptmin=20-CT10nlo_Job_merged.yoda", rivetName)
    powheg = getHistoFromYoda("fromRivet/powheg-jets-sqrts=7000-kt5-herapdf-CUETP8-herapdf-P0-rivet2_merged.yoda", rivetName)

    maxima = []
    maxima.append(uncResult["max"])
    for t in [unc, central, genHistoHerwig, genHistoPythia, hej, powheg]:
        maxima.append(t.GetMaximum())



    minima = []
    minima.append(uncResult["min"])
    for t in [unc, central, genHistoHerwig, genHistoPythia, hej, powheg]:
        maxima.append(t.GetMinimum())

    c = ROOT.TCanvas()

    c.Divide(1,2)
    c.cd(1)
    split = 0.2
    margin = 0.005
    ROOT.gPad.SetPad(.005, split+margin, .995, .995)
    c.cd(2)
    ROOT.gPad.SetPad(.005, .005, .995, split)
    c.cd(1)

    ROOT.gPad.SetTopMargin(0.1)
    #c.SetRightMargin(0.07)
    central.SetMaximum(max(maxima)*1.05)
    #unc.SetFillColor(17);
    unc.SetFillColor(ROOT.kOrange-2)
    unc.SetLineColor(ROOT.kOrange-2)

    DrawPlots.uniformFont(central)
    central.Draw()
    #central.GetXaxis().SetRangeUser(5,8)
    #central.GetYaxis().SetRangeUser(0,250000)

    central.GetYaxis().SetTitleOffset(2.2)
    central.GetXaxis().SetTitleOffset(1.2)
    unc.Draw("2SAME")
    central.Draw("SAME")
    central.SetMarkerStyle(20)
    central.SetMarkerSize(1)

    genHistoHerwig.Draw("SAME HIST")
    genHistoHerwig.SetLineColor(2)
    genHistoHerwig.SetMarkerColor(2)
    #genHistoHerwig.SetMarkerStyle(20)
    genHistoHerwig.SetLineWidth(3)

    genHistoPythia.Draw("SAME HIST")
    genHistoPythia.SetLineColor(4)
    genHistoPythia.SetMarkerColor(4)
    #genHistoPythia.SetMarkerStyle(21)
    genHistoPythia.SetLineWidth(3)


    print DrawMNPlots.banner(getExtra(options.variant))

    hej.Draw("SAME HIST")
    powheg.Draw("SAME HIST")

    hej.SetLineWidth(3)
    hej.SetLineColor(8)
    hej.SetMarkerColor(3)

    powheg.SetLineWidth(3)
    powheg.SetLineColor(ROOT.kMagenta+1)
    powheg.SetMarkerColor(6)

    ROOT.gStyle.SetLineStyleString(11, "10 15")
    ROOT.gStyle.SetLineStyleString(12, "20 20")
    ROOT.gStyle.SetLineStyleString(13, "40 20")
    
    genHistoPythia.SetLineStyle(13)
    powheg.SetLineStyle(12)
    hej.SetLineStyle(11)



    legendX2 = 1- ROOT.gPad.GetRightMargin()-0.02
    #print "XXX", legendX2
    legendWidth = 0.2
    legendX1 = legendX2-legendWidth
    legendHeight = 0.35

    legend = ROOT.TLegend(legendX1, ROOT.gPad.GetBottomMargin()+0.1, \
                          legendX2, ROOT.gPad.GetBottomMargin()+0.1+legendHeight  )
    legend.SetFillColor(0)
    legend.AddEntry(central, "data", "pel")
    legend.AddEntry(unc, "syst. unc.", "f")
    #genHistoHerwig.SetLineStyle(9)

    legend.AddEntry(genHistoHerwig, DrawMNPlots.prettyMCName("herwig"), "l")
    legend.AddEntry(genHistoPythia, DrawMNPlots.prettyMCName("pythia"), "l")
    legend.AddEntry(powheg, DrawMNPlots.prettyMCName("powheg"), "l")
    legend.AddEntry(hej, DrawMNPlots.prettyMCName("hej"), "l")
    legend.Draw("SAME")    

    c.cd(2)
    ROOT.gPad.SetTopMargin(0.)
    ROOT.gPad.SetBottomMargin(0.4)
    frame = ROOT.gPad.DrawFrame(central.GetXaxis().GetXmin(), 0, central.GetXaxis().GetXmax(), 3)
    DrawPlots.uniformFont(frame)
    frame.GetYaxis().SetNdivisions(505)
    frame.GetYaxis().SetTitle("#frac{MC}{data}")
    frame.GetYaxis().SetTitleOffset(2.2)
    frame.GetXaxis().SetTitleOffset(5)
    frame.GetXaxis().SetTitle(central.GetXaxis().GetTitle())
    #frame.GetXaxis().SetRangeUser(5,8)

    yUp = array('d')
    yDown = array('d')
    x = array('d')
    y = array('d')
    xDown = array('d')
    xUp = array('d')

    y4Rivet = array('d')
    yUp4Rivet = array('d')
    yDown4Rivet = array('d')
    for iBin in xrange(1, central.GetNbinsX()+1):
        val =  central.GetBinContent(iBin)
        if val == 0: continue

        if val != 0:
            binErr  = central.GetBinError(iBin)
            errUp = unc.GetErrorYhigh(iBin-1)
            errDown =  unc.GetErrorYlow(iBin-1)
            valDown = errDown/val
            valUp =   errUp/val
            yDown.append(valDown)
            yUp.append(valUp)
            valDown4Rivet = math.sqrt(errDown*errDown + binErr*binErr  )
            valUp4Rivet   = math.sqrt(errUp*errUp + binErr*binErr  )
            yUp4Rivet.append(valUp4Rivet)
            yDown4Rivet.append(valDown4Rivet)
            #print valDown, valUp
        else:
           yUp.append(0)
           yDown.append(0)
        #print 
        x.append(unc.GetX()[iBin-1])
        y.append(1)
        ratio = unc.GetY()[iBin-1]/val
        if max(ratio-1., 1.-ratio)>0.001:
            raise Exception("Expected equal values")

        y4Rivet.append(val)
        xDown.append(unc.GetErrorXlow(iBin-1))
        xUp.append(unc.GetErrorXhigh(iBin-1))

    #print type(x)
    uncRatio =     ROOT.TGraphAsymmErrors(len(x), x, y, xDown, xUp, yDown, yUp)
    result4Rivet = ROOT.TGraphAsymmErrors(len(x), x, y4Rivet, xDown, xUp, yDown4Rivet, yUp4Rivet)

    #uncRatio = ROOT.TGraphAsymmErrors(len(x), x, y, xDown, xUp, yDown, yUp)

    #uncRatio.SetFillStyle(3001)
    #uncRatio.SetFillColor(17)
    uncRatio.SetFillColor(ROOT.kOrange-2)
    uncRatio.SetLineColor(ROOT.kOrange-2)
    uncRatio.Draw("2SAME")


    centralRatio = central.Clone()
    centralRatio.Divide(central)
    centralRatio.Draw("SAME")

    herwigRatio = genHistoHerwig.Clone()
    herwigRatio.Divide(central)

    pythiaRatio = genHistoPythia.Clone()
    pythiaRatio.Divide(central)

    hejRatio = hej.Clone()
    powhegRatio = powheg.Clone()
    hejRatio.Divide(central)
    powhegRatio.Divide(central)


    herwigRatio.Draw("SAME L")
    pythiaRatio.Draw("SAME L")
    powhegRatio.Draw("SAME L")
    hejRatio.Draw("SAME L")



    frame.Draw("AXIS SAME")

    DrawMNPlots.toPDF(c,  oodir+"/mergedUnfolded_{}.pdf".format(options.normalization))
    c.Print(oodir+"/mergedUnfolded_{}.png".format(options.normalization))
    c.cd(1)
    ROOT.gPad.SetLogy()
    central.SetMaximum(max(maxima)*1.5)
    central.SetMinimum(min(minima)*0.7)
    legend.SetX1NDC(0.02 + ROOT.gPad.GetLeftMargin())
    legend.SetX2NDC(0.02 + ROOT.gPad.GetLeftMargin()+legendWidth)
    legend.SetY1NDC(0.02 + ROOT.gPad.GetBottomMargin())
    legend.SetY2NDC(0.02 + ROOT.gPad.GetBottomMargin()+legendHeight)
    c.Print(oodir+"/mergedUnfolded_{}_log.png".format(options.normalization))
    DrawMNPlots.toPDF(c,  oodir+"/mergedUnfolded_{}_log.pdf".format(options.normalization))


    # rivet export

    rivet = ROOT.TFile("toRivet.root", "RECREATE")
    rivetName = getRivetName(options.variant, options.normalization)


    rivet.WriteTObject(result4Rivet, rivetName)
    rivet.Close()
    del rivet

    import os
    r2f = "/cvmfs/cms.cern.ch/slc6_amd64_gcc481/external/rivet/1.8.2-cms8/bin/root2flat"
    if not os.path.isfile(r2f):
        raise Exception("Cannot find root2flat. Rivet export failed")

    os.system(r2f + " toRivet.root")

    import yoda
    analysisobjects = yoda.readFLAT(rivetName+".dat")
    #print type(analysisobjects)
    #print analysisobjects.keys()
    for k in analysisobjects:
        pth = "/CMS_2015_FWD071/"+rivetName
        #print dir(analysisobjects[k])
        #analysisobjects[k].setTitle(pth)
        #analysisobjects[k].setPath(pth)
        analysisobjects[k].setAnnotation("Title", pth)
        analysisobjects[k].setAnnotation("Path",  pth)

    yoda.writeYODA(analysisobjects, rivetName+".yoda")



    # /cvmfs/cms.cern.ch/slc6_amd64_gcc481/external/rivet/1.8.2-cms8/bin/root2flat


if __name__ == "__main__":
    main()


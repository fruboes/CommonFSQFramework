#!/usr/bin/env python

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gSystem.Load("libRooUnfold.so")

import os,re,sys,math

import CommonFSQFramework.Core.Util
import CommonFSQFramework.Core.Style

from CommonFSQFramework.Core.DrawPlots import DrawPlots

from array import array


from optparse import OptionParser

class DrawMNPlots(DrawPlots):

    # warning: duplicated code for lumi calculation: see unfoldMN.py
    def getLumi(self, target, samples): # override
        if "data_" not in target:
            raise Exception("getLumi called for "+ target )

        spl = target.split("_")
        if len(spl) < 1:
            raise Exception("Cannot extract trigger name from " + target)

        trg = spl[-1]
        triggersToSamples = {} # TODO make accessible from self
        triggersToSamples["jet15"] = ["Jet-Run2010B-Apr21ReReco-v1", "JetMETTau-Run2010A-Apr21ReReco-v1", "JetMET-Run2010A-Apr21ReReco-v1"]
        triggersToSamples["dj15fb"] = ["METFwd-Run2010B-Apr21ReReco-v1", "JetMETTau-Run2010A-Apr21ReReco-v1", "JetMET-Run2010A-Apr21ReReco-v1"]

        if trg not in triggersToSamples.keys():
            raise Exception("Dont know how to get lumi for "+ trg + ". Known triggers are " + " ".join(triggersToSamples.keys()))

        triggerToKey = {}
        triggerToKey["jet15"] = "lumiJet15"
        triggerToKey["dj15fb"] = "lumiDiJet15FB"

        sampleList=CommonFSQFramework.Core.Util.getAnaDefinition("sam")
        #print "-----"
        lumi = 0.
        for s in samples:
            #print s
            if s in triggersToSamples[trg]:
                lumiKeyName = triggerToKey[trg]
                lumi += sampleList[s][lumiKeyName]
                #print " lumi->",lumi

        return lumi

    def getTarget(self, histoName, sampleName): # override
        ''' target naming convention:
                - name should consist of two parts separated by underscore

                - part after underscore should contain your trigger label
                -- e.g. dj15fb (which for 2010 MN XS analysis coresponds to
                   HLT_DoubleJet15_ForwardBackward and HLT_DoubleJet15_ForwardBackward_v3)

                - part before underscore should start with string "data" or "MC"
                -- to distinguish different MC use descriptive names eg MCqcd or MCdymumu
        '''
        sampleList=CommonFSQFramework.Core.Util.getAnaDefinition("sam")

        trgSplt = histoName.split("_")
        if len(trgSplt) < 1:
            raise "Cannot extract trigger name from" , histoName
        triggerName =  trgSplt[-1]

        isData = sampleList[sampleName]["isData"]
        retName = None
        if not isData:
            retName = "MC_" + triggerName
        else:
            triggersToSamples = {} # TODO make accessible from self
            triggersToSamples["jet15"] = ["Jet-Run2010B-Apr21ReReco-v1", "JetMETTau-Run2010A-Apr21ReReco-v1", "JetMET-Run2010A-Apr21ReReco-v1"]
            triggersToSamples["dj15fb"] = ["METFwd-Run2010B-Apr21ReReco-v1", "JetMETTau-Run2010A-Apr21ReReco-v1", "JetMET-Run2010A-Apr21ReReco-v1"]
            triggersToSamples["sum"] = []

            if sampleName in triggersToSamples[triggerName]:
                retName = "data_" + triggerName

        return retName

    def applyScale(self, histoName, sampleName): # override
        if histoName.startswith("balance"): return False
        return True

    def setGlobalStyle(self):  # override
        CommonFSQFramework.Core.Style.setTDRStyle()

    @staticmethod
    def prettyMCName(mc):
        if mc == "pythia": return "Pythia6"
        if mc == "herwig": return "Herwig++"
        if mc == "hej": return "HEJ"
        if mc == "powheg": return "POWHEG"

        raise Exception("Unkown mc: "+mc)
        

    @staticmethod
    def banner(extra={}, draw=True):
        ret = {}
        latexCMS = ROOT.TLatex()
        latexCMS.SetNDC()
        # consistent with
        # https://ghm.web.cern.ch/ghm/plots/MacroExample/CMS_lumi.h
        latexCMS.SetTextFont(61)
        latexCMS.SetTextAlign(31) 
        cmsTextSize      = 0.75
        t = ROOT.gPad.GetTopMargin()
        b = ROOT.gPad.GetBottomMargin()

        r = ROOT.gPad.GetRightMargin()
        l = ROOT.gPad.GetLeftMargin()
        #t,b,r,l = (0,0,0,0)

        #text = "\\rm \\mathcal{L}=5.36 pb^{-1}, \\sqrt{s}=7 TeV"
        #text = "\\rm 5.36 pb^{-1} (\\sqrt{s}=7 TeV)"
        #text = "\\int L=5.36\,\\mathrm{pb}^{-1}\,(7\,\\mathrm{TeV})"
        #text = "5.36\,\\mathrm{pb}^{-1}\,(7\,\\mathrm{TeV})"
        #if "afterLumi" in extra:
        #    text += extra["afterLumi"]
        if "afterLumi" in extra:
            raise Exception("TODO")

        #ret["lumi"] = text

        latexCMS.SetTextFont(42)
        latexCMS.SetTextAlign(11) 
        latexCMS.SetTextSize(t*cmsTextSize*0.5)
        offX = 0.025
        #if draw:
        #    latexCMS.DrawLatex( 1-r-offX, 1-t+0.05, text)

        # same font as "lumi" on top
        if "bottomLeft" in extra:
            text = extra["bottomLeft"]
            if draw:
                latexCMS.DrawLatex( l+0.125, b+0.03, text)

        latexCMS.SetTextAlign(31) 
        posX =  1-r-offX
        if "cmsLogoPos" in extra :
            if extra["cmsLogoPos"] == "left":
                latexCMS.SetTextAlign(11) 
                # subs width of the frame
                posX -=  (1.-r-l)  -0.075
            if  extra["cmsLogoPos"] == "centralright":
                posX -= 0.2

        text = "CMS"
        offY = 0.1
        latexCMS.SetTextSize(t*cmsTextSize)
        latexCMS.SetTextFont(61)
        if draw:
            latexCMS.DrawLatex( posX, 1-t-offY, text)


        # note: font consistent with https://ghm.web.cern.ch/ghm/plots/MacroExample/CMS_lumi.h
        latexCMS.SetTextFont(52)
        latexCMS.SetTextSize(t*cmsTextSize*0.6)

        offY = 0.15

        text = "preliminary"
        if "insteadOfPreliminary" in extra:
            text = extra["insteadOfPreliminary"]

        ret["preliminary"] = text
        hasPreliminary = text != None

        if draw and text != None:
            latexCMS.DrawLatex(posX, 1-t-offY, text)

        for i in xrange(0,5):
            name = "line"+str(i)
            if name not in extra: continue
            cmsTextSize      = 0.4
            latexCMS.SetTextSize(t*cmsTextSize*0.8) # was: 0.6
            offY = (i)*0.046  # 0.035 -> 0.046
            if hasPreliminary:
                offY += 0.20
            else:
                offY += 0.15
            latexCMS.DrawLatex(posX, 1-t-offY, extra[name])


        return ret
        

            




    @staticmethod
    def xLabels():
        xLabels = {}
        xLabels["xs"] = "#Delta#eta"
        gev = " [GeV]"
        xLabels["etaSublead"] = "#eta^{subleading jet}"
        xLabels["etaLead"] = "#eta^{leading jet}"
        xLabels["ptSublead"] = "p_{T}^{subleading jet}"+gev
        xLabels["ptLead"] = "p_{T}^{leading jet}"+gev
        xLabels["vtx"] = "N_{good vertices}"
        xLabels["vtxNoPUW"] = "N_{good vertices}^{no pu-reweighing}"
        return xLabels

    @staticmethod
    def xRangeUser():
        ret = {}
        ret["vtx"] = (0.5, 6.5)
        ret["ptLead"] = (36, 99.5)
        ret["ptSublead"] = (36, 80)
        return ret

    @staticmethod
    def yLabels():
        yLabels = {}

        yLabels["xsAsPB"] = "#sigma [pb]"
        au = "events [a.u.]"
        for l in DrawMNPlots.xLabels():
            if l not in yLabels:
                yLabels[l] = au

        return yLabels


    def decorate(self, canvas, dataHisto, MCStack, errBand, extra): # override
        from mergeUnfoldedResult import getExtra
        variant = self.infile.split("_")[-1].split(".")[0] # :(

        name = dataHisto.GetName()
        nameShort = "default"
        nspl = name.split("_")
        if len(nspl) > 0:
            nameShort = nspl[0]

        if "dj15" in name:
            lumiVal = "5.36\,\\mathrm{pb}^{-1}"
        else:
            lumiVal = "26.7\,\\mathrm{nb}^{-1}"

        if name.startswith("eta"):
            extra4banner = getExtra(variant, extraSplit="dj15" not in name, lumiVal=lumiVal)
            if "dj15" in name:
                extra4banner["cmsLogoPos"] = "centralright"
        else:
            extra4banner = getExtra(variant, lumiVal=lumiVal)
        if nameShort in ["xs","xxx"] and "dj15" in name:
            extra4banner["cmsLogoPos"] = "left"


        self.banner(extra4banner)

        xLabels = self.xLabels()
        yLabels = self.yLabels()

        if nameShort in xLabels:
            dataHisto.GetXaxis().SetTitle(xLabels[nameShort])
            if "frame" in extra:
                extra["frame"].GetXaxis().SetTitle(xLabels[nameShort])
        else:
            dataHisto.GetXaxis().SetTitle("TODO:"+ nameShort)
            if "frame" in extra:
                extra["frame"].GetXaxis().SetTitle("TODO:"+ nameShort)

        if nameShort in yLabels:
            dataHisto.GetYaxis().SetTitle(yLabels[nameShort])
        else:
            dataHisto.GetYaxis().SetTitle("TODO:"+ nameShort)

        ranges = self.xRangeUser()
        if nameShort in ranges:
            r = ranges[nameShort]
            dataHisto.GetXaxis().SetRangeUser(r[0], r[1])
            if "frame" in extra:
                extra["frame"].GetXaxis().SetRangeUser(r[0], r[1])

        dataHisto.GetYaxis().SetTitleOffset(2)
        dataHisto.GetXaxis().SetTitleOffset(1.5)

        #MChistos = MCStack.GetHists()


        category = dataHisto.GetName().split("_")[-1]
        #print 
        legendPos = {}
        legendPos["dj15fb"] = {}
        legendPos["jet15"] = {}

        b = ROOT.gPad.GetBottomMargin()
        r = ROOT.gPad.GetRightMargin()
        h = 0.15
        w = 0.2
        hOffset = 0.15
        wOffset = 0.05

        legendPos["jet15"]["default"] = (1-r-w-wOffset, b+hOffset, 1-r-wOffset, b+hOffset+h)
        legendPos["dj15fb"]["default"] = legendPos["jet15"]["default"]

        legendPos["jet15"]["vtx"] = (1-r-w-wOffset, b+hOffset+0.1, 1-r-wOffset, b+hOffset+h+0.1)
        legendPos["dj15fb"]["vtx"] = legendPos["jet15"]["vtx"]
        #legendPos["dj15fb"]["vtx"] = (1-r-w-wOffset, b+hOffset+0.1, 1-r-wOffset, b+hOffset+h+0.1)

        off = 0.2
        offY = 0.5
        legendPos["dj15fb"]["etaLead"] = (0.6-off, 0.7-offY, 0.9-off, 0.85-offY)
        legendPos["dj15fb"]["etaSublead"] = legendPos["dj15fb"]["etaLead"]
        off = 0.4
        legendPos["dj15fb"]["xs"] = (0.6-off, 0.2, 0.9-off, 0.35)

        off = 0.2
        offY=0.55
        legendPos["jet15"]["etaLead"] = (0.6-off, 0.7-offY, 0.9-off, 0.85-offY)
        legendPos["jet15"]["etaSublead"] = legendPos["jet15"]["etaLead"]

        if nameShort in legendPos[category]:
            legend = ROOT.TLegend(*legendPos[category][nameShort] )
            print "X"*1000, dataHisto.GetName()

        else:
            legend = ROOT.TLegend(*legendPos[category]["default"] )
        #legend.SetNColumns(3)
        legend.SetFillColor(0)
        legend.AddEntry(dataHisto, "data", "pel")



        MChistos = MCStack.GetStack()
        for h in MChistos:
            h.SetMarkerColor(4)
            h.SetMarkerSize(1)
            h.SetLineColor(4)
            h.SetMarkerStyle(22)
            h.Draw("SAME*P")
            legend.AddEntry(h,  DrawMNPlots.prettyMCName(self.MCLabel), "pel")
            #print type(h.GetDrawOption())
            #h.SetOption("PE hist")
            #print h.GetDrawOption()
        
        legend.AddEntry(errBand, "syst. unc.", "f")

        dataHisto.SetMarkerSize(1)
        dataHisto.SetMarkerStyle(8)

        ROOT.gPad.SetTopMargin(0.12)
        #ROOT.gPad.SetRightMargin(0.07)

        legend.Draw("SAME")
        self.keep.append(legend)



if __name__ == "__main__":
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    ROOT.gSystem.Load("libFWCoreFWLite.so")
    ROOT.AutoLibraryLoader.enable()
    CommonFSQFramework.Core.Style.setTDRStyle()
    parser = OptionParser(usage="usage: %prog [options] filename",
                            version="%prog 1.0")

    parser.add_option("-i", "--infile", action="store", type="string",  dest="infile" )
    parser.add_option("-o", "--outdir", action="store", type="string",  dest="outdir" )
    parser.add_option("-v", "--variant", action="store", type="string",  dest="variant" ) 
    #parser.add_option("-x", "--variant4extra", action="store", type="string",  dest="variant4extra" ) 
    (options, args) = parser.parse_args()

    infile = "plotsMNxs.root"
    if options.infile:
        infile = options.infile

    if options.outdir:
        os.system("mkdir -p " + options.outdir)
        d = DrawMNPlots(infile, outdir = options.outdir)
    else:
        d = DrawMNPlots(infile)

    ignoreSamples = None
    if options.variant == "herwig":
        print "Will draw for herwig"
        ignoreSamples = ["QCD_Pt-15to3000_TuneZ2star_Flat_HFshowerLibrary_7TeV_pythia6"]
    elif options.variant == "pythia":
        print "Will draw for pythia"
        ignoreSamples = ["QCD_Pt-15to1000_TuneEE3C_Flat_7TeV_herwigpp"]
    elif options.variant:
        print "Uknown variant:", options.variant
        sys.exit(1)
    else:
        print "Provide variant (pythia/herwig)"
        sys.exit(1)

    d.MCLabel = options.variant
    d.draw(ignoreSamples=ignoreSamples, doRatio = True)


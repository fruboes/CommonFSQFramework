#! /usr/bin/env python
import ROOT
from ROOT import gRandom,TCanvas,TH1F, TPad

def zoom(todo, x1=0.12,y1=0.6,x2=0.4, y2=0.89, store=[]):
    aPad = TPad("zoom","", x1,y1,x2,y2)
    store.append(aPad)
    #ROOT.SetOwnership(aPad, False) 
    aPad.Draw()
    aPad.cd()
    clones = []
    store.append(clones)
    for t in todo:
       clones.append(hpx.Clone())   
       #ROOT.SetOwnership(clonesaPad, False) 
       if len(clones)==1:
          clones[-1].GetXaxis().SetRangeUser(-1,1)
          clones[-1].Draw()
       else:
          clones[-1].Draw("SAME")



c1 = TCanvas('c1','Example',200,10,700,500)
hpx = TH1F('hpx','px',100,-4,4)


for i in xrange(25000):
    px = gRandom.Gaus()
    hpx.Fill(px)

hpx.Draw()
todo = [hpx]
zoom(todo)
c1.Update()



c1.Print("~/tmp/test.png")

#! /usr/bin/env python
from ROOT import gRandom,TCanvas,TH1F, TPad

c1 = TCanvas('c1','Example',200,10,700,500)
hpx = TH1F('hpx','px',100,-4,4)


for i in xrange(25000):
    px = gRandom.Gaus()
    hpx.Fill(px)

hpx.Draw()
c1.Update()


aPad = TPad("zoom","", 0.12,0.6,0.4,0.89)
#aPad.SetFillColor(11)
aPad.Draw()
aPad.cd()
todo = [hpx]
clones = []
for t in todo:
   clones.append(hpx.Clone())   
   if len(clones)==1:
      clones[-1].GetXaxis().SetRangeUser(-1,1)
      clones[-1].Draw()
   else:
      clones[-1].Draw("SAME")


c1.Print("~/tmp/test.png")

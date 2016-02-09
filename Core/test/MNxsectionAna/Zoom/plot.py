#! /usr/bin/env python
import ROOT
from ROOT import gRandom,TCanvas,TH1F, TPad

def zoom(canvas, minx, maxx, todo=None, ignore=None, x1=0.12,y1=0.6,x2=0.4, y2=0.89, store=[]):
    if todo == None:
       todo = []
       for o in canvas.GetListOfPrimitives():
            isOK=True
            if ignore:
                className = o.ClassName()
                for i in ignore:
                     if className.startswith(i):
                        isOK=False

            if isOK:
                print "Appending", o.GetName()
                todo.append(o)

    aPad = TPad("zoom","", x1,y1,x2,y2)
    store.append(aPad)
    #ROOT.SetOwnership(aPad, False) 
    aPad.Draw()
    aPad.cd()
    clones = []
    store.append(clones)
    for t in todo:
       clones.append(t.Clone())   
       #ROOT.SetOwnership(clonesaPad, False) 
       if len(clones)==1:
          clones[-1].GetXaxis().SetRangeUser(minx,maxx)
          clones[-1].Draw()
       else:
          clones[-1].Draw("SAME")



c1 = TCanvas('c1','Example',200,10,700,500)
hpx = TH1F('hpx','px',100,-4,4)


for i in xrange(25000):
    px = gRandom.Gaus()
    hpx.Fill(px)

hpx.Draw()
zoom(c1, -1,1)
#zoom(c1, ignore=["TH1"])
c1.Update()



c1.Print("~/tmp/test.png")

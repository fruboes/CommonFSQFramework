#! /usr/bin/env python
import os,sys
import fnmatch

# note: dont touch todoCatAll variable, since rivet export in mergeUnfolded.py depends on it 
#   (entry order matters, since it must be consistent with one in rivet routine!)
todoCatAll = ["InclusiveBasic", "InclusiveAsym", "InclusiveWindow", "MNBasic", "MNAsym", "MNWindow"] # Cant touch this...
todoCat = todoCatAll
#todoCat = ["InclusiveBasic"]
#todoCat = ["InclusiveWindow"]
#todoCat = ["MNBasic"]
#todoCat = ["MNAsym", "InclusiveBasic"]
#todoCat = ["MNAsym"]
#todoCat = ["MNWindow"]
#todoCat = ["FWD11_002"]
#todoCat = ["InclusiveBasic"]
todoSteps = []
todoSteps.append("proof")
#todoSteps.append("hadd")
#todoSteps.append("simpleMCplots")
#todoSteps.append("draw")
#todoSteps.append("unfold")
#todoSteps.append("merge")
#todoSteps.append("rivetExport")

from optparse import OptionParser
def main():
    parser = OptionParser(usage="usage: %prog [options] filename",
                            version="%prog 1.0")
                            
    #parser.add_option("-p", "--plotDefFile",   action="store", type="string", dest="plotDefFile", help="plot using definitions from plot def file" )
    parser.add_option("-c", "--todoCats",   action="store", type="string", dest="todoCats", help="ana types to do" )
    (options, args) = parser.parse_args()
    global todoCat
    if options.todoCats:
        todoCat = options.todoCats.split(",")
        doIknowAll = set(todoCat)-set(todoCatAll)
        if len(doIknowAll) != 0:
            raise Exception("Unknown analysis type(s): "+ " ".join(doIknowAll) )
    
    for cat in todoCat:
        for step in todoSteps:
            if step == "proof":
                os.system("./MNxsAnalyzerClean.py -v {}".format(cat))

            elif step == "draw":
                command="./mnDraw.py -i plotsMNxs_XXS.root -o ~/tmp/MNXS_XXS_detectorLevel_XXM/ -v XXM"
                os.system(command.replace("XXS", cat).replace("XXM", "herwig"))
                os.system(command.replace("XXS", cat).replace("XXM", "pythia"))
            elif step == "hadd":
                target = "plotsMNxs_{}.root".format(cat)
                os.system("rm "+target)
                infiles = []
                for file in os.listdir('.'):
                    if fnmatch.fnmatch(file, 'plotsMNxs_{}_*.root'.format(cat)):
                        infiles.append(file)
                os.system("./hadd.py " + target + " " + " ".join(infiles) )
            elif step == "simpleMCplots":
                todo=[]
                #todo=["ptHat"]
                samples = ["QCD_Pt-15to3000_TuneZ2star_Flat_HFshowerLibrary_7TeV_pythia6", "QCD_Pt-15to1000_TuneEE3C_Flat_7TeV_herwigpp"]
                triggers = ["jet15", "dj15fb"]
                for t in todo:
                    os.system("./simpleMCplots.py -a {0},{1} -b {0},{2} -v {3}".format(t,samples[0], samples[1], cat))
                    #os.system("../simpleMCplots.py -d -a {0},{1} -b {0},{2} -v {3}".format(t,samples[0], samples[1], cat))
                #continue
                ptypes = ["fake" , "miss"]
                for ptype in ptypes:
                    for s in samples:
                        for trg in triggers:
                            if ptype == "fake":
                                nom = "fakeresponse_central_{}".format(trg)
                                denom =  "measuredresponse_central_{}".format(trg)
                            elif ptype == "miss":
                                nom = "miss_central_{}".format(trg)
                                denom =  "truthresponse_central_{}".format(trg)

                            command = "./simpleMCplots.py -d -a {1},{0} -b {2},{0} -v {3}".format(s, nom, denom,cat)
                            label = "pythia"
                            if label not in s: label = "herwig"
                            command += " -l "+label
                            os.system(command)



            elif step == "unfold":
                print "Starting unfold. This may take some time..."
                sys.stdout.flush()
                os.system("./unfoldMN.py -v {} 2>&1 > unfold_{}.log ".format(cat, cat))
            elif step == "merge":
                if cat == "FWD11_002":
                    os.system("./mergeUnfoldedResult.py -v {} -n xs  -b -s 5.6".format(cat))
                else:
                    os.system("./mergeUnfoldedResult.py -v {} -n xs -b".format(cat))
                    #os.system("./mergeUnfoldedResult.py -v {} -n xs -b -j".format(cat))
                    os.system("./mergeUnfoldedResult.py -v {} -n area -b".format(cat))
                    #os.system("./mergeUnfoldedResult.py -v {} -n area -b -j".format(cat))

    if "rivetExport" in todoSteps:
        mergeF = "/cvmfs/cms.cern.ch/slc6_amd64_gcc481/external/yoda/1.3.0-cms/bin/yodamerge"
        if not os.path.isfile(mergeF):
            raise Exception("yodamerge not found")
        f = lambda i: "d0"+str(i)+"-x01-y01.yoda" if i < 10 else "d"+str(i)+"-x01-y01.yoda"
        todo = [f(i) for i in xrange(1,7)] + [f(i) for i in xrange(11,17)]
        for t in todo:
            if not os.path.isfile(t):
                raise Exception("Input file missing: "+t)

        command = mergeF + " --assume-normalized -o CMS_2015_FWD071.yoda "+ " ".join(todo)
        os.system(command)


            


if __name__ == "__main__":
    main()


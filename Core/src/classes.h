

// note: workaround for CMSSW_4_2_8_lowpupatch1
#include "RVersion.h"
#if ROOT_VERSION_CODE >= ROOT_VERSION(5,28,0)
#include "FWCore/Utilities/interface/GCC11Compatibility.h"
#endif

#include "FWCore/ParameterSet/interface/FileInPath.h"
#include "TH1.h"
#include "TFile.h"
#include <cmath>
#include <string>
#include <boost/shared_ptr.hpp>
#include <vector>
//#define constexpr static const
#include "PhysicsTools/Utilities/interface/LumiReWeighting.h"
#include "CommonFSQFramework/Core/interface/TestTrackData.h"


namespace {
  struct dictionary {
    edm::FileInPath v1;
    edm::LumiReWeighting v2;

    tmf::TestTrackData v3;
    std::vector<tmf::TestTrackData> v4;

  };
}


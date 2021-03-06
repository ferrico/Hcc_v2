import FWCore.ParameterSet.Config as cms

from FWCore.ParameterSet.VarParsing import VarParsing

process = cms.Process("UFHZZ4LAnalysis")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.MessageLogger.categories.append('UFHZZ4LAna')

process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.Geometry.GeometryRecoDB_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.GlobalTag.globaltag='106X_mcRun2_asymptotic_preVFP_v9'

process.Timing = cms.Service("Timing",
                             summaryOnly = cms.untracked.bool(True)
                             )


process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(15000) )

process.options = cms.untracked.PSet(
	numberOfThreads = cms.untracked.uint32(2) )

myfilelist = cms.untracked.vstring(
'/store/mc/RunIISummer19UL16MiniAOD/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/106X_mcRun2_asymptotic_v13-v2/100000/03C3B70E-A520-5C46-8C57-B1EBE48038CB.root',
#'/store/mc/RunIISummer19UL16MiniAODAPV/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/106X_mcRun2_asymptotic_preVFP_v8-v1/100000/003DBF2A-A6DF-D746-B855-59A283679A4A.root',        
#DUMMYFILELIST
        )

process.source = cms.Source("PoolSource",fileNames = myfilelist,
                           # duplicateCheckMode = cms.untracked.string('noDuplicateCheck'),
                            )

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("DUMMYFILENAME_pre.root")
)

# clean muons by segments 
process.boostedMuons = cms.EDProducer("PATMuonCleanerBySegments",
				     src = cms.InputTag("slimmedMuons"),
				     preselection = cms.string("track.isNonnull"),
				     passthrough = cms.string("isGlobalMuon && numberOfMatches >= 2"),
				     fractionOfSharedSegments = cms.double(0.499),
				     )


# Kalman Muon Calibrations
process.calibratedMuons = cms.EDProducer("KalmanMuonCalibrationsProducer",
                                         muonsCollection = cms.InputTag("boostedMuons"),
                                         isMC = cms.bool(True),
                                         isSync = cms.bool(True),
                                         useRochester = cms.untracked.bool(True),
                                         year = cms.untracked.int32(20160)
                                         )

#from EgammaAnalysis.ElectronTools.regressionWeights_cfi import regressionWeights
#process = regressionWeights(process)
#process.load('EgammaAnalysis.ElectronTools.regressionApplication_cff')

process.selectedElectrons = cms.EDFilter("PATElectronSelector",
                                         src = cms.InputTag("slimmedElectrons"),
                                         #cut = cms.string("pt > 5 && abs(eta)<2.5 && abs(-log(tan(superClusterPosition.theta/2)))<2.5")
                                         cut = cms.string("pt > 5 && abs(eta)<2.5")
                                         )

process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
    calibratedPatElectrons = cms.PSet(
        #initialSeed = cms.untracked.uint32(SEED), # for HPC
        initialSeed = cms.untracked.uint32(123456), # for crab
        engineName = cms.untracked.string('TRandom3')
    )
)

#process.load('EgammaAnalysis.ElectronTools.calibratedElectronsRun2_cfi')
#process.calibratedPatElectrons = cms.EDProducer("CalibratedPatElectronProducerRun2",
#                                        # input collections
#                                        #electrons = cms.InputTag('selectedElectrons'),
#                                        electrons = cms.InputTag('electronsMVA'),
#                                        gbrForestName = cms.vstring('electron_eb_ECALTRK_lowpt', 'electron_eb_ECALTRK',
#                                                                    'electron_ee_ECALTRK_lowpt', 'electron_ee_ECALTRK',
#                                                                    'electron_eb_ECALTRK_lowpt_var', 'electron_eb_ECALTRK_var',
#                                                                    'electron_ee_ECALTRK_lowpt_var', 'electron_ee_ECALTRK_var'),
#                                        isMC = cms.bool(True),
#                                        isSynchronization = cms.bool(False),
#                                        #correctionFile = cms.string("EgammaAnalysis/ElectronTools/data/ScalesSmearings/Moriond17_23Jan_ele")
#                                        correctionFile = cms.string("EgammaAnalysis/ElectronTools/data/ScalesSmearings/Legacy2016_07Aug2017_FineEtaR9_v3_ele_unc")
#                                        )

from RecoEgamma.EgammaTools.EgammaPostRecoTools import setupEgammaPostRecoSeq
setupEgammaPostRecoSeq(process,
                       runEnergyCorrections=True,
                       runVID=True,
                       eleIDModules=['RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Summer16UL_ID_ISO_cff','RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV70_cff'],
                       phoIDModules=['RecoEgamma.PhotonIdentification.Identification.cutBasedPhotonID_Fall17_94X_V2_cff'],
                       era='2016-Legacy')
'''
process.load("RecoEgamma.EgammaTools.calibratedEgammas_cff")
process.calibratedPatElectrons.correctionFile = "EgammaAnalysis/ElectronTools/data/ScalesSmearings/Legacy2016_07Aug2017_FineEtaR9_v3_ele_unc"
#process.calibratedPatElectrons.src = cms.InputTag("selectedElectrons")
#process.calibratedPatElectrons.src = cms.InputTag("electronsMVA")
process.calibratedPatElectrons.src = cms.InputTag("slimmedElectrons")
'''
##  from PhysicsTools.SelectorUtils.tools.vid_id_tools import *
##  dataFormat = DataFormat.MiniAOD
##  switchOnVIDElectronIdProducer(process, dataFormat)
##  # define which IDs we want to produce
##  #my_id_modules = [ 'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring16_HZZ_V1_cff' ]
##  my_id_modules = [ 'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Summer16_ID_ISO_cff','RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV70_cff' ]
##  # add them to the VID producer
##  for idmod in my_id_modules:
##      setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)
##  #process.electronMVAValueMapProducer.srcMiniAOD = cms.InputTag("calibratedPatElectrons")
##  process.egmGsfElectronIDs.physicsObjectSrc = cms.InputTag('selectedElectrons')
##  process.electronMVAVariableHelper.srcMiniAOD = cms.InputTag('selectedElectrons')
##  process.electronMVAValueMapProducer.srcMiniAOD= cms.InputTag('selectedElectrons')
##  
##  from RecoEgamma.EgammaTools.egammaObjectModificationsInMiniAOD_cff import egamma_modifications,egamma8XLegacyEtScaleSysModifier,egamma8XObjectUpdateModifier
##  egamma_modifications.append(egamma8XObjectUpdateModifier)
##  
##  process.electronsMVA = cms.EDProducer("SlimmedElectronMvaIDProducer",
##                                        #mvaValuesMap = cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Spring16HZZV1Values"),
##                                        mvaValuesMap = cms.InputTag("electronMVAValueMapProducer:ElectronMVAEstimatorRun2Summer16IdIsoValues"),
##                                        #electronsCollection = cms.InputTag("calibratedPatElectrons"),
##                                        electronsCollection = cms.InputTag("selectedElectrons"),
##                                        #idname = cms.string("ElectronMVAEstimatorRun2Spring16HZZV1Values"),
##                                        idname = cms.string("ElectronMVAEstimatorRun2Summer16IdIsoValues"),
##  )

# FSR Photons
process.load('UFHZZAnalysisRun2.FSRPhotons.fsrPhotons_cff')

from RecoJets.JetProducers.PileupJetIDParams_cfi import full_80x_chs       
from RecoJets.JetProducers.PileupJetIDCutParams_cfi import full_80x_chs_wp 
from PhysicsTools.PatAlgos.tools.jetTools import updateJetCollection       

if (True):                                                               
    # JEC corrections                                                    
    jecLevels = None                                                     
    jecLevels = [ 'L1FastJet', 'L2Relative', 'L3Absolute' ]              
                                                                         
    btagVector = [                                                       
        'pfDeepFlavourJetTags:probb',                                    
        'pfDeepFlavourJetTags:probbb',                                   
        'pfDeepFlavourJetTags:problepb',                                 
        'pfDeepFlavourJetTags:probc',                                    
        'pfDeepFlavourJetTags:probuds',                                  
        'pfDeepFlavourJetTags:probg',                                    
        'pfDeepCSVJetTags:probudsg',                                     
        'pfDeepCSVJetTags:probb',                                        
        'pfDeepCSVJetTags:probc',                                        
        'pfDeepCSVJetTags:probbb'                                        
    ]                                                                    
                                                                         
    updateJetCollection(                                                 
        process,                                                         
        jetSource = cms.InputTag('slimmedJets'),                         
        pvSource = cms.InputTag('offlineSlimmedPrimaryVertices'),        
        svSource = cms.InputTag('slimmedSecondaryVertices'),             
        jetCorrections = ('AK4PFchs', cms.vstring(jecLevels), 'None'),   
        btagDiscriminators = btagVector,                                 
        postfix = 'WithDeepInfo'                                         
    )                                                                    
    process.jetSequence = cms.Sequence(process.patJetCorrFactorsWithDeepInfo                         
                                   *process.updatedPatJetsWithDeepInfo                           
                                   *process.pfImpactParameterTagInfosWithDeepInfo                
                                   *process.pfInclusiveSecondaryVertexFinderTagInfosWithDeepInfo 
                                   *process.pfDeepCSVTagInfosWithDeepInfo                        
                                   *process.pfDeepCSVJetTagsWithDeepInfo                         
                                   *process.pfDeepFlavourTagInfosWithDeepInfo                    
                                   *process.pfDeepFlavourJetTagsWithDeepInfo                     
                                   *process.patJetCorrFactorsTransientCorrectedWithDeepInfo      
                                   *process.updatedPatJetsTransientCorrectedWithDeepInfo         
    )                                                                                                

# Jet Energy Corrections
import os
from CondCore.DBCommon.CondDBSetup_cfi import *
#era = "Summer16_23Sep2016V3_MC"
era = "Summer16_07Aug2017_V11_MC"
# for HPC
dBFile = os.environ.get('CMSSW_BASE')+"/src/UFHZZAnalysisRun2/UFHZZ4LAna/data/"+era+".db"
# for crab
#dBFile = "src/UFHZZAnalysisRun2/UFHZZ4LAna/data/"+era+".db"
process.jec = cms.ESSource("PoolDBESSource",
                           CondDBSetup,
                           connect = cms.string("sqlite_file:"+dBFile),
                           toGet =  cms.VPSet(
        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PF"),
            label= cms.untracked.string("AK4PF")
            ),
        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PFchs"),
            label= cms.untracked.string("AK4PFchs")
            ),

        cms.PSet(
            record = cms.string("JetCorrectionsRecord"),
            tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK8PFchs"),
            label= cms.untracked.string("AK8PFchs")
            ),
        )
)
process.es_prefer_jec = cms.ESPrefer("PoolDBESSource",'jec')

process.load("PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff")

process.jetCorrFactors = process.updatedPatJetCorrFactors.clone(
    src = cms.InputTag("updatedPatJetsTransientCorrectedWithDeepInfo"),
    levels = ['L1FastJet', 
              'L2Relative', 
              'L3Absolute'],
    payload = 'AK4PFchs' ) 

process.AK8PFJetCorrFactors = process.updatedPatJetCorrFactors.clone(
    src = cms.InputTag("slimmedJetsAK8"),
    levels = ['L1FastJet',
              'L2Relative',
              'L3Absolute'],
    payload = 'AK8PFchs' )

process.slimmedJetsJEC = process.updatedPatJets.clone(
    #jetSource = cms.InputTag("slimmedJets"),
    jetSource = cms.InputTag("updatedPatJetsTransientCorrectedWithDeepInfo"),  
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("jetCorrFactors")),      
    addBTagInfo          = cms.bool(True),                                     
    addDiscriminators    = cms.bool(True)   ## addition of btag discriminators 
    )

process.slimmedJetsAK8JEC = process.updatedPatJets.clone(
    jetSource = cms.InputTag("slimmedJetsAK8"),
    jetCorrFactorsSource = cms.VInputTag(cms.InputTag("AK8PFJetCorrFactors"))
    )

### add pileup id and discriminant to patJetsReapplyJEC
#process.load("RecoJets.JetProducers.PileupJetID_cfi")
#process.pileupJetIdUpdated = process.pileupJetId.clone(
#    jets=cms.InputTag("slimmedJets"),
#    inputIsCorrected=False,
#    applyJec=True,
#    vertexes=cms.InputTag("offlineSlimmedPrimaryVertices")
#)
#process.slimmedJetsJEC.userData.userFloats.src += ['pileupJetIdUpdated:fullDiscriminant']
#process.slimmedJetsJEC.userData.userInts.src += ['pileupJetIdUpdated:fullId']


# JER
process.load("JetMETCorrections.Modules.JetResolutionESProducer_cfi")
# for hpc
dBJERFile = os.environ.get('CMSSW_BASE')+"/src/UFHZZAnalysisRun2/UFHZZ4LAna/data/Summer16_25nsV1_MC.db"
# for crab
#dBJERFile = "src/UFHZZAnalysisRun2/UFHZZ4LAna/data/Summer16_25nsV1_MC.db"
process.jer = cms.ESSource("PoolDBESSource",
        CondDBSetup,
        connect = cms.string("sqlite_file:"+dBJERFile),
        toGet = cms.VPSet(
            cms.PSet(
                record = cms.string('JetResolutionRcd'),
                tag    = cms.string('JR_Summer16_25nsV1_MC_PtResolution_AK4PFchs'),
                label  = cms.untracked.string('AK4PFchs_pt')
                ),
            cms.PSet(
                record = cms.string('JetResolutionRcd'),
                tag    = cms.string('JR_Summer16_25nsV1_MC_PhiResolution_AK4PFchs'),
                label  = cms.untracked.string('AK4PFchs_phi')
                ),
            cms.PSet(
                record = cms.string('JetResolutionScaleFactorRcd'),
                tag    = cms.string('JR_Summer16_25nsV1_MC_SF_AK4PFchs'),
                label  = cms.untracked.string('AK4PFchs')
                )
            )
        )
process.es_prefer_jer = cms.ESPrefer('PoolDBESSource', 'jer')


#QGTag
process.load("CondCore.CondDB.CondDB_cfi")
qgDatabaseVersion = 'cmssw8020_v2'
# for hpc
QGdBFile = os.environ.get('CMSSW_BASE')+"/src/UFHZZAnalysisRun2/UFHZZ4LAna/data/QGL_"+qgDatabaseVersion+".db"
# for crab
#QGdBFile = "src/UFHZZAnalysisRun2/UFHZZ4LAna/data/QGL_"+qgDatabaseVersion+".db"
process.QGPoolDBESSource = cms.ESSource("PoolDBESSource",
      DBParameters = cms.PSet(messageLevel = cms.untracked.int32(1)),
      timetype = cms.string('runnumber'),
      toGet = cms.VPSet(
        cms.PSet(
            record = cms.string('QGLikelihoodRcd'),
            tag    = cms.string('QGLikelihoodObject_'+qgDatabaseVersion+'_AK4PFchs'),
            label  = cms.untracked.string('QGL_AK4PFchs')
        ),
      ),
      connect = cms.string('sqlite_file:'+QGdBFile)
)
process.es_prefer_qg = cms.ESPrefer('PoolDBESSource','QGPoolDBESSource')
process.load('RecoJets.JetProducers.QGTagger_cfi')
process.QGTagger.srcJets = cms.InputTag( 'slimmedJetsJEC' )
process.QGTagger.jetsLabel = cms.string('QGL_AK4PFchs')
process.QGTagger.srcVertexCollection=cms.InputTag("offlinePrimaryVertices")

# compute corrected pruned jet mass
process.corrJets = cms.EDProducer ( "CorrJetsProducer",
                                    jets    = cms.InputTag( "slimmedJetsAK8JEC" ),
                                    vertex  = cms.InputTag( "offlineSlimmedPrimaryVertices" ), 
                                    rho     = cms.InputTag( "fixedGridRhoFastjetAll"   ),
                                    payload = cms.string  ( "AK8PFchs" ),
                                    isData  = cms.bool    (  False ),
                                    year = cms.untracked.int32(20160))


# Recompute MET
from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD

runMetCorAndUncFromMiniAOD(process,
            isData=False,
            )

from PhysicsTools.PatUtils.l1ECALPrefiringWeightProducer_cfi import l1ECALPrefiringWeightProducer
process.prefiringweight = l1ECALPrefiringWeightProducer.clone(                                   
    DataEra = cms.string("2016BtoH"), #Use 2016BtoH for 2016 2017BtoF foe 2017                   
    UseJetEMPt = cms.bool(False),                                                                
    PrefiringRateSystematicUncty = cms.double(0.2),                                              
    SkipWarnings = False)    
                                                                    
# STXS
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.mergedGenParticles = cms.EDProducer("MergedGenParticleProducer",
    inputPruned = cms.InputTag("prunedGenParticles"),
    inputPacked = cms.InputTag("packedGenParticles"),
)
#process.myGenerator = cms.EDProducer("GenParticles2HepMCConverterHTXS",
process.myGenerator = cms.EDProducer("GenParticles2HepMCConverter",
    genParticles = cms.InputTag("mergedGenParticles"),
    genEventInfo = cms.InputTag("generator"),
    signalParticlePdgIds = cms.vint32(25)
)
process.rivetProducerHTXS = cms.EDProducer('HTXSRivetProducer',
  HepMCCollection = cms.InputTag('myGenerator','unsmeared'),
  LHERunInfo = cms.InputTag('externalLHEProducer'),
  ProductionMode = cms.string('AUTO'),
)
# HZZ Fiducial from RIVET
process.rivetProducerHZZFid = cms.EDProducer('HZZRivetProducer',
  HepMCCollection = cms.InputTag('myGenerator','unsmeared'),
)



# Analyzer
process.Ana = cms.EDAnalyzer('UFHZZ4LAna',
                              photonSrc    = cms.untracked.InputTag("slimmedPhotons"),
                              #electronSrc  = cms.untracked.InputTag("electronsMVA"),
                              #electronUnSSrc  = cms.untracked.InputTag("electronsMVA"),
                              electronUnSSrc  = cms.untracked.InputTag("slimmedElectrons"),
 				#                             electronSrc  = cms.untracked.InputTag("calibratedPatElectrons"),
                              muonSrc      = cms.untracked.InputTag("calibratedMuons"),
                              tauSrc      = cms.untracked.InputTag("slimmedTaus"),
                              jetSrc       = cms.untracked.InputTag("slimmedJetsJEC"),
                              mergedjetSrc = cms.untracked.InputTag("corrJets"),
                              metSrc       = cms.untracked.InputTag("slimmedMETs","","UFHZZ4LAnalysis"),
                              vertexSrc    = cms.untracked.InputTag("offlineSlimmedPrimaryVertices"),
                              beamSpotSrc  = cms.untracked.InputTag("offlineBeamSpot"),
                              conversionSrc  = cms.untracked.InputTag("reducedEgamma","reducedConversions"),
                              isMC         = cms.untracked.bool(True),
                              isSignal     = cms.untracked.bool(True),
                              mH           = cms.untracked.double(125.0),
                              CrossSection = cms.untracked.double(1),#DUMMYCROSSSECTION),
                              FilterEff    = cms.untracked.double(1),
                              weightEvents = cms.untracked.bool(True),
                              elRhoSrc     = cms.untracked.InputTag("fixedGridRhoFastjetAll"),
                              muRhoSrc     = cms.untracked.InputTag("fixedGridRhoFastjetAll"),
                              rhoSrcSUS    = cms.untracked.InputTag("fixedGridRhoFastjetCentralNeutral"),
                              pileupSrc     = cms.untracked.InputTag("slimmedAddPileupInfo"),
                              pfCandsSrc   = cms.untracked.InputTag("packedPFCandidates"),
                              fsrPhotonsSrc = cms.untracked.InputTag("boostedFsrPhotons"),
                              prunedgenParticlesSrc = cms.untracked.InputTag("prunedGenParticles"),
                              packedgenParticlesSrc = cms.untracked.InputTag("packedGenParticles"),
                              genJetsSrc = cms.untracked.InputTag("slimmedGenJets"),
                              generatorSrc = cms.untracked.InputTag("generator"),
                              lheInfoSrc = cms.untracked.InputTag("externalLHEProducer"),
                              reweightForPU = cms.untracked.bool(True),
                              triggerSrc = cms.InputTag("TriggerResults","","HLT"),
                              triggerObjects = cms.InputTag("selectedPatTrigger"),
                              doJER = cms.untracked.bool(True),
                              doJEC = cms.untracked.bool(True),
                              doTriggerMatching = cms.untracked.bool(False),
                              triggerList = cms.untracked.vstring(
                                'HLT_Ele17_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v',
                                'HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v',
                                'HLT_DoubleEle33_CaloIdL_GsfTrkIdVL_v',
                                'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v',
                                'HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_DZ_v',
                                'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v',
                                'HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v',
                                'HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v',
                                'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_v',
                                'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ_v',
                                'HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v',
                                'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v',
                                'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v',
                                'HLT_Mu23_TrkIsoVVL_Ele8_CaloIdL_TrackIdL_IsoVL_v',
                                'HLT_Mu8_DiEle12_CaloIdL_TrackIdL_v',
                                'HLT_DiMu9_Ele9_CaloIdL_TrackIdL_v',
                                'HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL_v',
                                'HLT_TripleMu_12_10_5_v',
                                'HLT_Ele25_eta2p1_WPTight_Gsf_v',
                                'HLT_Ele27_WPTight_Gsf_v',
                                'HLT_Ele27_eta2p1_WPLoose_Gsf_v',
                                'HLT_Ele32_eta2p1_WPTight_Gsf_v',
                                'HLT_IsoMu20_v',
                                'HLT_IsoTkMu20_v',
                                'HLT_IsoMu22_v',
                                'HLT_IsoTkMu22_v',
                                'HLT_IsoMu24_v',
                                'HLT_IsoTkMu24_v',
                              ),
                              verbose = cms.untracked.bool(False),              
                              skimLooseLeptons = cms.untracked.int32(4),              
                              skimTightLeptons = cms.untracked.int32(4),              
                              #bestCandMela = cms.untracked.bool(False),
#                              verbose = cms.untracked.bool(True),              
                              year = cms.untracked.int32(20160),
                              isCode4l = cms.untracked.bool(False),
                             )


process.p = cms.Path(process.fsrPhotonSequence*
                     process.boostedMuons*
                     process.calibratedMuons*
                     #process.regressionApplication*
        #             process.selectedElectrons*
                     #process.calibratedPatElectrons*
                     process.egmGsfElectronIDSequence*
        #             process.electronMVAValueMapProducer*
        #             process.electronsMVA*
                     process.egmPhotonIDSequence*
                     process.egammaPostRecoSeq*
                     #			process.calibratedPatElectrons*
                     process.jetSequence*
                     process.jetCorrFactors*
                     #process.pileupJetIdUpdated*
                     process.slimmedJetsJEC*
                     process.QGTagger*
                     process.AK8PFJetCorrFactors*
                     process.slimmedJetsAK8JEC*
                     process.fullPatMetSequence*
                     process.corrJets*
                     process.mergedGenParticles*process.myGenerator*process.rivetProducerHTXS*#process.rivetProducerHZZFid*
                     process.prefiringweight* 
                     process.Ana
                     )

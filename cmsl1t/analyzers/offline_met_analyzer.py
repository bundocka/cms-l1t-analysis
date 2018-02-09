from BaseAnalyzer import BaseAnalyzer
from cmsl1t.plotting.efficiency import EfficiencyPlot
from cmsl1t.collections import EfficiencyCollection
from cmsl1t.plotting.onlineVsOffline import OnlineVsOffline
from cmsl1t.plotting.resolution import ResolutionPlot
from cmsl1t.plotting.resolution_vs_X import ResolutionVsXPlot
from cmsl1t.playground.jetfilters import pfJetFilter
from cmsl1t.playground.metfilters import pfMetFilter
import cmsl1t.recalc.met as recalc
from cmsl1t.playground.eventreader import Met, Sum
from math import pi
import pprint
from collections import namedtuple
import numpy as np


sum_types = [
    "caloHT", "pfHT", "caloMETHF", "caloMETBE", "pfMET_NoMu",
]
sum_types += [t + '_Emu' for t in sum_types]
jet_types = [
    "caloJetET_BE", "caloJetET_HF",
    "pfJetET_BE", "pfJetET_HF",
]
jet_types += [t + '_Emu' for t in jet_types]

Sums = namedtuple("Sums", sum_types)

# Eta ranges so we can put |\eta| < val as the legend header on the
# efficiency plots.
ETA_RANGES = dict(
    caloHT="|\\eta| < 2.4",
    pfHT="|\\eta| < 2.4",
    caloMETHF="|\\eta| < 5.0",
    caloMETBE="|\\eta| < 3.0",
    pfMET_NoMu="|\\eta| < 5.0",
    caloJetET_BE="|\\eta| < 3.0",
    caloJetET_HF="3.0 < |\\eta| < 5.0",
    pfJetET_BE="|\\eta| < 3.0",
    pfJetET_HF="3.0 < |\\eta| < 5.0",
)

THRESHOLDS = dict(
    caloHT=[160, 220, 280, 340, 400],
    pfHT=[160, 220, 280, 340, 400],
    caloMETBE=[40, 60, 80, 100, 120],
    caloMETHF=[40, 60, 80, 100, 120],
    pfMET_NoMu=[40, 60, 80, 100, 120],
    caloJetET_BE=[35, 60, 90, 140, 180],
    caloJetET_HF=[35, 60, 90, 140, 180],
    pfJetET_BE=[35, 60, 90, 140, 180],
    pfJetET_HF=[35, 60, 90, 140, 180],
)

HIGH_RANGE_BINS = list(range(0, 100, 5)) + list(range(100, 300, 10))
HIGH_RANGE_BINS += list(range(300, 500, 20)) + list(range(500, 700, 50))
HIGH_RANGE_BINS += list(range(700, 1000, 100))+ list(range(1000, 1400, 200))
HIGH_RANGE_BINS += list(range(1400, 2000, 300))
HIGH_RANGE_BINS_HT = list(range(30, 100, 5)) + list(range(100, 300, 10))
HIGH_RANGE_BINS_HT += list(range(300, 500, 20)) + list(range(500, 700, 50))
HIGH_RANGE_BINS_HT += list(range(700, 1000, 100))+ list(range(1000, 1400, 200))
HIGH_RANGE_BINS_HT += list(range(1400, 2000, 300))

HIGH_RANGE_BINS = np.asarray(HIGH_RANGE_BINS, 'd')
HIGH_RANGE_BINS_HT = np.asarray(HIGH_RANGE_BINS_HT, 'd')

def ExtractSums(event):
    offline = dict(
        caloHT=Sum(event.sums.caloHt),
        pfHT=Sum(event.sums.Ht),
        caloMETBE=Met(event.sums.caloMetBE, event.sums.caloMetPhiBE),
        caloMETHF=Met(event.sums.caloMet, event.sums.caloMetPhi),
        pfMET_NoMu=Met(event.sums.pfMetNoMu, event.sums.pfMetNoMuPhi),
        caloHT_Emu=Sum(event.sums.caloHt),
        pfHT_Emu=Sum(event.sums.Ht),
        caloMETHF_Emu=Met(event.sums.caloMet, event.sums.caloMetPhi),
        caloMETBE_Emu=Met(event.sums.caloMetBE, event.sums.caloMetPhiBE),
        pfMET_NoMu_Emu=Met(event.sums.pfMetNoMu, event.sums.pfMetNoMuPhi)
    )
    online = dict(
        caloHT=event.l1Sums["L1Htt"],
        pfHT=event.l1Sums["L1Htt"],
        caloMETBE=event.l1Sums["L1Met"],
        caloMETHF=event.l1Sums["L1MetHF"],
        pfMET_NoMu=event.l1Sums["L1MetHF"],
        caloHT_Emu=event.l1Sums["L1EmuHtt"],
        pfHT_Emu=event.l1Sums["L1EmuHtt"],
        caloMETHF_Emu=event.l1Sums["L1EmuMetHF"],
        caloMETBE_Emu=event.l1Sums["L1EmuMet"],
        pfMET_NoMu_Emu=event.l1Sums["L1EmuMetHF"]
    )
    return online, offline


class Analyzer(BaseAnalyzer):

    def __init__(self, config, **kwargs):
        super(Analyzer, self).__init__("weekly_analyzer", config)

        for name in sum_types:
            eff_plot = EfficiencyPlot("L1", "offline_" + name)
            res_plot = ResolutionPlot("energy", "L1", "offline_" + name)
            twoD_plot = OnlineVsOffline("L1", "offline_" + name)
            self.register_plotter(eff_plot)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_eff", eff_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

            eff_plot_HR = EfficiencyPlot("L1", "offline_" + name + "_HiRange")
            twoD_plot_HR = OnlineVsOffline(
                "L1", "offline_" + name + "_HiRange")
            self.register_plotter(eff_plot_HR)
            self.register_plotter(twoD_plot_HR)
            setattr(self, name + "_eff_HR", eff_plot_HR)
            setattr(self, name + "_2D_HR", twoD_plot_HR)

        for angle in sum_types:
            name = angle + "_phi"
            if 'HT' in angle:
                continue
            res_plot = ResolutionPlot("phi", "L1", "offline_" + name)
            twoD_plot = OnlineVsOffline("L1", "offline_" + name)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

        for name in jet_types:
            eff_plot = EfficiencyPlot("L1", "offline_" + name)
            res_plot = ResolutionPlot("energy", "L1", "offline_" + name)
            twoD_plot = OnlineVsOffline("L1", "offline_" + name)
            self.register_plotter(eff_plot)
            self.register_plotter(res_plot)
            self.register_plotter(twoD_plot)
            setattr(self, name + "_eff", eff_plot)
            setattr(self, name + "_res", res_plot)
            setattr(self, name + "_2D", twoD_plot)

            eff_plot_HR = EfficiencyPlot("L1", "offline_" + name + "_HiRange")
            twoD_plot_HR = OnlineVsOffline(
                "L1", "offline_" + name + "_HiRange")
            self.register_plotter(eff_plot_HR)
            self.register_plotter(twoD_plot_HR)
            setattr(self, name + "_eff_HR", eff_plot_HR)
            setattr(self, name + "_2D_HR", twoD_plot_HR)

        self.res_vs_eta_CentralJets = ResolutionVsXPlot(
            "energy", "onlineJet", "offlineJet", "offlineJet_eta")
        self.register_plotter(self.res_vs_eta_CentralJets)

    def prepare_for_events(self, reader):
        puBins = self.puBins
        puBins_HR = [0, 999]

        Config = namedtuple(
            "Config",
            "name off_title on_title min max",
        )
        cfgs = [
            Config("caloHT", "Offline Calo HT", "L1 HT", 30, 800),
            Config("pfHT", "Offline PF HT", "L1 HT", 30, 800),
            Config("caloMETHF", "Offline Calo MET HF", "L1 MET", 0, 400),
            Config("caloMETBE", "Offline Calo MET BE", "L1 MET", 0, 400),
            Config("pfMET_NoMu", "Offline PF MET NoMu", "L1 MET", 0, 400),
            Config("caloJetET_BE", "Offline Central Calo Jet ET","L1 Jet ET", 20, 400),
            Config("caloJetET_HF", "Offline Forward Calo Jet ET","L1 Jet ET", 20, 400),
            Config("pfJetET_BE", "Offline Central PF Jet ET","L1 Jet ET", 20, 400),
            Config("pfJetET_HF", "Offline Forward PF Jet ET","L1 Jet ET", 20, 400),
        ]
        self._plots_from_cfgs(cfgs, puBins)
        self._plots_from_cfgs(cfgs, puBins, emulator=True)
        self._plots_from_cfgs(cfgs, puBins_HR, high_range=True)
        self._plots_from_cfgs(cfgs, puBins_HR, emulator=True, high_range=True)

        self.res_vs_eta_CentralJets.build(
            "Online Jet energy (GeV)",
            "Offline Jet energy (GeV)",
            "Offline Jet Eta (rad)",
            puBins,
            50, -0.5, 3.5, 50, -5.0, 5.0,
        )
        return True

    def _plots_from_cfgs(self, cfgs, puBins, emulator=False, high_range=False):
        suffix = ""
        prefix = ""
        if high_range:
            suffix = '_HR'
        if emulator:
            prefix = '_Emu'
        for cfg in cfgs:
            eff_plot = getattr(self, cfg.name + prefix + "_eff" + suffix)

            twoD_plot = getattr(self, cfg.name + prefix + "_2D" + suffix)
            thresholds = THRESHOLDS.get(cfg.name)
            params = [
                cfg.on_title, cfg.off_title + " (GeV)", puBins, thresholds,
                200, cfg.min, cfg.max,
            ]
            if high_range:
                if "HT" in cfg.name:
                    params = [
                        cfg.on_title, cfg.off_title + " (GeV)", puBins, thresholds,
                        HIGH_RANGE_BINS_HT.size - 1, HIGH_RANGE_BINS_HT
                        ]
                else:
                    params = [
                        cfg.on_title, cfg.off_title + " (GeV)", puBins, thresholds,
                        HIGH_RANGE_BINS.size - 1, HIGH_RANGE_BINS
                        ]

            eff_plot.build(*params, legend_title=ETA_RANGES.get(cfg.name, ""))
            params.remove(thresholds)
            twoD_plot.build(*params)

            if high_range:
                continue
            res_plot = getattr(self, cfg.name + prefix + "_res" + suffix)
            res_plot.build(cfg.on_title, cfg.off_title,
                           puBins, 80, -3, 3, legend_title=ETA_RANGES.get(cfg.name, ""))

            if not hasattr(self, cfg.name + prefix + "_phi_res"):
                continue
            res_plot = getattr(self, cfg.name + prefix + "_phi_res")
            twoD_plot = getattr(self, cfg.name + prefix + "_phi_2D")
            twoD_plot.build(
                cfg.on_title + " Phi (rad)",
                cfg.off_title + " Phi (rad)",
                puBins, 100,
                -pi,
                2 * pi,
            )
            res_plot.build(
                cfg.on_title + " Phi",
                cfg.off_title + " Phi",
                puBins,
                100,
                -2 * pi,
                2 * pi,
                legend_title=ETA_RANGES.get(cfg.name, ""),
            )

    def fill_histograms(self, entry, event):

        offline, online = ExtractSums(event)
        pileup = event.nVertex

        for name in sum_types:
            if 'pfMET' in name and not pfMetFilter(event):
                continue
            on = online[name]
            off = offline[name]
            for suffix in ['_eff', '_res', '_2D', '_eff_HR', '_2D_HR']:
                getattr(self, name + suffix).fill(pileup, off.et, on.et)
            if hasattr(self, name + "_phi_res"):
                getattr(self, name + "_phi_res").fill(pileup, off.phi, on.phi)
                getattr(self, name + "_phi_2D").fill(pileup, off.phi, on.phi)

        goodPFJets = event.goodJets(jetFilter=pfJetFilter, doCalo=False)
        goodCaloJets = event.goodJets(jetFilter=None, doCalo=True)

        for pfJet in goodPFJets:
            l1Jet = event.getMatchedL1Jet(pfJet, l1Type='EMU')
            if not l1Jet:
                continue
            if pfJet.etCorr > 30.:
                self.res_vs_eta_CentralJets.fill(
                    pileup, pfJet.eta, pfJet.etCorr, l1Jet.et)

        leadingPFJet = event.getLeadingRecoJet(jetFilter=pfJetFilter, doCalo=False)
        leadingCaloJet = event.getLeadingRecoJet(jetFilter=None, doCalo=True)
        
        if leadingPFJet:

            pfL1EmuJet = event.getMatchedL1Jet(leadingPFJet, l1Type='EMU')
            if pfL1EmuJet:
                pfL1EmuJetEt = pfL1EmuJet.et
            else:
                pfL1EmuJetEt = 0.

            pfFillRegions = []
            if abs(leadingPFJet.eta) < 3.0:
                pfFillRegions = ['BE']
            else:
                pfFillRegions = ['HF']

            for region in pfFillRegions:
                for suffix in ['_eff', '_res', '_2D', '_eff_HR', '_2D_HR']:
                    if '_res' in suffix and pfL1EmuJetEt == 0:
                        continue
                    name = 'pfJetET_{0}_Emu{1}'.format(region, suffix)
                    getattr(self, name).fill(
                        pileup, leadingPFJet.etCorr, pfL1EmuJetEt,
                    )

            pfL1Jet = event.getMatchedL1Jet(leadingPFJet, l1Type='HW')
            if pfL1Jet:
                pfL1JetEt = pfL1Jet.et
            else:
                pfL1JetEt = 0.

            for region in pfFillRegions:
                for suffix in ['_eff', '_res', '_2D', '_eff_HR', '_2D_HR']:
                    if '_res' in suffix and pfL1JetEt == 0:
                        continue
                    name = 'pfJetET_{0}{1}'.format(region, suffix)
                    getattr(self, name).fill(
                        pileup, leadingPFJet.etCorr, pfL1JetEt,
                    )
                
        if leadingCaloJet:

            caloL1EmuJet = event.getMatchedL1Jet(leadingCaloJet, l1Type='EMU')
            if caloL1EmuJet:
                caloL1EmuJetEt = caloL1EmuJet.et
            else:
                caloL1EmuJetEt = 0.

            caloFillRegions = []
            if abs(leadingCaloJet.eta) < 3.0:
                caloFillRegions = ['BE']
            else:
                caloFillRegions = ['HF']


            for region in caloFillRegions:
                for suffix in ['_eff', '_res', '_2D', '_eff_HR', '_2D_HR']:
                    if '_res' in suffix and caloL1EmuJetEt == 0:
                        continue
                    name = 'caloJetET_{0}_Emu{1}'.format(region, suffix)
                    getattr(self, name).fill(
                        pileup, leadingCaloJet.etCorr, caloL1EmuJetEt,
                    )

            caloL1Jet = event.getMatchedL1Jet(leadingCaloJet, l1Type='HW')
            if caloL1Jet:
                caloL1JetEt = caloL1Jet.et
            else:
                caloL1JetEt = 0.

            for region in caloFillRegions:
                for suffix in ['_eff', '_res', '_2D', '_eff_HR', '_2D_HR']:
                    if '_res' in suffix and caloL1JetEt == 0:
                        continue
                    name = 'caloJetET_{0}{1}'.format(region, suffix)
                    getattr(self, name).fill(
                        pileup, leadingCaloJet.etCorr, caloL1JetEt,
                    )

        return True

    def make_plots(self):
        """
        Custom version, does what the normal one does but also overlays whatever you like.
        """
        #for plot in self.all_plots:
        #    plot.draw()

        getattr(self, 'caloHT_eff').draw()
        getattr(self, 'pfHT_eff').draw()
        getattr(self, 'caloMETBE_eff').draw()
        getattr(self, 'caloMETHF_eff').draw()
        getattr(self, 'pfMET_NoMu_eff').draw()
        getattr(self, 'caloJetET_BE_eff').draw()
        getattr(self, 'caloJetET_HF_eff').draw()
        getattr(self, 'pfJetET_BE_eff').draw()
        getattr(self, 'pfJetET_HF_eff').draw()

        getattr(self, 'caloHT_eff_HR').draw()
        getattr(self, 'pfHT_eff_HR').draw()
        getattr(self, 'caloMETBE_eff_HR').draw()
        getattr(self, 'caloMETHF_eff_HR').draw()
        getattr(self, 'pfMET_NoMu_eff_HR').draw()
        getattr(self, 'caloJetET_BE_eff_HR').draw()
        getattr(self, 'caloJetET_HF_eff_HR').draw()
        getattr(self, 'pfJetET_BE_eff_HR').draw()
        getattr(self, 'pfJetET_HF_eff_HR').draw()

        getattr(self, 'caloHT_res').draw()
        getattr(self, 'pfHT_res').draw()
        getattr(self, 'caloMETBE_res').draw()
        getattr(self, 'caloMETHF_res').draw()
        getattr(self, 'pfMET_NoMu_res').draw()
        getattr(self, 'caloJetET_BE_res').draw()
        getattr(self, 'caloJetET_HF_res').draw()
        getattr(self, 'pfJetET_BE_res').draw()
        getattr(self, 'pfJetET_HF_res').draw()


        #getattr(self, 'caloHT_eff').overlay_with_emu(getattr(self, 'caloHT_Emu_eff'))
        #getattr(self, 'pfHT_eff').overlay_with_emu(getattr(self, 'pfHT_Emu_eff'))
        #getattr(self, 'caloMETBE_eff').overlay_with_emu(getattr(self, 'caloMETBE_Emu_eff'))
        #getattr(self, 'caloMETHF_eff').overlay_with_emu(getattr(self, 'caloMETHF_Emu_eff'))
        #getattr(self, 'pfMET_NoMu_eff').overlay_with_emu(getattr(self, 'pfMET_NoMu_Emu_eff'))
        #getattr(self, 'caloJetET_BE_eff').overlay_with_emu(getattr(self, 'caloJetET_BE_Emu_eff'))
        #getattr(self, 'caloJetET_HF_eff').overlay_with_emu(getattr(self, 'caloJetET_HF_Emu_eff'))
        #getattr(self, 'pfJetET_BE_eff').overlay_with_emu(getattr(self, 'pfJetET_BE_Emu_eff'))
        #getattr(self, 'pfJetET_HF_eff').overlay_with_emu(getattr(self, 'pfJetET_HF_Emu_eff'))

        #getattr(self, 'caloHT_res').overlay_with_emu(getattr(self, 'caloHT_Emu_res'))
        #getattr(self, 'pfHT_res').overlay_with_emu(getattr(self, 'pfHT_Emu_res'))
        #getattr(self, 'caloMETBE_res').overlay_with_emu(getattr(self, 'caloMETBE_Emu_res'))
        #getattr(self, 'caloMETHF_res').overlay_with_emu(getattr(self, 'caloMETHF_Emu_res'))
        #getattr(self, 'pfMET_NoMu_res').overlay_with_emu(getattr(self, 'pfMET_NoMu_Emu_res'))
        #getattr(self, 'caloJetET_BE_res').overlay_with_emu(getattr(self, 'caloJetET_BE_Emu_res'))
        #getattr(self, 'caloJetET_HF_res').overlay_with_emu(getattr(self, 'caloJetET_HF_Emu_res'))
        #getattr(self, 'pfJetET_BE_res').overlay_with_emu(getattr(self, 'pfJetET_BE_Emu_res'))
        #getattr(self, 'pfJetET_HF_res').overlay_with_emu(getattr(self, 'pfJetET_HF_Emu_res'))

        return True

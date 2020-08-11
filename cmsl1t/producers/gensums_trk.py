from __future__ import division
from cmsl1t.energySums import EnergySum, Met
from .base import BaseProducer


class Producer(BaseProducer):

    def __init__(self, inputs, outputs, **kwargs):
        self._expected_input_order = ['genMet']
        super(Producer, self).__init__(inputs, outputs, **kwargs)

    def produce(self, event):
        setattr(event, self._outputs[0] + '_MetBE', Met(event['L1TrkMET_GenMet'], event['L1TrkMET_GenMetPhi']))
        setattr(event, self._outputs[0] + '_MetHF', Met(event['L1TrkMET_GenMet'], event['L1TrkMET_GenMetPhi']))
        setattr(event, self._outputs[0] + '_HT', EnergySum(event['L1TrackJet_GenJetHt']))

        return True

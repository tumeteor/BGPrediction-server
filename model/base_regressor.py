import time
import logging
import pandas as pd
from feature_manager import FeatureManager
import numpy as np
import matplotlib.dates as md
from utils.dbutil import DBConnector


class BaseRegressor(object):

    def __init__(self, patientId):
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.DEBUG)
        self.log = logging.getLogger("BaseClassifier")

        dbc = DBConnector(patientId=patientId)
        self.glucoseData, self.insulinData, self.carbData, self.activityData = dbc.loadAllData()

        ###### LOAD Feature Extraction ####
        self.Features = FeatureManager(self.glucoseData, self.insulinData, self.carbData,
                                       self.activityData, self.patientId)
        # tuning option for RF
        # set it now as a common parameter
        # for all models
        self.tune = False
        # parameters
        self.split_ratio = .66
        self.look_back = 8
        self._plotLearnedModel = False

        # customize feature set option
        # TODO: set from outside
        self._customizeFeatureSet = False

        self._allFeatureDesp = list()


    def train(self):
        raise NotImplementedError()

    def extractFeatures(self, customizeFeatureSet=False, customGroup=None):
        X, Y = self.Features.buildFeatureMatrix(self.look_back)
        if customGroup != None:
            return self.Features.customFeatureGroup(X, customGroup), Y
        if not customizeFeatureSet:
            return X, Y
        else:
            new_X, desp = self.Features.customFeatureGroupSubset(X)
            return new_X, Y, desp

    def loadInstance(self):
        return self.Features.getNextInstance()

    def extractFeatures(self, i):
        return self.Features.extractFeaturesforOneInstance(i, look_back=self.look_back)

import six.moves.cPickle as pickle
from training_job import TrainingManager
import os
import logging
import datetime
from utils.dbutil import DBConnector
from model.feature_manager import FeatureManager
import numpy as np

class PredictionManager:

    def __init__(self, patientId):
        # configure log
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.INFO)
        self.log = logging.getLogger("PredictionManager")
        self.dbc = DBConnector(patientId=patientId)
        self.patientId = patientId
        self.log.info("Start loading data from DB.")
        self.glucoseData, self.insulinData, self.carbData, self.activityData = self.dbc.loadAllData()
        self.log.info("End loading data from DB.")
        self.look_back = 8

        ###### LOAD Feature Extraction ####
        self.Features = FeatureManager(self.glucoseData, self.insulinData, self.carbData,
                                       self.activityData)

    def load_model(self):
        with open(TrainingManager.PICKELPATH + self.patientId + ".pkl", 'rb') as f:
            self.rf = pickle.load(f)


    def predictJob(self):
        if os.path.isfile(TrainingManager.PICKELPATH + self.patientId + ".pkl"):
            self.log.info("model serialization exists.")
        else: return
        self.load_model()
        nextIns = self.getNextInstanceIndex()# get the index of the next bg
        '''
        check if there is a new blood glucose measurements
        only predict if there is a new BG input in between job interval
        '''
        if self.check_criterias_for_prediction():
            instance = self.extractFeaturesForOneInstance(nextIns)
            bg_prediction = self.rf.predict(instance)
            self.storePrediction(self.patientId, bg_prediction)
        else:
            return

    def check_criterias_for_prediction(self):
        self.log.info("cheking predicting criterias:")
        # check if the trained model exists
        # check criterias
        return self.check_time_gap()

    def check_time_gap(self):
        # check time gap from the last
        # measurement, must be at least 1 hour
        lastTime = self.getLastBGMeasurement()
        curTime = datetime.datetime.utcnow()
        timeGap = curTime - lastTime
        return timeGap.seconds > TrainingManager.MIN_TIME_GAP

    def getNextInstanceIndex(self):
        return len(self.glucoseData) - 1

    def getLastBGMeasurement(self):
        return self.glucoseData[-2]['time']

    def extractFeaturesForOneInstance(self, i):
        ins_features = np.array(self.Features.extractFeaturesForOneInstance(i, look_back=self.look_back))
        ins_features = np.reshape(ins_features, (-1, len(ins_features)))
        return ins_features


    def storePrediction(self, patientId, score):
        self.dbc.storePrediction(patientId=patientId, score=score, ptype="regression")





import six.moves.cPickle as pickle
from training_job import TrainingManager
import os
import logging
import datetime

class PredictionManager:

    def __init__(self):
        # configure log
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.INFO)
        self.log = logging.getLogger("PredictionManager")

    def load_model(self, patientId):
        with open(TrainingManager.PICKELPATH + patientId + ".pkl", 'rb') as f:
            self.rf = pickle.load(f, encoding="bytes")


    def predictJob(self, patientId):
        if os.path.isfile(TrainingManager.PICKELPATH + patientId + ".pkl"):
            self.log("model serialization exists.")
        else: return
        self.load_model(patientId)
        nextIns = self.rf.getNextInstanceIndex() # get the index of the next bg
        instance = self.rf.extractFeaturesForOneInstance(nextIns)
        if self.check_criterias_for_prediction():
            bg_prediction = self.rf.predictJob(instance)
            self.rf.dbc.storePrediction(patientId=patientId, score=bg_prediction)
        else:
            return

    def check_criterias_for_prediction(self):
        # check if the trained model exists
        # check criterias
        return os.path.isfile(TrainingManager.PICKELPATH) and self.check_time_gap()

    def check_time_gap(self):
        # check time gap from the last
        # measurement
        lastTime = self.rf.getLastBGMeasurement()
        curTime = datetime.datetime.utcnow()
        timeGap = curTime - lastTime
        return timeGap.seconds > TrainingManager.MIN_TIME_GAP



    def storePrediction(self, dbc, patientId, score):
        dbc.storePrediction(patientId=patientId, score=score, ptype="regression")





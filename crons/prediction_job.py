import pickle
from training_job import TrainingManager
import os
import logging

class PredictionManager:

    def __init__(self):
        # configure log
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.INFO)
        self.log = logging.getLogger("PredictionManager")

    def load_model(self, patientID):

        f = open(TrainingManager.PICKELPATH + patientID + ".pkl", 'rb')
        self.rf = pickle.load(f, encoding="bytes")

    @property
    def predictJob(self, patientId):
        self.load_model(patientId)
        nextIns = self.rf.loadInstance() # get the index of the next bg
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
        pass


    def storePrediction(self, dbc, patientId, score):
        dbc.storePrediction(patientId=patientId, score=score, ptype="regression")





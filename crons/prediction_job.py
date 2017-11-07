import pickle
from training_job import TrainingManager
import os

class PredictionManager:

    def __init__(self): pass

    def load_model(self, patientID):
        f = open(TrainingManager.PICKELPATH, 'rb')
        self.rf = pickle.load(f, encoding="bytes")

    @property
    def predict(self):
        nextIns = self.rf.loadInstance()
        instance = self.rf.extractFeatures(nextIns)
        if self.check_criterias():
            prediction = self.rf.predict(instance)
            return prediction
        else:
            return

    def check_criterias(self):
        return os.path.isfile(TrainingManager.PICKELPATH) and self.check_time_gap()

    def check_time_gap(self):
        # check time gap from the last
        # measurement
        pass

    def storePrediction(self):
        pass




import pickle
from training_job import TrainingManager

class PredictionManager:

    def __init__(self): pass

    def loadModel(self):
        f = open(TrainingManager.PICKELPATH, 'rb')
        self.rf = pickle.load(f, encoding="bytes")

    def predict(self):
        nextIns = self.rf.loadInstance()
        instance = self.rf.extractFeatures(nextIns)
        prediction = self.rf.predict(instance)




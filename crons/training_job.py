import pickle

from model.rf import RandomForest
import logging

class TrainingManager:

    PICKELPATH = '/home/glycorec/BGPrediction-server/persistence/'

    STDDEV_THRSHD = None
    CONFIDENT_THRSHD = None
    MIN_SIZE = 25

    def __init__(self):
        # configure log
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.INFO)
        self.log = logging.getLogger("TrainingManager")

    def trainingJob(self, patientId):
        self.rf = RandomForest(patientId=patientId,modelName="rf")
        self.rf.loadData()

        if (self.check_criterias_for_training()):
            self.rf.train()
            self.pickling(patientId)

    def pickling(self, patientId):
        pickle.dumps(self.rf, self.PICKELPATH + patientId + ".pkl", pickle.DEFAULT_PROTOCOL)

    def check_criterias_for_training(self):
        std, conf = self.rf.getStdDevAndConfidence()
        size = self.rf.getTrainingSize()

        return std > self.STDDEV_THRSHD and conf > self.CONFIDENT_THRSHD \
               and size > self.MIN_SIZE










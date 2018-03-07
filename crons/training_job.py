import six.moves.cPickle as pickle

from model.rf import RandomForest
import logging

class TrainingManager:

    PICKELPATH = '/home/glycorec/BGPrediction-server/persistence/'

    STDDEV_THRSHD = 0.5
    CONFIDENT_THRSHD = 0
    MIN_SIZE = 7
    MIN_TIME_GAP = 60 * 60

    def __init__(self):
        # configure log
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.INFO)
        self.log = logging.getLogger("TrainingManager")

    def trainingJob(self, patientId):
        self.rf = RandomForest(patientId=patientId,modelName="rf")
        self.rf.loadData()

        if (self.check_criterias_for_training()):
            self.log.info("start training for patientId: {}".format(patientId))
            self.rf.train()
            self.pickling(patientId)
    def getTrainingSize(self):
        return len(self.rf.glucoseData)

    def pickling(self, patientId):
        with open(self.PICKELPATH + patientId + ".pkl", 'wb') as file:
            pickle.dump(self.rf.rf, file, 2)


    def check_criterias_for_training(self):
        if self.rf.getTrainingSize() < self.MIN_SIZE: return False
        std = self.rf.getStdDevAndConfidence()

        print("confident interval: {}".format(std))


        return std < self.STDDEV_THRSHD










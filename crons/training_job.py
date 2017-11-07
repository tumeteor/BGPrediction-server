import pickle

from model.rf import RandomForest
from utils.dbutil import DBConnector


class TrainingManager:

    PICKELPATH = 'rf.pkl'

    STDDEV_THRSHD = None
    CONFIDENT_THRSHD = None
    MIN_SIZE = 25

    def __init__(self):
        self.dbc = DBConnector()

    def training(self, patientId):
        self.rf = RandomForest(patientId=patientId,
                          dbConnection=self.dbc.cnx)
        self.rf.loadData()

        if (self.check_criterias()):
            self.rf.train()
            self.pickling()

    def pickling(self):
        pickle.dumps(self.rf, self.PICKELPATH, pickle.DEFAULT_PROTOCOL)

    def check_criterias(self):
        std, conf = self.rf.getStdDevAndConfidence()
        size = self.rf.getTrainingSize()

        return std > self.STDDEV_THRSHD and conf > self.CONFIDENT_THRSHD \
               and size > self.MIN_SIZE










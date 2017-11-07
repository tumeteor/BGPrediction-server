import pickle

from model.rf import RandomForest
from utils.dbutil import DBConnector


class TrainingManager:

    PICKELPATH = 'rf.pkl'

    def __init__(self):
        self.dbc = DBConnector()

    def training(self, patientId):
        self.rf = RandomForest(patientId=patientId,
                          dbConnection=self.dbc.cnx)
        self.rf.train()


    def pickling(self):
        pickle.dumps(self.rf, self.PICKELPATH, pickle.DEFAULT_PROTOCOL)







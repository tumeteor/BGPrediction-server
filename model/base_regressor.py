import logging
from model.feature_manager import FeatureManager
from utils.dbutil import DBConnector
from utils.timeutil import str_to_datetime


class BaseRegressor(object):

    def __init__(self, patientId):
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.DEBUG)
        self.log = logging.getLogger("BaseClassifier")

        self.dbc = DBConnector(patientId=patientId)
        self.log.info("Start loading data from DB.")
        self.glucoseData, self.insulinData, self.carbData, self.activityData = self.dbc.load_all_data()
        self.log.info("End loading data from DB.")

        ###### LOAD Feature Extraction ####
        self.features = FeatureManager(self.glucoseData, self.insulinData, self.carbData,
                                       self.activityData)
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
        self._customize_feature_set = False

        self._all_feature_desp = list()

    def train(self):
        raise NotImplementedError()

    def extract_features(self, customize_feature_set=False, custom_group=None):
        X, Y = self.features.build_feature_matrix(self.look_back)
        if custom_group is not None:
            return self.features.custom_feature_group(X, custom_group), Y
        if not customize_feature_set:
            return X, Y
        else:
            new_X, desp = self.features.customFeatureGroupSubset(X)
            return new_X, Y, desp

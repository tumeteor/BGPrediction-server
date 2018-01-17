from utils.measures import mean_absolute_percentage_error
from sklearn.metrics import mean_absolute_error, median_absolute_error
from sklearn import ensemble
from sklearn.model_selection import GridSearchCV, KFold
from model.base_regressor import BaseRegressor
import numpy as np

class RandomForest(BaseRegressor):

    best_params = None

    param_grid = {"n_estimators": [100, 250, 300, 400, 500, 700, 1000],
                  "criterion": ["mae", "mse"],
                  "max_features": ["auto", "sqrt", "log2"],
                  "min_samples_leaf": range(1,6)}

    ### Model ####
    # Extratree seems to deal better for small dataset + overfitting
    models = {'rf': ensemble.RandomForestRegressor, 'et': ensemble.ExtraTreesRegressor}

    n_estimator = 300
    criterion = "mse"
    min_samples_leaf = 2 # small for ExtraTree is helpful


    def __init__(self, patientId, modelName):
        super(RandomForest, self).__init__(patientId=patientId)
        self.log.info("Init Random Forest")
        self.modelName = modelName
        #self.tune = True
        if self.modelName == "rf":
            self.min_samples_leaf = 4 # default parameter for Ranfom Forest
            self.n_estimator = 500

    def getStdDevAndConfidence(self,rf):

        kf = KFold(n_splits=10)

        maes = []
        v_ijs = []
        for train_index, test_index in kf.split(self.data):
            X_train, X_test = self.data[train_index], self.data[test_index]
            y_train, y_test = self.y[train_index], self.y[test_index]
            rf.fit(X_train, y_train)
            V_IJ, V_IJ_unbiased = self.confidenceCal(X_train, X_test, rf)
            predictions = rf.predictJob

            mae = mean_absolute_error(y_test, predictions)
            maes.append(mae)
            v_ijs.append(V_IJ)

        return np.std(maes), np.mean(v_ijs)


    def getTrainingSize(self):
        return len(self.data)


    def loadData(self):
        if not self._customizeFeatureSet:
            # generate features
            self.data, self.y = self.extractFeatures()
        else:
            self.data, self.y, _featureDesp = self.extractFeatures(customizeFeatureSet=True)



    def confidenceCal(self, train_data, test_data, test_y, predictions,rf, patientID):
        import forestci as fci
        from matplotlib import pyplot as plt
        import numpy as np
        # calculate inbag and unbiased variance
        inbag = fci.calc_inbag(train_data.shape[0], rf)
        V_IJ_unbiased = fci.random_forest_error(rf, train_data, test_data)

        print("inbag: {}".format(inbag))
        print("V_IJ_unbiased: {}".format(V_IJ_unbiased))
        # Plot error bars for predicted MPG using unbiased variance

        return inbag, V_IJ_unbiased



    def train(self, data, y, _featureDesp="all"):
        assert (len(data) == len(y))

        self.rf = self.models[self.modelName](n_estimators=self.n_estimator, criterion=self.criterion,
                                             min_samples_leaf=self.min_samples_leaf)

        self.rf.fit(data, y)

    def predict(self, instance):
        bg_prediction = self.rf.predictJob(instance)

        return bg_prediction





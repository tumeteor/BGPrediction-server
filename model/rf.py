from utils.measures import mean_absolute_percentage_error
from sklearn.metrics import mean_absolute_error, median_absolute_error
from sklearn import ensemble
from sklearn.model_selection import GridSearchCV, KFold
from model.base_regressor import BaseRegressor

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


    def __init__(self, patientId, dbConnection, modelName):
        super(RandomForest, self).__init__(patientId, dbConnection)
        self.modelName = modelName
        #self.tune = True
        if self.modelName == "rf":
            self.min_samples_leaf = 4 # default parameter for Ranfom Forest
            self.n_estimator = 500


    def train(self):
        if not self._customizeFeatureSet:
            # generate features
            data, y = self.extractFeatures()
        else:
            data, y, _featureDesp = self.extractFeatures(customizeFeatureSet=True)
        return self.trainWithData(data, y)


    def confidenceCal(self, train_data, test_data, test_y, predictions,rf, patientID):
        import forestci as fci
        from matplotlib import pyplot as plt
        import numpy as np
        # calculate inbag and unbiased variance
        inbag = fci.calc_inbag(train_data.shape[0], rf)
        V_IJ_unbiased = fci.random_forest_error(rf, train_data, test_data)

        print "inbag: {}".format(inbag)
        print "V_IJ_unbiased: {}".format(V_IJ_unbiased)
        # Plot error bars for predicted MPG using unbiased variance
        (_, caps, _) = plt.errorbar(predictions, test_y, yerr=np.sqrt(V_IJ_unbiased), fmt='o', markersize=4, capsize=10, mfc='red',
         mec='green')
        for cap in caps:
            cap.set_markeredgewidth(1)
        plt.title('Error bars for Patient: ' + str(patientID))

        plt.xlabel('Actual BG')
        plt.ylabel('Predicted BG')
        plt.savefig("prediction/tmp/confidence_intervals_patient{}_4.png".format(self.patientId))
        plt.close()

        return inbag, V_IJ_unbiased



    def trainWithData(self, data, y, _featureDesp="all"):
        assert (len(data) == len(y))

        self.rf = self.models[self.modelName](n_estimators=self.n_estimator, criterion=self.criterion,
                                             min_samples_leaf=self.min_samples_leaf)

        self.rf.fit(data, y)

    def predict(self, instance): pass





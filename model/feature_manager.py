import datetime
from utils.timeutil import getTimeBinInt
from utils.measures import mean
from utils.timeutil import tohour
import numpy as np
import logging
from itertools import chain, combinations
from sklearn.model_selection import cross_val_score
from sklearn import preprocessing


class FeatureManager:
    """
    Class for feature manager
    Add new features here
    """

    def __init__(self, glucoseData, insulinData, carbData, activityData):
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.INFO)
        self.log = logging.getLogger("FeatureManager")

        self.horizon_minutes = 60

        self.glucoseData = glucoseData
        self.insulinData = insulinData
        self.carbData = carbData
        self.activityData = activityData

        self.n_samples = len(self.glucoseData)

        # insulin decay params
        self.gamma = {"basal": 0.5,
                      "rapid": 0.7,
                      "misch": 0.3}

        self.carbRate = 0.5

        self.featureNames = list()

        '''
        assign features into groups, each feature can be assigned to a (or many) group(s)
        that is declared here
        '''

        FeatureGroup.groups = list()
        self.contextFeatureGroup = FeatureGroup(name="Time")
        self.carbFeatureGroup = FeatureGroup(name="Carb")
        self.insulinFeatureGroup = FeatureGroup(name="Insulin")
        self.glucoseFeatureGroup = FeatureGroup(name="Glucose")
        self.activityFeatureGroup = FeatureGroup(name="Activity")

        self._storedGroupIndices = False

    def toTimeBin(self, t):
        """
        Feature time of day
        :param t:
        :return: time period of day
        """
        # TODO: rename method
        timeBinFeature = Feature("timeBin", getTimeBinInt(t))
        self.contextFeatureGroup.addFeature(timeBinFeature)


    def aggregateHistory(self, prev_glucose, cur_time, next_time):
        """
        :param cur_time, next_time:
        :return: average of previous glucose values,
                 rolling average of previous glucose values
        """
        # previous values
        # avg of previous glucose values
        # TODO: rename method
        avgGlucose = mean([p['value'] for p in prev_glucose])
        avgGlucoseFeature = Feature("avgGlucose", avgGlucose)
        self.glucoseFeatureGroup.addFeature(avgGlucoseFeature)
        # previous glucose values (average of last hour) Note: remove since it is covered by the other method for now
        delta = datetime.timedelta(hours=1)
        prevGlucose = mean([a['value'] for a in prev_glucose if a['value'] and a['time'] >= (cur_time - delta)])
        prevGlucoseFeature = Feature("prevGlucose", prevGlucose)
        self.activityFeatureGroup.addFeature(prevGlucoseFeature)

        # TODO: trend?
        # avg of previous glucose values in same time bin
        # features.append(avg([p['value'] for p in prev_glucose if getTimeBinInt(p['time']) == cur_time_bin]))
        # decreasing weight w/ difference in time
        avg_prev = 0.0
        avg_prev_w = 0.0
        for prev in prev_glucose:
            t1 = min(next_time.hour, prev['time'].hour)
            t2 = max(next_time.hour, prev['time'].hour)
            time_diff = min(t2 - t1, t1 + 24 - t2) # <= 12
            #t_w = 1.0 / 12.0 * time_diff
            t_w = np.exp(-time_diff)
            avg_prev += t_w * prev['value']
            avg_prev_w += t_w
        timeWeightAvgGlucose = avg_prev / avg_prev_w if len(prev_glucose) != 0 else 0

        timeWeightAvgGlucoseFeature = Feature("timeWeightAvgGlucose", timeWeightAvgGlucose)
        self.glucoseFeatureGroup.addFeature(timeWeightAvgGlucoseFeature)

    def insulinDecayConcentration(self, c0, timedelta, type):
        """
        assume that the drug is administered intravenously, so that the concentration of the drug
        in the bloodstream jumps almost immediately to its highest level.
        The concentration of the drug then decays exponentially.
        :param c: concentration at t0
        :param timedelta: time distance at t0 + delta
        :param type: insulin type [basal, rapid, misch]
        :return: concentration at t0 + delta
        """
        ct = c0 * np.exp(-self.gamma[type] * tohour(timedelta))
        if ct < 0.001: ct = 0
        return ct

    def carbLinearAbsorption(self, c0, timedelta):
        """
        https://diyps.org/2014/05/29/determining-your-carbohydrate-absorption-rate-diyps-lessons-learned/
        :param c0:
        :param timedelta:
        :return:
        """

        ct = - self.carbRate * tohour(timedelta) + c0
        if ct < 0: ct = 0

        return ct

    def aggregateRecentHistory(self, look_back, prev_glucose, prev_insulin, prev_carbs, prev_activity, cur_time):
        """
        add aggregated features for recent history
        :param look_back: window size
        :param prev_insulin:
        :param prev_carbs:
        :param prev_activity:
        :param cur_time:
        :return: 5 * (look_back + 1) features
        """
        features = list()

        for k in range(1, look_back + 1):
            delta = datetime.timedelta(hours=k)
            # sum of activity in last k hours
            sumAc = sum([a['value'] for a in prev_activity if a['value'] and a['time'] >= (cur_time - delta)])
            sumAcFeature = Feature("sumActivityLast_{}".format(k), sumAc)
            self.activityFeatureGroup.addFeature(sumAcFeature)
            # sum of insulin in last k hours
            sumIl = sum([i['value'] for i in prev_insulin if i['value'] and i['time'] >= (cur_time - delta)])
            sumIlFeature = Feature("sumInsulinLast_{}".format(k),sumIl)
            self.insulinFeatureGroup.addFeature(sumIlFeature)
            # sum of carbs in last k hours
            sumCarb = sum([c['value'] for c in prev_carbs if c['value'] and c['time'] >= (cur_time - delta)])
            sumCarbFeature = Feature("sumCarbLast_{}".format(k),sumCarb)
            self.carbFeatureGroup.addFeature(sumCarbFeature)
            # sum of carbs in last k hours
            #if (k-1)%2 and k <= 3: # having too many features
            #    avgGlucose = mean([c['value'] for c in prev_glucose if c['value'] and c['time'] >= (cur_time - delta)])
            #    avgGlucoseFeature = Feature("avgGlucoseLast_{}".format(k),avgGlucose)
            #    self.carbFeatureGroup.addFeature(avgGlucoseFeature)

            ##### insulin decay feature ####
            #  [self.log.debug("insulin type {}".format(i['type']))  for i in  prev_insulin if i['value'] and i['time'] >= (cur_time - delta)]

            sumDecayIn = sum([self.insulinDecayConcentration(i['value'], (cur_time - i['time']), i['type']) for i in
                     prev_insulin if
                     i['value'] and i['time'] >= (cur_time - delta)])
            sumDecayInFeature = Feature("sumInsulinDecayLast_{}".format(k),sumDecayIn)
            self.insulinFeatureGroup.addFeature(sumDecayInFeature)

            # absorbed insulin: difference between decay and sum of insulin
            # TODO: comment in when we can speficy to ignore for certain models; rf suffers from too many features
            #absIn = sumIl - sumDecayIn
            #self.featureGroups.get(self.Insulin).addFeature("absorbedInsulinLast_{}".format(k), absIn)

            ### carb absorption ####
            ### high feature importance but reduce prediction performance ####

            sumDecayCarb = sum([self.carbLinearAbsorption(c['value'], (cur_time - c['time'])) for c in
                      prev_carbs if
                      c['value'] and c['time'] >= (cur_time - delta)])
            sumDecayCarbFeature = Feature("sumCarbAbsorptionLast_{}".format(k), sumDecayCarb)
            self.carbFeatureGroup.addFeature(sumDecayCarbFeature)

            # absorbed carbs: difference between sum of eaten carbs and decayed carbs
            # TODO: comment in when we can specify to ignore for certain models; rf suffers from too many features
            #absCarbs = sumCarb - sumDecayCarb
            #self.featureGroups.get(self.Carb).addFeature("absorbedCarbsLast_{}".format(k), absCarbs)

        return features


    '''
    Exhaustive search for best feature subset
    '''
    def featureExhaustiveBestSubset(self, estimator, X, y, lvl=None):
        '''
        X: feature matrix
        lvl: expected size of subset
        :return: all possible subsets
        '''
        n_features = X.shape[1]
        subsets = chain.from_iterable(combinations(xrange(n_features), k + 1)
                                      for k in xrange(n_features))

        best_score = -np.inf
        best_subset = None
        for subset in subsets:
            if lvl != None and lvl < n_features:
                if len(subset) != lvl: continue
            score = cross_val_score(estimator, X[:, subset], y, scoring='neg_mean_absolute_errors').mean()
            if score > best_score:
                best_score, best_subset = score, subset

        return best_subset, best_score

    def FeatureGroupBestSubset(self, estimator,X ,y):
        '''
        :param estimator:
        :param X:
        :param y:
        :return:
        '''
        n_groups = len(FeatureGroup.groups)
        subsets = chain.from_iterable(combinations(xrange(n_groups), k + 1)
                                      for k in xrange(n_groups))

        best_score = -np.inf
        best_subset = None
        for subset in subsets:
            self.log.info("Feature group subset: {}".format(subset))
            sub_feature_set = set()
            for groupIdx in subset:
                grp = FeatureGroup.groups[groupIdx]
                sub_feature_set = sub_feature_set.union(grp.getFeatureIndices())
            sub_feature_set = list(sub_feature_set)
            score = cross_val_score(estimator, X[:, sub_feature_set], y, scoring='neg_mean_absolute_errors').mean()

            self.log.info("Feature subset indices: {}".format(sub_feature_set))
            if score > best_score:
                best_score, best_subset = score, subset
        return best_subset, best_score


    def FeatureGroupAllSubsets(self, X, lvl=2):
        '''
        :param X:
        :return:
        '''
        n_groups = len(FeatureGroup.groups)
        subsets = chain.from_iterable(combinations(xrange(n_groups), k + 1)
                                      for k in xrange(n_groups))
        _allSubsets = {}
        for subset in subsets:
            if lvl != None and lvl < n_groups:
                if len(subset) != lvl: continue
            self.log.info("Feature group subset: {}".format(subset))
            sub_feature_set = set()
            feature_desp = ""
            for groupIdx in subset:
                grp = FeatureGroup.groups[groupIdx]
                sub_feature_set = sub_feature_set.union(grp.getFeatureIndices())
                feature_desp += grp.name + " ({} features),".format(grp.size())
            self.log.info("Feature subset indices: {}".format(sub_feature_set))
            sub_feature_set = list(sub_feature_set)
            _allSubsets[subset] = (X[:,sub_feature_set],feature_desp)
        return _allSubsets


    def customFeatureGroup(self, X, groupIdx):
        '''
        :param X:
        :param featureIndices:
        :return: X with selected features
        '''

        grp = FeatureGroup.groups[groupIdx]
        featureIndices = grp.getFeatureIndices()
        return X[:,featureIndices]


    def getFeatureList(self):
        features = list()

        for feature in Feature.allFeatureList:
            features.append(feature.value)
        return features


    def extractFeaturesForOneInstance(self, i, look_back):
        # time of predicted value
        next_time = self.glucoseData[i]['time']
        # current time
        cur_time = next_time - datetime.timedelta(minutes=self.horizon_minutes)

        # Note 05/11/17: all filtering for predictions with gap less than k hours
        last_time = self.glucoseData[i - 1]['time']

        delta_time = next_time - last_time
        # if delta_time.seconds > 2 * 60 * 60: continue

        # labels.append(self.glucoseData[i])

        # observed data
        prev_glucose = [item for item in self.glucoseData[:i] if item['time'] <= cur_time]
        prev_insulin = [item for item in self.insulinData if item['time'] <= cur_time]
        prev_carbs = [item for item in self.carbData if item['time'] <= cur_time]
        prev_activity = [item for item in self.activityData if item['time'] <= cur_time]

        '''
        feature to group addition
        '''
        self.toTimeBin(next_time)
        # self.fixedModel(ie=prev_insulin[-1]['value'], bz=prev_glucose[-1]['value'], carb=prev_carbs[-1]['value'],
        # il_case=prev_insulin[-1]['type'], t=cur_time)
        self.aggregateHistory(prev_glucose, cur_time, next_time)
        self.aggregateRecentHistory(look_back, prev_glucose, prev_insulin, prev_carbs, prev_activity, cur_time)

        features = self.getFeatureList()



        self.log.debug("number of features: {}".format(len(features)))
        return features


    '''
    Combining features here for each glucose instance
    '''
    def buildFeatureMatrix(self, look_back):
        """
        Extract features from glucose, insulin, carbs, and activity data.
        :return: Feature matrix with all available features
        """
        self.log.info("Extract features")

        result = list()
        # generate one instance per glucose value, starting with the second
        labels = list()
        for i in range(1, self.n_samples):

            features = self.extractFeaturesForOneInstance(i, look_back)
            result.append(features)



        #assert (len(result) == self.n_samples -1) # skip the first sample
        if len(result) > 0:
            self.log.debug("Build feature matrix with {} features.".format(len(result[0])))
            self.log.debug([feature.name for feature in list(set.union(*map(set,[group.group for group in FeatureGroup.groups])))])
        return preprocessing.normalize(np.array(result)), \
               np.array(labels)
               #np.array([row['value'] for row in self.glucoseData[1:]])

    def getNextInstance(self):
        # return the idx of the next bg measurement

        return self.n_samples


class FeatureGroup:
    groups = list()

    def __init__(self, name):
        self.group = set()
        self.name = name
        if not self in FeatureGroup.groups: FeatureGroup.groups.append(self)

    def addFeature(self, feature):
        self.group.add(feature)

    def getFeatureIndices(self):
        featureIndices = list()
        for feature in self.group:
            featureIndices.append(feature.getFeatureIdx())
        return featureIndices

    def size(self): return len(self.group)
    def emptyGroup(self): self.group = list()



class Feature:
    allFeatureList = list()

    def __init__(self, name, value):
        self.name = name
        self.value = value
        if self in Feature.allFeatureList:
            # feature objects are compared by name
            # this will remove the object with old value
            Feature.allFeatureList.remove(self)
            # this will append the object with new value
            Feature.allFeatureList.append(self)
        else:
            Feature.allFeatureList.append(self)


    def getFeatureIdx(self):
        return self.allFeatureList.index(self)

    def modifyValue(self, newValue):
        self.value = newValue

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.name == other.name

    def __hash__(self):
        return hash(self.name)







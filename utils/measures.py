import numpy as np


def mean_absolute_percentage_error(groundtruth, predictions):
    """
    Compute symmertric mean absolute percentage error (SMAPE)
    :param groundtruth: the list of ground truths
    :param predictions: the list of predictions
    :return: SMAPE value
    """
    gt = np.array(groundtruth)
    pred = np.array(predictions)
    errors = np.abs(pred - gt)
    averages = (np.abs(gt) + np.abs(pred)) / 2.0
    return 100.0 * np.mean(errors / averages)


def median_absolute_error(groundtruth, predictions):
    """
    Compute median absolute error (MdAE)
    :param groundtruth: the list of ground truths
    :param predictions: the list of predictions
    :return: MdAE
    """
    gt = np.array(groundtruth)
    pred = np.array(predictions)
    return np.abs(pred - gt)


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

from apscheduler.schedulers.blocking import BlockingScheduler
from crons.prediction_job import PredictionManager
from crons.training_job import TrainingManager

if __name__ == '__main__':
    scheduler = BlockingScheduler()



from apscheduler.schedulers.blocking import BlockingScheduler
from crons.prediction_job import PredictionManager
from crons.training_job import TrainingManager
import datetime

if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='UTC')
    scheduler.add_executor('processpool')
    trainMan = TrainingManager()
    predMan = PredictionManager()

    patientIDs = []

    for patient in patientIDs:
        scheduler.add_job(trainMan.training(patientId=patient), 'inteval',
                          next_run_time=datetime.now(), minutes=30)

        scheduler.add_job(predMan.predict(), 'interval',
                          next_run_time=datetime.now(), minutes=10)

    try:
        scheduler.start()
    except (SystemExit):
        pass






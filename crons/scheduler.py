from apscheduler.schedulers.blocking import BlockingScheduler
from crons.prediction_job import PredictionManager
from crons.training_job import TrainingManager
import datetime

if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='UTC')
    scheduler.add_executor('processpool')
    trainMan = TrainingManager()
    predMan = PredictionManager()

    patientIds = ['00bd6e5f-d918-4e9f-9699-d96e5a6220ef', '04828d88-0cfc-46f8-a2a6-6aaff400fbcc']

    # add cron job for each patient
    for patientId in patientIds:
        scheduler.add_job(trainMan.trainingJob(patientId=patientId), 'interval',
                          next_run_time=datetime.now(), minutes=30)

        scheduler.add_job(predMan.predictJob(patientId=patientId), 'interval',
                          next_run_time=datetime.now(), minutes=10)

    try:
        print("Start Scheduler.")
        scheduler.start()
    except (SystemExit):
        pass






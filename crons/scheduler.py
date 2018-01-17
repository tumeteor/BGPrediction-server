from apscheduler.schedulers.blocking import BlockingScheduler
from crons.prediction_job import PredictionManager
from crons.training_job import TrainingManager
import datetime

if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='UTC')
    scheduler.add_executor('processpool')
    trainMan = TrainingManager()
    predMan = PredictionManager()

    patientIds = ['3f456e62-7239-42ca-b40e-74b11536a76d', 'e5ce302f-8510-4720-9f35-24eb6c64c089']

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






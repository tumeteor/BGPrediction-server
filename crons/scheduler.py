from apscheduler.schedulers.blocking import BlockingScheduler
from crons.prediction_job import PredictionManager
from crons.training_job import TrainingManager
from utils.dbutil import _DBConnector

trainMan = TrainingManager()

conn = _DBConnector()


def train_job(patientId):
    trainMan.training_job(patientId)


def pred_job(patientId):
    predMan = PredictionManager(patientId)
    predMan.predict_job()


if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='UTC')
    scheduler.add_executor('processpool')

    patientIds = conn.load_all_patient_uuids()
    # patientIds = ["8","15"]

    # add cron job for each patient
    for patientId in patientIds:
        scheduler.add_job(train_job, 'interval', args=[patientId], seconds=6)

        scheduler.add_job(pred_job, 'interval', args=[patientId], seconds=6)

    try:
        print("Start Scheduler.")
        scheduler.start()
    except (SystemExit):
        pass

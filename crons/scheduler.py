from apscheduler.schedulers.blocking import BlockingScheduler
from crons.prediction_job import PredictionManager
from crons.training_job import TrainingManager
from utils.dbutil import _DBConnector

trainMan = TrainingManager()
predMan = PredictionManager()

conn = _DBConnector()

def trainJob(patientId):
    trainMan.trainingJob(patientId)

def predJob(patientId):
    predMan.predictJob(patientId)

if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='UTC')
    scheduler.add_executor('processpool')

    #TODO: load all patientIds from DB
    patientIds = conn.loadAllPatientUUIDs()


    # add cron job for each patient
    for patientId in patientIds:
        scheduler.add_job(trainJob, 'interval', args=[patientId], seconds=2)

        scheduler.add_job(predJob, 'interval', args=[patientId], seconds=2)

    try:
        print("Start Scheduler.")
        scheduler.start()
    except (SystemExit):
        pass






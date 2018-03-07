from apscheduler.schedulers.blocking import BlockingScheduler
from crons.prediction_job import PredictionManager
from crons.training_job import TrainingManager
from utils.dbutil import _DBConnector

trainMan = TrainingManager()


conn = _DBConnector()
def trainJob(patientId):
    trainMan.trainingJob(patientId)

def predJob(patientId):
    predMan = PredictionManager(patientId)
    predMan.predictJob()

if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone='UTC')
    scheduler.add_executor('processpool')

    patientIds = conn.loadAllPatientUUIDs()
    #patientIds = ["8","15"]

    # add cron job for each patient
    for patientId in patientIds:
        scheduler.add_job(trainJob, 'interval', args=[patientId], seconds=6)

        scheduler.add_job(predJob, 'interval', args=[patientId], seconds=6)

    try:
        print("Start Scheduler.")
        scheduler.start()
    except (SystemExit):
        pass






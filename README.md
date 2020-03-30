# Glycorec Blood Glucose Prediction Server Backend

This documentation is for the backend service of Glycorec Blood Glucose Prediction. 

### Prerequisites

Python (>= 2.7 or >= 3.3,  
NumPy (>= 1.8.2),  
SciPy (>= 0.13.3),  
Scikit-learn (>=0.16),  
APScheduler (>=3.3.0),  
mysql-connector-python (>=2.0),  
Pandas (>=0.12.0).

## Getting Started

Add the project folder to the Python path:

```
export PYTHONPATH=$PYTHONPATH:/path/to/the/project
```

## Deployment

The cron jobs are started by "crons/scheduler.py". There the interval triggering time for training and predictiong jobs are configurable. 

```
python crons/scheduler.py
```
## Configurations

### Connecting to MySQL server

The MySQL configurations are in "utils/dbutil.py"


```
   config = {
        'user': xxx,
        'password': xxx,
        'host': '127.0.0.1',
        'database': 'glycorec_server',
        'raise_on_warnings': True
    }
```

### Cron job configurations

The time interval for each cron job is configurable in "crons/scheduler.py". For example:

```
scheduler.add_job(train_job, 'interval', args=[patientId], seconds=6)
```

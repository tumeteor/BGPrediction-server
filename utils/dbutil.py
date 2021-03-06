import mysql.connector
import pandas as pd
import time, datetime
import logging
from contextlib import contextmanager
import uuid


class _DBConnector:
    config = {
        'user': 'xxx',
        'password': 'xxx',
        'host': '127.0.0.1',
        'database': 'glycorec_server',
        'raise_on_warnings': True
    }

    def __init__(self):
        self.con = mysql.connector.connect(**self.config)

    @contextmanager
    def manage_transaction(self, *args, **kw):
        exc = False
        try:
            try:
                self.con.start_transaction(*args, **kw)
                yield self.con.cursor(dictionary=True)
            except mysql.connector.Error as err:
                print(err)
                exc = True
                self.con.rollback()
        finally:
            if not exc:
                self.con.commit()

    def load_all_patient_uuids(self):
        with self.manage_transaction() as cur:
            query = "SELECT uuid FROM storage_user"
            cur.execute(query)
            rows = cur.fetchall()
            if not rows:
                self.log.error("No Glucose data was returned!")
                return
            patients = list()
            for row in rows:
                patients.append(row)
            return patients


class DBConnector:
    config = {
        'user': 'root',
        'password': 'pu9eek9I',
        'host': '127.0.0.1',
        'database': 'glycorec_server',
        'raise_on_warnings': True
    }

    def __init__(self, patientId):
        # configure log
        logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.INFO)
        self.log = logging.getLogger("DBConnector")
        self.connect_db()
        self.patient_id = patientId
        self.glucoseData = list()
        self.insulinData = list()
        self.carbData = list()
        self.activityData = list()
        self.con = None

    @contextmanager
    def manage_transaction(self, *args, **kw):
        exc = False
        try:
            try:
                self.con.start_transaction(*args, **kw)
                yield self.con.cursor(dictionary=True)
            except mysql.connector.Error as err:
                print(err)
                exc = True
                self.con.rollback()
        finally:
            if not exc:
                self.con.commit()

    def connect_db(self):
        self.con = mysql.connector.connect(**self.config)
        self.con.set_converter_class(NumpyMySQLConverter)

    def close_db(self):
        self.con.close()

    def load_all_data(self):
        if self.patient_id is None:
            self.log.error.info("No patient ID provided")
            return
        self.connect_db()
        ###### LOAD DATA ######
        self.load_glucose_data()
        self.load_insulin_data()
        self.load_carb_data()
        self.load_activity_data()
        return self.glucoseData, self.insulinData, self.carbData, self.activityData

    def load_glucose_data(self):
        """
        Retrieve glucose (ground truth) data from databasev
        """
        self.log.info("Loading Glucose data for patient {}".format(self.patient_id))
        with self.manage_transaction() as cur:
            query = "SELECT pos, time, value FROM (SELECT @rownum := @rownum + 1 as pos, bs_date_created as 'time', `bs_value_mgdl` as 'value'," \
                    "user_entity_uuid FROM storage_blood_sugar_data " \
                    "cross join (select @rownum := 0) r order by 'time') a WHERE a.user_entity_uuid = '{patientId}'".format(
                patientId=self.patient_id)
            self.log.debug("load_glucose_data() query: '" + query + "'")

            cur.execute(query)
            rows = cur.fetchall()
            if not rows:
                self.log.error("No Glucose data was returned!")
                return
            for row in rows:
                self.glucoseData.append(row)

        self.log.info("{} glucose measurements returned".format(len(self.glucoseData)))

    def load_insulin_data(self, ignore_basal=False):
        """
        Retrieve insulin data
        """
        self.log.info("Loading insulin data for patient {}".format(self.patient_id))
        if ignore_basal:
            with self.manage_transaction() as cur:
                query = "SELECT DISTINCT date_time as 'time', CONVERT(insulin_units, UNSIGNED INTEGER) as 'value', type FROM storage_insulin_data " \
                        "WHERE user_entity_uuid = {patient_id} and type=1 order by 'time'".format(
                    patient_id=self.patient_id)
                self.log.info("load_insulin_data() query: '" + query + "'")
                cur.execute(query)
                rows = cur.fetchall()
                if not rows:
                    self.log.error("No insulin data was returned!")
                    return
                for row in rows:
                    self.insulinData.append(row)
        else:
            with self.manage_transaction() as cur:
                query = "SELECT DISTINCT date_time as 'time', CONVERT(insulin_units, UNSIGNED INTEGER) as 'value', type FROM storage_insulin_data " \
                        "WHERE user_entity_uuid = {patient_id} and type is not NULL order by 'time'".format(
                    patient_id=self.patient_id)
                self.log.info("load_insulin_data() query: '" + query + "'")
                cur.execute(query)
                rows = cur.fetchall()
                self.log.info("row size: {}".format(len(rows)))
                if not rows:
                    self.log.error("No insulin data was returned!")
                    return
                for row in rows:
                    self.insulinData.append(row)
        self.log.info("{} insulin measurements returned".format(len(self.insulinData)))

    def load_carb_data(self):
        """
        Retrieve carbohydrate data
        """
        self.log.info("Loading carbohydrate data for patient {}".format(self.patient_id))
        with self.manage_transaction() as cur:
            query = "SELECT DISTINCT  date_time as 'time', CONVERT(kcal, UNSIGNED INTEGER) as 'value' FROM storage_meal_data " \
                    "WHERE user_entity_uuid = {patientId} order by 'time'".format(patientId=self.patient_id)
            self.log.info("loadCarbohydrateData() query: '" + query + "'")
            cur.execute(query)
            rows = cur.fetchall()
            if not rows:
                self.log.error("No carb data was returned!")
                return
            for row in rows:
                self.carbData.append(row)
                print(len(self.carbData))
        self.log.info("{} carb measurements returned".format(len(self.carbData)))

    def load_activity_data(self):
        """
        Retrieve activity data
        """
        # FIXED: import steps and use them in place of Akcal
        self.log.info("Loading activity data for patient {}".format(self.patient_id))
        with self.manage_transaction() as cur:
            cur = self.con.cursor()
            query = "SELECT DISTINCT  date_time as 'time', CONVERT(kcal, UNSIGNED INTEGER) as 'value' FROM storage_planned_activity " \
                    "WHERE user_entity_uuid = {patientId} order by 'time'".format(patientId=self.patient_id)
            self.log.debug("load_activity_data() query: '" + query + "'")
            cur.execute(query)
            self.log.debug("{} rows returned".format(cur.rowcount()))
            rows = cur.fetchall()
            if not rows:
                self.log.error("No activity data was returned!")
                return
            for row in rows:
                self.activityData.append(row)

    ''''' load the raw timestamp for blood glucose data '''

    def load_timestamps(self, patientId):
        with self.manage_transaction() as cur:
            query = "SELECT * FROM (SELECT @rownum := @rownum + 1 as pos, bs_date_created as 'date' FROM storage_blood_sugar_data " \
                    "cross join (select @rownum := 0) r order by 'time') WHERE a.user_entity_uuid = {patientId}".format(
                patientId=patientId)
            df = pd.read_sql(query, self.con)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        # IMPORTANT: sort by date
        df = df.sort_index()

        return df

    def store_prediction(self, patient_id, score, ptype):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        with self.manage_transaction() as cur:
            # sql = "INSERT into storage_recommendation_data (date_time, score, type, user_entity_uuid ) VALUES  \
            #     (%(date_time)s, %(score)s, %(ptype)s, %(user_entity_uuid)s)."

            sql = "INSERT INTO storage_blood_sugar_prediction (uuid, date_time, value_mgdl, user_entity_uuid) VALUES" \
                  "(%(uuid)s, %(date_time)s, %(value_mgdl)s, %(user_entity_uuid)s)"
            self.log.info("insert prediction for user {}:".format(patient_id))
            print(sql)
            cur.execute(sql, {
                "uuid": str(uuid.uuid1()),
                "date_time": timestamp,
                "value_mgdl": score[0],
                "user_entity_uuid": patient_id
            })
            self.con.commit()


class NumpyMySQLConverter(mysql.connector.conversion.MySQLConverter):
    """ A mysql.connector Converter that handles Numpy types """

    @staticmethod
    def _float32_to_mysql(value):
        return float(value)

    @staticmethod
    def _float64_to_mysql(value):
        return float(value)

    @staticmethod
    def _int32_to_mysql(value):
        return int(value)

    @staticmethod
    def _int64_to_mysql(value):
        return int(value)

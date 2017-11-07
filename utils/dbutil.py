import mysql.connector
import pandas as pd


class DBConnector:

    config = {
        'user': 'scott',
        'password': 'tiger',
        'host': '127.0.0.1',
        'database': 'employees',
        'raise_on_warnings': True,
        'use_pure': False,
    }

    def __init__(self, patientId):
        self.patientId = patientId
        self.glucoseData = list()
        self.insulinData = list()
        self.carbData = list()
        self.activityData = list()

    def connectDB(self):
        self.cnx = mysql.connector.connect(**self.config)

    def closeDB(self):
        self.cnx.close()

    def loadAllData(self):
        ###### LOAD DATA ######
        self.loadGlucoseData()
        self.loadInsulinData()
        self.loadCarbData()
        self.loadActivityData()
        return self.glucoseData, self.insulinData, self.carbData, self.activityData



    def loadGlucoseData(self):
        """
        Retrieve glucose (ground truth) data from database
        """
        self.log.info("Loading Glucose data for patient {}".format(self.patientId))
        with self.con:
            cur = self.con.cursor()
            query = "SELECT date as 'time', `gt-value` as 'value', pos as 'index' FROM BG_Instance " \
                    "WHERE patientID = {patientId} and date > '2017-02-25'".format(patientId=self.patientId)
            self.log.debug("loadGlucoseData() query: '" + query + "'")
            cur.execute(query)
            self.log.debug("{} rows returned".format(cur.rowcount))
            rows = cur.fetchall()
            if not rows:
                self.log.error("No Glucose data was returned!")
                return
            for row in rows:
                self.glucoseData.append(row)

        self.log.debug("{} glucose measurements returned".format(len(self.glucoseData)))

    def loadInsulinData(self, ignoreBasal=False):
        """
        Retrieve insulin data
        """
        self.log.info("Loading insulin data for patient {}".format(self.patientId))
        if ignoreBasal:
            with self.con:
                cur = self.con.cursor()
                query = "SELECT date as 'time', value, type FROM BG_Insulin " \
                        "WHERE patientID = {patientId} and date > '2017-02-25' and type='rapid'".format(
                    patientId=self.patientId)
                self.log.debug("loadInsulinData() query: '" + query + "'")
                cur.execute(query)
                logging.debug("{} rows returned".format(cur.rowcount))
                rows = cur.fetchall()
                if not rows:
                    self.log.error("No insulin data was returned!")
                    return
                for row in rows:
                    self.insulinData.append(row)
        else:
            with self.con:
                cur = self.con.cursor()
                query = "SELECT date as 'time', value, type FROM BG_Insulin " \
                        "WHERE patientID = {patientId} and date > '2017-02-25'".format(patientId=self.patientId)
                self.log.debug("loadInsulinData() query: '" + query + "'")
                cur.execute(query)
                logging.debug("{} rows returned".format(cur.rowcount))
                rows = cur.fetchall()
                if not rows:
                    self.log.error("No insulin data was returned!")
                    return
                for row in rows:
                    self.insulinData.append(row)

    def loadCarbData(self):
        """
        Retrieve carbohydrate data
        """
        self.log.info("Loading carbohydrate data for patient {}".format(self.patientId))
        with self.con:
            cur = self.con.cursor()
            query = "SELECT date as 'time', value FROM BG_carbohydrate " \
                    "WHERE patientID = {patientId} and date > '2017-02-25'".format(patientId=self.patientId)
            self.log.debug("loadCarbohydrateData() query: '" + query + "'")
            cur.execute(query)
            self.log.debug("{} rows returned".format(cur.rowcount))
            rows = cur.fetchall()
            if not rows:
                self.log.error("No carb data was returned!")
                return
            for row in rows:
                self.carbData.append(row)

    def loadActivityData(self):
        """
        Retrieve activity data
        """
        # FIXED: import steps and use them in place of Akcal
        self.log.info("Loading activity data for patient {}".format(self.patientId))
        with self.con:
            cur = self.con.cursor()
            query = "SELECT date as 'time', value FROM BG_steps " \
                    "WHERE patientID = {patientId} and date > '2017-02-25'".format(patientId=self.patientId)
            self.log.debug("loadActivityData() query: '" + query + "'")
            cur.execute(query)
            self.log.debug("{} rows returned".format(cur.rowcount))
            rows = cur.fetchall()
            if not rows:
                self.log.error("No activity data was returned!")
                return
            for row in rows:
                self.activityData.append(row)

    ''''' load the raw timestamp for blood glucose data '''

    def loadTimestamps(self, con, patientId):
        with con:
            cur = con.cursor()
            query = "SELECT date, pos FROM BG_Instance " \
                    "WHERE patientID = {patientId} ".format(patientId=patientId)
            df = pd.read_sql(query, con)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        # IMPORTANT: sort by date
        df = df.sort_index()

        return df






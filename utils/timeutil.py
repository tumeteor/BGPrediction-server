import time
import datetime
_night = "night"
_morning = "morning"
_afternoon = "afternoon"
_evening = "evening"

def tohour(duration):
    """
    convert timedelta to hours
    :param duration:
    :return:
    """
    days, seconds = duration.days, duration.seconds
    hours = days * 24 + seconds // 3600
    return hours

def strToDateTime(t):
    return time.strptime(t,"'%d/%m/%y %H:%M:%S")

def getTimeBin(timestamp):
    """
    Return the time bin for the given datetime input
    :param timestamp: datetime object
    :return: Time bin ('night', 'morning', 'afternoon', 'evening'
    """
    assert timestamp
    start_night = datetime.time(0, 0, 0)
    end_night = datetime.time(5, 59, 59)
    start_morning = datetime.time(6, 0, 0)
    end_morning = datetime.time(11, 59, 59)
    start_afternoon = datetime.time(12, 0, 0)
    end_afternoon = datetime.time(17, 59, 59)
    start_evening = datetime.time(18, 0, 0)
    end_evening = datetime.time(23, 59, 59)
    if checkTimeInterval(timestamp, start_night, end_night):
        return _night
    if checkTimeInterval(timestamp, start_morning, end_morning):
        return _morning
    if checkTimeInterval(timestamp, start_afternoon, end_afternoon):
        return _afternoon
    if checkTimeInterval(timestamp, start_evening, end_evening):
        return _evening
    raise ArithmeticError

def checkTimeInterval(datetimeInput, start, end):
    """
    Check whether given datetime input falls into the interval defined by datetime.time values start and end
    :return: boolean
    """
    assert(datetimeInput)
    # TODO: avoid this! use timestamps in the database instead or transform the timestamps to UTC in import!!
    datetimeInput = datetimeInput + datetime.timedelta(minutes=60)
    assert(start < end)
    timeInput = datetime.time(
        datetimeInput.hour,
        datetimeInput.minute,
        datetimeInput.second)
    return start <= timeInput <= end


"""
Calendar utilities

Doublecheck conversions:

    >>> brt = gettz('Brazil/East')

    >>> dt = DateTime('2005/07/07 18:00:00 Brazil/East')
    >>> dt == dt2DT(DT2dt(dt))
    True

    >>> dt = datetime.datetime(2005, 07, 07, 18, 00, 00, tzinfo=tz)
    >>> dt == DT2dt(dt2DT(dt))
    True

"""

import datetime
from DateTime import DateTime
try:
    import dateutil
except ImportError:
    # To make Calendaring patch in dateutils:
    import Products.Calendaring
    import dateutil

def gettz(name=None):
    try:
        return _extra_times[name]
    except KeyError:
        return dateutil.tz.gettz(name)

def dt2DT(dt, tzname=None):
    """Convert a python datetime to DateTime. 

    >>> import time, os
    >>> oldtz = os.environ['TZ']
    >>> os.environ['TZ'] = 'Brazil/East'
    >>> time.tzset()
    >>> brt = gettz('Brazil/East')

    No timezone information, assume local timezone at the time.

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0))
    DateTime('2005/11/07 18:00:00 GMT-2')

    Provide a default TZID:

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0), tzname='EET')
    DateTime('2005/11/07 18:00:00 GMT+2')

    UTC timezone.

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0, tzinfo=gettz('UTC')))
    DateTime('2005/11/07 18:00:00 GMT+0')

    BRST timezone (GMT-2 on this day).

    >>> dt2DT(datetime.datetime(2005, 11, 07, 18, 0, 0, tzinfo=brt))
    DateTime('2005/11/07 18:00:00 GMT-2')

    BRT timezone (GMT-3 on this day).

    >>> dt2DT(datetime.datetime(2005, 07, 07, 18, 0, 0, tzinfo=brt))
    DateTime('2005/07/07 18:00:00 GMT-3')
    
    Change back:
    >>> os.environ['TZ'] = oldtz
    >>> time.tzset()    

    """
    if tzname is None and dt.tzinfo is None:
        # Assume local time
        tz = gettz()
    elif tzname is not None:
        # Convert to timezone
        tz = gettz(tzname)
    else:
        tz = None
    if tz is not None:
        dt = dt.replace(tzinfo=tz)
    return DateTime(dt.isoformat())

def DT2dt(dt):
    """Convert a DateTime to python's datetime in UTC.

    >>> dt = DT2dt(DateTime('2005/11/07 18:00:00 UTC'))
    >>> dt
    datetime.datetime(2005, 11, 7, 18, 0, tzinfo=tzfile('/usr/share/zoneinfo/Universal'))
    >>> dt.astimezone(gettz('UTC'))
    datetime.datetime(2005, 11, 7, 18, 0, tzinfo=tzfile('/usr/share/zoneinfo/UTC'))

    >>> dt = DT2dt(DateTime('2005/11/07 18:00:00 Brazil/East'))
    >>> dt
    datetime.datetime(2005, 11, 7, 18, 0, tzinfo=tzfile('/usr/share/zoneinfo/Brazil/East'))
    >>> dt.astimezone(gettz('UTC'))
    datetime.datetime(2005, 11, 7, 20, 0, tzinfo=tzfile('/usr/share/zoneinfo/UTC'))

    >>> dt = DT2dt(DateTime('2005/11/07 18:00:00 GMT-2'))
    >>> dt
    datetime.datetime(2005, 11, 7, 18, 0, tzinfo=tzoffset('GMT-2', -7200))
    >>> dt.astimezone(gettz('UTC'))
    datetime.datetime(2005, 11, 7, 20, 0, tzinfo=tzfile('/usr/share/zoneinfo/UTC'))

    >>> dt = DT2dt(DateTime('2005/07/07 18:00:00 Brazil/East'))
    >>> dt
    datetime.datetime(2005, 7, 7, 18, 0, tzinfo=tzfile('/usr/share/zoneinfo/Brazil/East'))
    >>> dt.astimezone(gettz('UTC'))
    datetime.datetime(2005, 7, 7, 21, 0, tzinfo=tzfile('/usr/share/zoneinfo/UTC'))

    >>> dt = DT2dt(DateTime('2005/07/07 18:00:00 GMT-3'))
    >>> dt
    datetime.datetime(2005, 7, 7, 18, 0, tzinfo=tzoffset('GMT-3', -10800))
    >>> dt.astimezone(gettz('UTC'))
    datetime.datetime(2005, 7, 7, 21, 0, tzinfo=tzfile('/usr/share/zoneinfo/UTC'))
    """
    tz = gettz(dt.timezone())
    value = datetime.datetime(dt.year(), dt.month(), dt.day(),
                              dt.hour(), dt.minute(), int(dt.second()),
                              int(dt.second()*1000000) % 1000000, tzinfo=tz)
    return value

_extra_times = {}
for x in range(-12, 0) + range(1, 13):
    for n in ('GMT', 'UTC'):
        name = '%s%+i' % (n, x)
        tz = dateutil.tz.tzoffset(name, x*3600)
        _extra_times[name] = tz

from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone


class CommonDate(object):
    DEFAULT_ZONE = timezone(offset=timedelta(hours=8))

    @staticmethod
    def today(tz=DEFAULT_ZONE):
        return date.today()

    @staticmethod
    def today_time(tz=DEFAULT_ZONE):
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def yday(tz=DEFAULT_ZONE):
        return date.today() - timedelta(days=1)

    @staticmethod
    def yday_time(tz=DEFAULT_ZONE):
        yday_tmp = datetime.now() - timedelta(days=1)
        return yday_tmp.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def today_ymd(tz=DEFAULT_ZONE):
        return CommonDate.today().strftime('%Y%m%d')

    @staticmethod
    def today_iso(tz=DEFAULT_ZONE):
        return CommonDate.today().strftime('%Y-%m-%d')

    @staticmethod
    def yday_ymd(tz=DEFAULT_ZONE):
        return CommonDate.yday().strftime('%Y%m%d')

    @staticmethod
    def yday_iso(tz=DEFAULT_ZONE):
        return CommonDate.yday().strftime('%Y-%m-%d')

    @staticmethod
    def today_ts(tz=DEFAULT_ZONE):
        """Today's 0:0:0 timestamp
        :return integer
        """
        return int(CommonDate.today().strftime('%s'))

    @staticmethod
    def yday_ts(tz=DEFAULT_ZONE):
        """Yesterday's 0:0:0 timestamp
        :return integer
        """
        return int(CommonDate.yday().strftime('%s'))

    @staticmethod
    def now_ts(tz=DEFAULT_ZONE):
        """Now's timestamp
        :return integer
        """
        return int(datetime.timestamp(datetime.now()))

    @staticmethod
    def now(tz=DEFAULT_ZONE):
        return datetime.now()

    @staticmethod
    def now_iso(tz=DEFAULT_ZONE):
        return CommonDate.now().strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def mts_2_iso(mts, tz=DEFAULT_ZONE):
        return datetime.fromtimestamp(mts/1000).strftime('%Y-%m-%d %H:%M:%S')

    @staticmethod
    def ts_2_iso(ts, tz=DEFAULT_ZONE):
        return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

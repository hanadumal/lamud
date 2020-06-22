from lamuda.date.common_date import CommonDate


class TestCommonDate(object):
    def test_yday_time(self):
        print(CommonDate.yday_time())

    def test_yday_iso(self):
        print(CommonDate.yday_iso())

    def test_yday_ymd(self):
        print(CommonDate.yday_ymd())

    def test_yday_ts(self):
        print(CommonDate.yday_ts())

    def test_today_time(self):
        print(CommonDate.today_time())

    def test_today_iso(self):
        print(CommonDate.today_iso())

    def test_today_ymd(self):
        print(CommonDate.today_ymd())

    def test_today_ts(self):
        print(CommonDate.today_ts())

    def test_now_ts(self):
        print(CommonDate.now_ts())

    def test_now_iso(self):
        print(CommonDate.now_iso())

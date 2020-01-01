from lamuda.misc.utils import ObjDict


class TestObjDict(object):
    """ObjDict Test class"""
    def test_get(self):
        a_dict = ObjDict()
        a_dict.name = 'hanadumal'
        assert a_dict.name=='hanadumal'
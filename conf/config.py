import os


class Const(object):
    class ConstError(PermissionError):
        pass

    GOV_YAML = "conf/govUrl.yaml"
    BASE_FILE_PATH = os.path.abspath(".") + "/file"
    DOWNLOAD_PATH = os.path.abspath(".") + "/download"

    def __setattr__(self, name, value):
        if name in self.__dict__.keys():
            raise self.ConstError("Can't rebind const(%s)" % name)
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError("Can't unbind const(%s)" % name)
        raise NameError(name)

class Attachment(object):
    def __init__(self, url, origin_file_name, file_name, file_type_name, file_path, local_path):
        self.url = url
        self.origin_file_name = origin_file_name
        self.file_name = file_name
        # 同源文件
        self.file_type_name = file_type_name
        self.file_path = file_path
        self.local_path = local_path

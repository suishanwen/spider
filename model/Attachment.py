class Attachment(object):
    def __init__(self, url, file_name, relate_file_name, file_type_name, file_path, local_href):
        self.url = url
        self.file_name = file_name
        # 同源文件
        self.relate_file_name = relate_file_name
        self.file_type_name = file_type_name
        self.file_path = file_path
        self.local_href = local_href

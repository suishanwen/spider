import yaml


# 读取 yaml 文件
def yaml_read(path, props):
    with open(path, "r") as yaml_file:
        yaml_obj = yaml.load(yaml_file.read())
        for key in props:
            yaml_obj = yaml_obj[key]
        return yaml_obj

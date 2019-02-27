import yaml


# 读取 yaml 文件
def yaml_read(path, props):
    with open(path, "r", encoding='UTF-8') as yaml_file:
        yaml_obj = yaml.load(yaml_file.read())
        for key in props:
            yaml_obj = yaml_obj[key]
        return yaml_obj


def yaml_write_pages(path, section, data):
    yaml_obj = yaml_read(path, ())
    with open(path, "w", encoding='UTF-8') as yaml_file:
        yaml_obj["gov"][section]["pages"] = data
        yaml.dump(yaml_obj, yaml_file, allow_unicode=True)

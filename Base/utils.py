from typing import Union

from SmartDjango import E


def error_add_class_prefix(name, cls):
    cls_name = cls.__name__.upper()  # type: str
    if cls_name.endswith('ERROR'):
        cls_name = cls_name[:-5]
    return '%s-%s' % (cls_name, name)


@E.register(id_processor=error_add_class_prefix)
class UtilsError:
    CHOICE_PROCESSOR = E("参数不合法")

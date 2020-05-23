# -*- coding: utf-8 -*-


class ObjDict(dict):
    """
    dictからobjectに変更することが出来ます
    例えば、下記コードを実装できることになる：
        example = {'key1': 'value1', 'key2': 2}
        print(example['key1'])

        obj_example = ObjDict(**example)
        print(obj_example.key1)
        print(obj_example['key1'])
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

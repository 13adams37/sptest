from tinydb import TinyDB, Query
import json

db = TinyDB('db.json')
Object = Query()
keys = ['dogovor', 'act', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'uv', 'folder',
        'rgg', 'rggpp', 'level', 'ss', 'kp', 'table']


class DataBase:
    # def __int__(self):

    def add(self, what):
        db.insert(self.makejson(what))

    def get(self, what):
        pass

    def makejson(self, elements):
        tempdict = {}
        tempdict1 = {}
        tempdict2 = {}
        listdict1 = {}
        listdict2 = {}
        for key, element in zip(keys, elements):
            tempdict[key] = element
            if key == "table" and element:
                v = 0
                for element1 in element:
                    for key1, element2 in zip(keys, element1):
                        tempdict1[key1] = element2
                        if key1 == "table" and element2:
                            z = 0
                            for element3 in element2:
                                for key2, element4 in zip(keys, element3):
                                    tempdict2[key2] = element4
                                listdict2.update({z: tempdict2.copy()})
                                z = z + 1
                                tempdict2.clear()
                            tempdict1[key1] = listdict2
                    listdict1.update({v: tempdict1.copy()})
                    v = v + 1
                    tempdict1.clear()
                tempdict[key] = listdict1.copy()
        return tempdict


if __name__ == '__main__':
    test = DataBase()

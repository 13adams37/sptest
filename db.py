import time

import jsondblite

try:
    db = jsondblite.Database("testbig.db", create=True)  # Explicitly create new db.
    with db:
        db.create_index("objects", "$..object")
        db.create_index("names", "$..name")
        db.create_index("models", "$..model")
        db.create_index("parts", "$..part")
        db.create_index("vendors", "$..vendor")
        db.create_index("serials", "$..serial1")
except OSError:
    db = jsondblite.Database("testbig.db", create=False)

keys = ['object', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'amount', 'uv',
        'rgg', 'rggpp', 'level', 'table']


class DataBase:
    # def __int__(self):

    def add(self, what):
        with db:
            db.add(self.makejson(what))

    def search(self, jquery, name):
        with db:
            return db.search(jquery, name)
            # print(db.search(jquery, name))

    def search_if_exists(self, jquery, name):
        if db.search(jquery, name):
            return True
        else:
            return False

    def get_index_names(self, index):
        items = []
        with db:
            for item in db.get_index_values(index):
                # if item[1] not in items:
                #     items.append(item[1])
                items.append(item)
        # items.sort()
        return items

    def get_unique_index_names(self, index):
        items = []
        with db:
            for item in db.get_index_values(index):
                # if item[1] not in items:
                #     items.append(item[1])
                if item[1] not in items:
                    items.append(item[1])
        # items.sort()
        return items

    def getall(self):
        # return db.all()
        pass

    def get_by_id(self, itemid):
        with db:
            # db.get(id)
            return db.get(itemid)

    def get_display_values(self, itemid):  # need transaction
        # with db:
        #     response = db.get(itemid)
        response = db.get(itemid)
        return f"{response['object']} {response['name']} {response['model']} {response['part']} {response['vendor']} {response['serial1']}"

    def update_element(self, docid, doc):
        with db:
            db.update(docid, self.makejson(doc))

    # def start_transaction(self):
    #     db.

    def makejson(self, elements):  # making dict
        tempdict, tempdict1, tempdict2 = {}, {}, {}
        listdict1, listdict2 = [], []
        for key, element in zip(keys, elements):
            tempdict[key] = element
            if key == "table" and element:
                for element1 in element:
                    for key1, element2 in zip(keys, element1):
                        tempdict1[key1] = element2
                        if key1 == "table" and element2:
                            for element3 in element2:
                                for key2, element4 in zip(keys, element3):
                                    tempdict2[key2] = element4
                                listdict2.append(tempdict2.copy())
                                tempdict2.clear()
                            tempdict1[key1] = listdict2.copy()
                            listdict2.clear()
                    listdict1.append(tempdict1.copy())
                    tempdict1.clear()
                tempdict[key] = listdict1.copy()
        return tempdict


if __name__ == '__main__':
    dbclass = DataBase()

    # Максимальное заполнение за 10 секунд
    # mydict = ['multi', 'Системный блок', 'KCAS-13', '148001', 'POWERCOOL', '1337555', '', False, '', '', '', 'Комплект', [['multi', 'материнка', 'b450m-re', 'AKB450M000137', 'ASUS', '', '1', False, '', '', '', 'Составная часть', [['multi', 'проц', 'i7-4700k', '00148', 'Intel', '', '', True, '', '', '', 'Элемент', []]]], ['multi', 'SSD', 'ARC-100', '', 'OCZ', '', '', False, '', '', '', 'Составная часть', []], ['multi', 'БП', 'R450M', '', 'AEROCOOL', '', '', False, '', '', '', 'Составная часть', [['multi', 'плата', '', '', '', '', '', False, '', '', '', 'Элемент', []]]], ['multi', 'вентилятор корпуса', 'SA-143', '', 'DEEPCOOL', '', '1', False, '', '', '', 'Элемент', []]]]
    # timeout = 10  # [seconds]
    # timeout_start = time.time()
    # # with db:
    # #     while time.time() < timeout_start + timeout:
    # #         db.add(mydict)
    # while time.time() < timeout_start + timeout:
    #     dbclass.add(mydict)

    # with db:
    #     db.add(mydict)
    # print(db.search("$..name", 'element1'))
    # result = db.search("$..name", 'sost3')
    # print(len(result))
    # print(result)

    # Создание индекса
    # with db:
    #     db.create_index("names", "$..name")

    # Вывод всех уникальных значений из индекса
    # items = []
    # for item in db.get_index_values("names"):
    #     # if item[1] not in items:
    #     #     items.append(item)
    #     items.append(item)
    #
    # # items.sort()
    # print(items)
    # for item in items:
    #     print(item[1])

    # Очистка бд
    # with db:
    #     for item in iter(db):
    #         del db[item]

    # поиск
    # with db:
    #     resp = db.search("$..name", "testname")
    # print(resp)
    # print("body", resp[0][1])
    # print("id", resp[0][0])

    # print(dbclass.get_by_id("2be3291a137744d8a53135c64bb112f0"))
    # print(dbclass.get_unique_index_names('names'))


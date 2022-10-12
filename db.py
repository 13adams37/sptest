import jsondblite

try:
    db = jsondblite.Database("test.db", create=True)  # Explicitly create new db.
    print("new")
except OSError:
    db = jsondblite.Database("test.db", create=False)  # Explicitly create new db.
    print("old")

keys = ['object', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'uv', 'folder',
        'rgg', 'rggpp', 'level', 'table']


class DataBase:
    # def __int__(self):

    def add(self, what):
        with db:
            db.add(self.makejson(what))

    # def get(self, what):
    #     with open("db.json", 'r') as json_file:
    #         json_data = json.load(json_file)
    #     jsonpath_expression = parse(what)
    #
    #     items = []
    #
    #     for match in jsonpath_expression.find(json_data):
    #         if match.value not in items:
    #             items.append(match)
    #     return items

    def search(self, jquery, name):
        with db:
            db.search(jquery, name)

    def get_index_names(self, index):
        items = []
        with db:
            for item in db.get_index_values(index):
                # if item[1] not in items:
                #     items.append(item[1])
                items.append(item)
        # items.sort()
        return items

    def getall(self):
        # return db.all()
        pass

    def get_by_id(self, itemid):
        with db:
            # db.get(id)
            return db.get(itemid)

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
    # timeout = 10  # [seconds]
    # timeout_start = time.time()
    # with db:
    #     while time.time() < timeout_start + timeout:
    #         db.add(mydict)

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
    items = []
    for item in db.get_index_values("names"):
        # if item[1] not in items:
        #     items.append(item)
        items.append(item)

    # items.sort()
    print(items)
    for item in items:
        print(item[1])

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


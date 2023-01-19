import jsondblite


try:
    db = jsondblite.Database("saturn_test444.db", create=True)
    with db:
        db.create_index("objects", "$.object")
        db.create_index("names", "$..name")
        db.create_index("models", "$..model")
        db.create_index("parts", "$..part")
        db.create_index("vendors", "$..vendor")
        db.create_index("serials", "$..serial1")
        db.add({"search": True, "hints": True, "jump": True, "max_len": "0"}, "1337")
except OSError:
    db = jsondblite.Database("saturn_test444.db", create=False)

keys = ['object', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'amount', 'uv',
        'rgg', 'rggpp', 'level', 'table']


class DataBase:

    def add(self, what):
        with db:
            db.add(self.all_trim_json(self.makejson(what)))

    def add_dict(self, what, doc_id=None):
        with db:
            db.add(self.all_trim_json(what), doc_id)

    def search(self, jquery, name):
        with db:
            return db.search(jquery, name)

    def search_if_exists(self, jquery, name):
        if db.search(jquery, name):
            return True
        else:
            return False

    def search_by_id_if_exists(self, docid):
        if db.get(docid) is not None:
            return True
        else:
            return False

    def get_index_names_fromthisdb(self, index):
        items = []
        with db:
            for item in db.get_index_values(index):
                if item[0] != '444' and item[1]:
                    items.append(item)
        return items

    def get_index_names(self, index):
        items = []
        with db:
            for item in db.get_index_values(index):
                # if item[0] != '444' and item[1]:
                items.append(item)
        return items

    def get_unique_index_idnames(self, index):
        items = []
        ids = []
        for item in db.get_index_values(index):
            # if item[0] != '444' and item[1]:
            items.append(item[1])
            ids.append(item[0])
        return items, ids

    def get_unique_index_names(self, index):
        items = []
        for item in db.get_index_values(index):
            # if item[0] != '444' and item[1]:
            items.append(item[1])
        return list(set(items))

    def get_by_id(self, itemid):
        return db.get(itemid)

    def update_element(self, docid, doc):
        with db:
            db.update(docid, self.makejson(doc))

    def update_element_dict(self, docid, doc):
        with db:
            db.update(docid, doc)

    def delete_by_id(self, docid):
        with db:
            db.delete(docid)

    def base_trim_string(self, what):
        what['name'] = " ".join(what['name'].split())
        what['model'] = " ".join(what['model'].split())
        what['part'] = " ".join(what['part'].split())
        what['vendor'] = " ".join(what['vendor'].split())
        what['serial1'] = " ".join(what['serial1'].split())
        what['serial2'] = " ".join(what['serial2'].split())
        what['amount'] = " ".join(what['amount'].split())
        what['rgg'] = " ".join(what['rgg'].split())
        what['rggpp'] = " ".join(what['rggpp'].split())

    def all_trim_json(self, what):
        if type(what) == list:
            for item in what:
                self.base_trim_string(item)
                if item['table']:
                    for item1 in item['table']:
                        self.base_trim_string(item1)
                        if item1['table']:
                            for item2 in item1['table']:
                                self.base_trim_string(item2)
        else:
            self.base_trim_string(what)
            if what['table']:
                for item in what['table']:
                    self.base_trim_string(item)
                    if item['table']:
                        for item1 in item['table']:
                            self.base_trim_string(item1)
        return what

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


if __name__ == "__main__":
    dbclass = DataBase()

    # pandas
    # def get_dict_excelsheet_by_year(year):
    #     df = pd.read_excel('База.xlsx', sheet_name=year)
    #     dict_list = []
    #
    #     for row in df.iterrows():
    #         main = row[1]
    #         if str(main['amount']) == 'nan':  # break line detection
    #             continue
    #
    #         for item in main.to_dict():
    #             if str(main[item]) == 'nan':
    #                 main[item] = ""
    #             else:
    #                 main[item] = str(main[item])
    #
    #         dict_main = main.to_dict()
    #         dict_main['object'] = dict_main['object'][:-2]
    #         dict_main['amount'] = dict_main['amount'][:-2]
    #         if len(dict_main['serial1']) == 1:
    #             dict_main['serial1'] = ""
    #         if dict_main['serial2'] == '–':
    #             dict_main['serial2'] = ""
    #         dict_main['uv'] = False
    #         dict_main['rgg'] = ""
    #         dict_main['rggpp'] = ""
    #         dict_main['level'] = "Комплект"
    #         dict_main['table'] = []
    #         dict_list.append(dict_main)
    #     return dict_list
    #
    # hints_dict = {
    #     '2015': get_dict_excelsheet_by_year('2015'),
    #     '2016': get_dict_excelsheet_by_year('2016'),
    #     '2017': get_dict_excelsheet_by_year('2017'),
    #     '2018': get_dict_excelsheet_by_year('2018'),
    #     '2019': get_dict_excelsheet_by_year('2019'),
    #     '2020': get_dict_excelsheet_by_year('2020'),
    #     '2021': get_dict_excelsheet_by_year('2021'),
    #     '2022': get_dict_excelsheet_by_year('2022')
    # }
    # with db:
    #     db.add(hints_dict, '444')


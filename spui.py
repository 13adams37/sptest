# from dearpygui import *
# may be later :(
import json

import PySimpleGUI as sg
import db
from copy import deepcopy

NULLLIST = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
table1, table2 = [], []
fontbig = ("Arial", 24)
fontbutton = ("Helvetica", 20)
fontmid = ("Arial Baltic", 18)
fontmidlow = ("Arial Baltic", 16)

baza = db.DataBase()
tdb = db.db


class Pages:
    def __init__(self):
        self.window = None
        self.addtswindow = None
        self.addwindow = None
        self.credentialswindow = None
        self.viewwindow = None
        self.addkomerswindow = None
        self.edittswidow = None

        self.object = None
        self.tsdata = []
        self.tsavailable = ["Комплект", "Составная часть", "Элемент"]

    def mainpage(self):
        mainpage = [
            [sg.Button('Добавление ТС', key="-Add-", enable_events=True,
                       expand_x=True,
                       expand_y=True,
                       pad=(30, 30),
                       s=(30, 5),
                       button_color=(sg.theme_text_color(), sg.theme_background_color()),
                       border_width=0,
                       font=fontbig,
                       )],
            [sg.Button('Редактирование/просмотр ТС', key="-Edit-", enable_events=True,
                       expand_x=True,
                       expand_y=True,
                       pad=(30, 30),
                       s=(30, 5),
                       button_color=(sg.theme_text_color(), sg.theme_background_color()),
                       border_width=0,
                       font=fontbig
                       )]
        ]
        self.window = sg.Window('MainPage', mainpage, resizable=True).Finalize()
        # self.window.Maximize()

    def addaddpage(self):
        addpage = [
            # [sg.Button('Добавить организацию', key="-AddKomers-", enable_events=True,
            #            expand_x=True,
            #            expand_y=True,
            #            s=(30, 5),
            #            button_color=(sg.theme_text_color(), sg.theme_background_color()),
            #            border_width=0,
            #            pad=(30, 30),
            #            font=fontbig)],
            [sg.Button('Добавить проверенное ТС', key="-AddTs-", enable_events=True,
                       expand_x=True,
                       expand_y=True,
                       s=(30, 5),
                       button_color=(sg.theme_text_color(), sg.theme_background_color()),
                       border_width=0,
                       pad=(30, 30),
                       font=fontbig)],
            [sg.Button('Назад', key="-CloseAddPage-", enable_events=True,
                       expand_x=True,
                       s=(30, 5),
                       button_color=(sg.theme_text_color(), sg.theme_background_color()),
                       border_width=0,
                       pad=(30, 30),
                       font=fontbig)]
        ]
        self.addwindow = sg.Window('AddPage', addpage, resizable=True, element_justification="c").Finalize()

    @property
    def credentialspage(self):
        self.actnumber, self.dogovornumber = None, None  # reset
        credentials = [
            [sg.Text('Объект', font=fontbig), sg.InputCombo(["get bd"], key='-OBJECT-', font=fontmid)],
            # [sg.Button('Без номеров', font=fontbutton, size=(10, 0), button_color='gray', p=(20, 0)),
            [sg.Submit('Дальше', size=(15, 0), button_color='green', p=(40, 0), font=fontbutton),
             sg.Cancel('Отмена', button_color='red', font=fontbutton)]
        ]
        self.credentialswindow = sg.Window('Выбор объекта', credentials, resizable=True,
                                           element_justification="c").Finalize()
        while True:
            event, values = self.credentialswindow.read()

            if event == "Дальше":
                if values['-OBJECT-'] != '':
                    self.object = values["-OBJECT-"]
                    self.credentialswindow.close()
                    return 1
                else:
                    self.credentialswindow["-OBJECT-"].Update("")
                    sg.Window('Ошибочка',
                              [[sg.T('Заполните поле!', font=fontbig)], [sg.Button('Понял', font=fontbutton)]],
                              element_justification="c", no_titlebar=True, size=(400, 100), auto_close=True,
                              auto_close_duration=5).read(close=True)

            # elif event == "Без номеров":
            #     self.object = "Null"
            #     self.credentialswindow.close()
            #     return 1
            elif event in ('Отмена', sg.WIN_CLOSED):
                self.credentialswindow.close()
                return 0

    def addtspage(self, master, headername):
        global table1, table2
        headings = ['Объект', 'Наим.', 'Модель', 'S/N', 'Произв.', 'С1', 'С2', 'УФ', 'Фото', 'РГГ', 'РГГ пп',
                    'П', 'Состав']
        tabledata = [NULLLIST, ]
        addtspage = [
            [sg.Column(
                [[sg.Text('Объект', font=fontmid), sg.InputText(key='object', default_text=self.object, disabled=True,
                                                                s=(7, 5), text_color="black", font=fontmidlow)]]
                , justification="c"
            )],
            [sg.Column(
                [[sg.Text('Наименование ТС', font=fontmid),
                  sg.InputCombo(["нужна БД"], key='name', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="nameSAVE", font=fontmid)],
                 [sg.Text('Модель', font=fontmid),
                  sg.InputCombo(["нужна БД"], key='model', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="modelSAVE", font=fontmid)],
                 [sg.Text('Заводской номер', font=fontmid),
                  sg.InputCombo(["нужна БД"], key='part', enable_events=True, font=fontmid, s=(39, 0)),
                  sg.Checkbox("б/н", k="nopart", enable_events=True, font=fontmid),
                  sg.Checkbox("Сохр.", k="partSAVE", font=fontmid)],
                 [sg.Text('Производитель', font=fontmid),
                  sg.InputCombo(["нужна БД"], key='vendor', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="vendorSAVE", font=fontmid)],
                 [sg.Text('СЗЗ-1', font=fontmid), sg.InputText(key='serial1', font=fontmid, s=(15, 0)),
                  sg.Checkbox("Сохр.", k="serial1SAVE", font=fontmid)],
                 [sg.Text('СЗЗ-2', font=fontmid), sg.InputText(key='serial2', s=(10, 0), font=fontmid)]]  # count values
                , justification="c", element_justification="r"
            )],
            [sg.Column(
                [[sg.Checkbox("УФ", font=fontmid, key='uv'),
                  sg.Input(k="folder", visible=False),
                  sg.FolderBrowse('Папка с фото', k='folder', enable_events=True, visible=False, font=fontmidlow),
                  sg.Input(k='rgg', visible=False),
                  sg.FileBrowse("РГГ", k="rgg", font=fontmidlow),
                  sg.Text('РГГ пп', font=fontmid), sg.InputText(key='rggpp', s=(7, 0), font=fontmid)]]
                , justification="c")],
            [sg.Column(
                [[sg.Text('Признак (уровень)', font=fontmid),
                  sg.Combo(self.tsavailable, readonly=True, enable_events=True, key="level",
                           default_value=self.tsavailable[0], font=fontmidlow),
                  sg.Button("+", key="-ADDMORE-", visible=False, p=(15, 0), s=(3, 1), font=fontmid)],
                 # [sg.Text('Степень секретности', font=fontmid), sg.Combo(["С", "СС"], readonly=True, key='ss',
                 #                                                         default_value=self.ss, s=(5, 0),
                 #                                                         enable_events=True, font=fontmidlow),
                 #  sg.Text('Категория помещения', font=fontmid), sg.Combo(["2", "3"], readonly=True, key='kp',
                 #                                                         default_value=self.kp, s=(5, 0),
                 #                                                         enable_events=True, font=fontmidlow)]
                 ],
                justification="c", element_justification="c"
            )],
            [sg.Table(tabledata, headings=headings, justification='c', key="-TABLE-", visible=False,
                      auto_size_columns=True, expand_x=True, expand_y=True,
                      right_click_menu=['&Right', ['Редактировать', 'Удалить']], font=fontmidlow,
                      header_font=fontmidlow, enable_events=True)],
            [sg.Text('Назад', key="-CloseAddTsPage-", enable_events=True, justification="left", expand_x=True,
                     font=fontbutton),
             sg.Button("Сохранить", font=fontbutton),
             sg.Button("Новое ТС", font=fontbutton),
             ]
        ]
        self.addtswindow = sg.Window(headername, addtspage, resizable=True, return_keyboard_events=True,
                                     element_justification="").Finalize()
        self.addtswindow.Maximize()
        table = self.addtswindow['-TABLE-']
        tabledata.clear()
        table.Update(tabledata)
        # remove cols in table
        displaycolumns = deepcopy(headings)
        displaycolumns.remove('Объект')
        table.ColumnsToDisplay = displaycolumns
        table.Widget.configure(displaycolumns=displaycolumns)

        if self.tsavailable == ["Элемент"]:
            self.addtswindow['level'].update()

        if "Комплект" in self.tsavailable or "Составная часть" in self.tsavailable:
            self.addtswindow["-ADDMORE-"].update(visible=True)
            self.addtswindow["-TABLE-"].update(visible=True)
        else:
            self.addtswindow["-ADDMORE-"].update(visible=False)
            self.addtswindow["-TABLE-"].update(visible=False)

        if master:
            self.addtswindow["folder0"].update(visible=True)

        # fucking slaves get your ass back here
        if master == "slave":
            self.fun_slave()

        if master == "editor":
            self.fun_vieweditor()
            table.Update(self.tsdata[12])
            if self.tsavailable == ["Комплект", "Составная часть", "Элемент"]:
                table1 = self.tsdata[12]
            if self.tsavailable == ["Составная часть", "Элемент"]:
                table2 = self.tsdata[12]

        while True:  # TSPage
            event, values = self.addtswindow.read()

            if event == "level" and not master == "slave":
                if values[event] == "Комплект" or values[event] == "Составная часть":
                    self.addtswindow["-ADDMORE-"].update(visible=True)
                    self.addtswindow["-TABLE-"].update(visible=True)
                else:
                    self.addtswindow["-ADDMORE-"].update(visible=False)
                    self.addtswindow["-TABLE-"].update(visible=False)

            elif event == "-ADDMORE-" and not master == "slave":
                # вызов нового окна, обработка его возращаемного значения и добавление в таблицу
                page2 = Pages()
                page3 = Pages()

                if values["level"] == "Комплект":
                    page2.tsavailable = ["Составная часть", "Элемент"]
                    page2.object = self.object

                    page2.addtspage(master=False, headername="Добавление 2-го уровня")
                    table.Update(table1)
                else:
                    page3.tsavailable = ["Элемент"]
                    page3.object = self.object

                    page3.addtspage(master=False, headername="Добавление 3-го уровня")
                    table.Update(table2)

            elif event == "nopart":
                if values[event]:
                    self.addtswindow["part"].update("б/н", disabled=True)
                else:
                    self.addtswindow["part"].update("", disabled=False)

            elif event == "Сохранить":
                if master == "slave" or master == "editor":
                    self.tsdata = self.get_tsvalues(values)
                else:
                    if self.tsavailable == ["Составная часть", "Элемент"]:
                        self.insert_values_into_table(self.get_tsvalues(values), table1)
                    if self.tsavailable == ["Элемент"]:
                        self.insert_values_into_table(self.get_tsvalues(values), table2)
                if master == True:  # ♂oh shit im sorry♂
                    baza.add(self.get_tsvalues(values))

            elif event == "Новое ТС":
                whitelist = ['object', 'serial2', 'level', '-TABLE-', 'folder0', 'rgg1', 'nopart']
                savelist = ['name', 'model', 'part', 'vendor', 'serial1']
                rmlist = []

                for value in values:
                    if "SAVE" not in value and value not in whitelist:
                        rmlist.append(value)

                for item in savelist:
                    if values[item + "SAVE"]:
                        rmlist.remove(item)

                if values['nopart'] and values['partSAVE']:
                    self.addtswindow["part"].update("б/н", disabled=True)
                elif values['nopart'] and not values['partSAVE']:
                    self.addtswindow["part"].update("", disabled=False)
                    self.addtswindow['nopart'].Update(False)

                for item in rmlist:
                    if type(values[item]) is bool:
                        self.addtswindow[item].Update(False)
                    else:
                        self.addtswindow[item].Update('')

                if "Комплект" in self.tsavailable:
                    table1.clear()
                    table.Update("")
                if self.tsavailable == ["Составная часть", "Элемент"]:
                    table2.clear()
                    table.Update("")

            elif event == "Удалить":
                pos = int(values["-TABLE-"][0])

                if sg.PopupYesNo("Уверены что хотите удалить? ", auto_close_duration=7, auto_close=True) == "Yes":
                    if "Комплект" in self.tsavailable:
                        table1.pop(pos)
                        table.Update(table1)
                    if self.tsavailable == ["Составная часть", "Элемент"]:
                        table2.pop(pos)
                        table.Update(table2)

            elif event == "Редактировать":
                pos = int(values["-TABLE-"][0])
                tbl = table.Get()
                slave = Pages()
                slave.tsdata = tbl[pos]
                if values['level'] == "Комплект":
                    slave.tsavailable = ["Составная часть", "Элемент"]
                else:
                    slave.tsavailable = ["Элемент"]

                if master == "editor":
                    slave.addtspage(master="editor", headername="Редактирование элемента")
                else:
                    slave.addtspage(master="slave", headername="Редактирование элемента")

                if slave.tsavailable == ["Составная часть", "Элемент"]:
                    print("processing table1")
                    table1[pos] = slave.tsdata
                    table.Update(table1)
                if slave.tsavailable == ["Элемент"]:
                    print("processing table2")
                    table2[pos] = slave.tsdata
                    table.Update(table2)

            elif event == sg.WIN_CLOSED or event == "-CloseAddTsPage-" or event.startswith('Escape'):
                if values["level"] == "Комплект" and not master:
                    table1.clear()
                if values["level"] == "Составная часть" and not master:
                    table2.clear()
                self.addtswindow.close()
                break

    def fun_slave(self):
        allnames = ['object', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'uv', 'folder',
                    'rgg', 'rggpp', 'level', '-TABLE-']
        hideitems = ['nameSAVE', 'modelSAVE', 'partSAVE', 'nopart', 'vendorSAVE', 'serial1SAVE', 'Новое ТС',
                     '-ADDMORE-']
        for element in hideitems:
            self.addtswindow[element].Update(visible=False)
        for element, toput in zip(allnames, self.tsdata):
            self.addtswindow[element].update(toput)

    def fun_vieweditor(self):
        allnames = ['object', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'uv', 'folder',
                    'rgg', 'rggpp', 'level', '-TABLE-']
        hideitems = ['nameSAVE', 'modelSAVE', 'partSAVE', 'vendorSAVE', 'serial1SAVE', 'Новое ТС']
        for element in hideitems:
            self.addtswindow[element].Update(visible=False)
        for element, toput in zip(allnames, self.tsdata):
            self.addtswindow[element].update(toput)

    def insert_values_into_table(self, values, table):
        table.append(values)

    def get_tsvalues(self, values):
        allowed_list = ["object", "name", "model", "part", "vendor", "serial1", "serial2", "uv", "folder",
                        "rgg", "rggpp", "level"]
        listed = []

        for value in values:
            if value in allowed_list:
                listed.append(values[value])
        if values["level"] == "Составная часть" or "Комплект":
            temptable = []
            tables = self.addtswindow["-TABLE-"].Get()
            for table in tables:
                temptable.append(table)
            listed.append(temptable)
        return listed

    def add_komers_page(self):
        pass

    def dict_2_list(self, dict_obj):
        temp, temp2 = [], []
        if dict_obj["table"]:
            for z in dict_obj["table"]:
                if z["table"]:
                    for v in z["table"]:
                        temp2.append(list(v.values()))
                z["table"] = temp2.copy()
                temp2.clear()
                temp.append(list(z.values()))
        dict_obj["table"] = temp
        return list(dict_obj.values())

    def edit_ts_page(self, headername):
        def myFunc(e):
            return e[1]
        input_width = 80
        num_items_to_show = 20

        choices = baza.get_index_names("names")
        choices.sort(key=myFunc)

        editlayout = [
            [
                sg.Column([
                    [sg.Radio("Объект", "rad0", k='objects', enable_events=True, font=fontbig),
                     sg.Radio("Название", "rad0", k='names', default=True, enable_events=True, font=fontbig),
                     sg.Radio("Модель", "rad0", k="models", enable_events=True, font=fontbig),
                     sg.Radio("Серийный номер", "rad0", k="parts", enable_events=True, font=fontbig),
                     sg.Radio("Производитель", "rad0", k="vendors", enable_events=True, font=fontbig),
                     sg.Radio("СЗЗ", "rad0", k="serials", enable_events=True, font=fontbig)],
                    [sg.T("         ")],
                    [sg.T("ПОИСК ТС", font=fontbig)],
                    [sg.T("         ")],
                    [sg.Input(size=(input_width, 0), enable_events=True, key='-IN-', justification="l", font=fontbig)],
                    [sg.pin(sg.Col(
                        [[sg.Listbox(values=[], size=(input_width, num_items_to_show), enable_events=True, key='-BOX-',
                                     select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                        key='-BOX-CONTAINER-', pad=(0, 0)))]
                ], justification="c", element_justification="c")
            ],
            [
                sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                        enable_events=True, expand_x=True),
                sg.Submit("Открыть", key="-OPEN-", font=fontbutton),
            ]
        ]

        self.edittswidow = sg.Window(headername, editlayout, resizable=True, return_keyboard_events=True,
                                     element_justification="").Finalize()
        self.edittswidow.Maximize()

        list_element: sg.Listbox = self.edittswidow.Element('-BOX-')
        # store listbox element for easier access and to get to docstrings
        prediction_list, prediction_ids, input_text, sel_item = [], [], "", 0

        while True:
            event, values = self.edittswidow.read()

            if event == "-OPEN-" and values["-IN-"]:
                obj = baza.get_by_id(prediction_ids[sel_item])
                editor = Pages()
                editor.tsdata = self.dict_2_list(obj)
                editor.object = editor.tsdata[0]
                editor.addtspage(master="editor", headername="Редактирование и просмотр ТС")
                baza.update_element(prediction_ids[sel_item], editor.tsdata)

            elif event == "-CLOSE-":
                self.edittswidow.close()
                break

            # pressing down arrow will trigger event -IN- then aftewards event Down:40
            elif event.startswith('Escape'):
                self.edittswidow['-IN-'].update('')
            elif event.startswith('Down') and len(prediction_list):
                sel_item = (sel_item + 1) % len(prediction_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
            elif event.startswith('Up') and len(prediction_list):
                sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
            elif event == '\r':
                if len(values['-BOX-']) > 0:
                    self.edittswidow['-IN-'].update(value=values['-BOX-'])
            elif event == '-IN-':
                text = values['-IN-'].lower()
                if text == input_text:
                    continue
                else:
                    input_text = text
                prediction_list = []
                prediction_ids = []
                if text:
                    prediction_list = [f"{item[1]} {baza.get_display_values(item[0])}"
                                       for item in choices if item[1].lower().__contains__(text)]  # text
                    prediction_ids = [item[0] for item in choices if item[1].lower().__contains__(text)]  # ids

                list_element.update(values=prediction_list)
                sel_item = 0
                list_element.update(set_to_index=sel_item)

            elif event == '-BOX-':
                self.edittswidow['-IN-'].update(value=values['-BOX-'])

            elif event in ("objects", "names", "models", "parts", "vendors", "serials"):
                choices = baza.get_index_names(event)
                choices.sort(key=myFunc)

        self.edittswidow.close()


class SpUi:

    def makeui(self):
        pages = Pages()
        sg.theme('DarkAmber')
        pages.mainpage()

        while True:  # MainPage
            event, values = pages.window.read()
            if event == "-Add-":
                pages.window.Hide()
                pages.addaddpage()
                while True:  # Add Page
                    event, values = pages.addwindow.read()
                    if event == "-AddTs-":  # AddPage
                        pages.addwindow.Hide()
                        if pages.credentialspage:  # close check
                            pages.addtspage(master=True, headername="Добавление технического средства")
                            table1.clear()
                            table2.clear()

                        pages.addwindow.UnHide()
                    # elif event == "-AddKomers-":
                    #     # Добавление огранизации
                    #     pass

                    elif event == sg.WIN_CLOSED or event == "-CloseAddPage-":
                        pages.window.UnHide()
                        pages.addwindow.close()
                        break

            elif event == "-Edit-":
                # view + edit
                pages.window.Hide()
                pages.edit_ts_page("Редактирование")

                pages.window.UnHide()

            elif event == sg.WIN_CLOSED:
                break
            # mainpage event, values
        pages.window.close()

        # TODO Добавить функцию просмотра и редактирования ТС из базы
        # TODO Реализовать разные методы поиска ТС

        # TODO Реализовать метод вывода всех УНИКАЛЬНЫХ названий, моделей, вендоров и СЗЗ.
        # TODO Реализовать функцию автозаполнения (из примера autocompleteTest.py) полей "имя", "модель", "вендор"

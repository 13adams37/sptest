# from dearpygui import *
# may be later :(
import PySimpleGUI as sg
import db
from copy import deepcopy

NULLLIST = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
table1, table2 = [], []
fontbig = ("Arial", 24)
fontbutton = ("Helvetica", 20)
fontmid = ("Arial Baltic", 18)
fontmidlow = ("Arial Baltic", 16)

names = ['Roberta', 'Kylie', 'Jenny', 'Helen',
         'Andrea', 'Meredith', 'Deborah', 'Pauline',
         'Belinda', 'Wendy']
tablenames = ['Roberta', 'Kylie', 'Jenny', 'Helen',
         'Andrea', 'Meredith', 'Deborah', 'Pauline',
         'Belinda', 'Wendy']


class Pages:
    def __init__(self):
        self.window = None
        self.addtswindow = None
        self.addwindow = None
        self.credentialswindow = None
        self.viewwindow = None
        self.addkomerswindow = None
        self.edittswidow = None

        self.dogovornumber = None
        self.actnumber = None
        self.ss = None
        self.kp = None
        self.tsdata = []
        # self.tabledata = None
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
            [sg.Button('Добавить организацию', key="-AddKomers-", enable_events=True,
                       expand_x=True,
                       expand_y=True,
                       s=(30, 5),
                       button_color=(sg.theme_text_color(), sg.theme_background_color()),
                       border_width=0,
                       pad=(30, 30),
                       font=fontbig)],
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
            [sg.Text('Договор', font=fontbig), sg.InputCombo(["get bd"], key='-DOGOVOR-', font=fontmid)],
            [sg.Text('Акт', font=fontbig), sg.InputCombo(["get bd"], key='-AKT-', font=fontmid)],
            [sg.Button('Без номеров', font=fontbutton, size=(10, 0), button_color='gray', p=(20, 0)),
             sg.Submit('Дальше', size=(15, 0), button_color='green', p=(40, 0), font=fontbutton),
             sg.Cancel('Отмена', button_color='red', font=fontbutton)]
        ]
        self.credentialswindow = sg.Window('DogovorPage', credentials, resizable=True,
                                           element_justification="c").Finalize()
        while True:
            event, values = self.credentialswindow.read()
            if event == "Дальше":
                if values['-DOGOVOR-'] and values['-AKT-'] != '':
                    self.dogovornumber = values["-DOGOVOR-"]
                    self.actnumber = values["-AKT-"]
                    self.credentialswindow.close()
                    return 1
                else:
                    self.credentialswindow["-DOGOVOR-"].Update("")
                    self.credentialswindow["-AKT-"].Update("")
                    sg.Window('Ошибочка',
                              [[sg.T('Заполните поля!', font=fontbig)], [sg.Button('Понял', font=fontbutton)]],
                              element_justification="c", no_titlebar=True, size=(400, 100), auto_close=True,
                              auto_close_duration=5).read(close=True)

            elif event == "Без номеров":
                self.dogovornumber = "Null"
                self.actnumber = "Null"
                self.credentialswindow.close()
                return 1
            elif event in ('Отмена', sg.WIN_CLOSED):
                self.credentialswindow.close()
                return 0

    def addtspage(self, master, headername):
        headings = ['Дог.', 'Акт', 'Наим.', 'Модель', 'S/N', 'Произв.', 'С1', 'С2', 'УФ', 'Фото', 'РГГ', 'РГГ пп',
                    'П', 'Сек', 'Кат.', 'Состав']
        tabledata = [NULLLIST, ]
        addtspage = [
            [sg.Column(
                [[sg.Text('Договор', font=fontmid),
                  sg.InputText(key='dogovor', default_text=self.dogovornumber, disabled=True, s=(7, 5),
                               text_color="black", font=fontmidlow),
                  sg.Text('Акт', font=fontmid), sg.InputText(key='act', default_text=self.actnumber, disabled=True,
                                                             s=(7, 5), text_color="black", font=fontmidlow)]]
                , justification="c"
            )],
            [sg.Column(
                [[sg.Text('Наименование ТС', font=fontmid),
                  sg.InputCombo(names, key='name', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="nameSAVE", font=fontmid)],
                 # input + spisok. link model, vendor
                 [sg.Text('Модель', font=fontmid),
                  sg.InputCombo(["нужна БД"], key='model', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="modelSAVE", font=fontmid)],
                 # input, link tsname, vendor
                 [sg.Text('Заводской номер', font=fontmid),
                  sg.InputCombo(["нужна БД"], key='part', enable_events=True, font=fontmid, s=(39, 0)),
                  sg.Checkbox("б/н", k="nopart", enable_events=True, font=fontmid),
                  sg.Checkbox("Сохр.", k="partSAVE", font=fontmid)],
                 [sg.Text('Производитель', font=fontmid),
                  sg.InputCombo(["нужна БД"], key='vendor', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="vendorSAVE", font=fontmid)],
                 # input + spisok. link tsname, model
                 [sg.Text('СЗЗ-1', font=fontmid), sg.InputText(key='serial1', font=fontmid, s=(15, 0)),
                  sg.Checkbox("Сохр.", k="serial1SAVE", font=fontmid)],
                 [sg.Text('СЗЗ-2', font=fontmid), sg.InputText(key='serial2', s=(10, 0), font=fontmid)]]  # count values
                , justification="c", element_justification="r"
            )],  # locked + kol-vo objects in LEVEL
            [sg.Column(
                [[sg.Checkbox("УФ", font=fontmid, key='uv'),
                  sg.Input(k="folder", visible=False),
                  sg.FolderBrowse('Папка с фото', k='folder', enable_events=True, visible=False, font=fontmidlow),
                  # sg.Text('РГГ', font=fontmid),
                  sg.Input(k='rgg', visible=False),
                  sg.FileBrowse("РГГ", k="rgg", font=fontmidlow),
                  sg.Text('РГГ пп', font=fontmid), sg.InputText(key='rggpp', s=(7, 0), font=fontmid)]]
                , justification="c")],
            [sg.Column(
                [[sg.Text('Признак (уровень)', font=fontmid),
                  sg.Combo(self.tsavailable, readonly=True, enable_events=True, key="level",
                           default_value=self.tsavailable[0], font=fontmidlow),
                  sg.Button("+", key="-ADDMORE-", visible=False, p=(15, 0), s=(3, 1), font=fontmid)],
                 [sg.Text('Степень секретности', font=fontmid), sg.Combo(["С", "СС"], readonly=True, key='ss',
                                                                         default_value=self.ss, s=(5, 0),
                                                                         enable_events=True, font=fontmidlow),
                  sg.Text('Категория помещения', font=fontmid), sg.Combo(["2", "3"], readonly=True, key='kp',
                                                                         default_value=self.kp, s=(5, 0),
                                                                         enable_events=True, font=fontmidlow)]],
                justification="c", element_justification="c"
            )],
            [sg.Table(tabledata, headings=headings, justification='c', key="-TABLE-", visible=False,
                      auto_size_columns=True, expand_x=True, expand_y=True,
                      right_click_menu=['&Right', ['Редактировать', 'Удалить']], font=fontmidlow,
                      header_font=fontmidlow)],
            [sg.Text('Закрыть', key="-CloseAddTsPage-", enable_events=True, justification="left", expand_x=True,
                     font=fontbutton),
             sg.Button("Сохранить", font=fontbutton),
             # sg.Submit('Обновить', size=(10, 0), k="-REFR-", button_color='gray', p=(20, 0), font=fontbutton),
             sg.Button("Новое ТС", font=fontbutton),
             ]
        ]
        self.addtswindow = sg.Window(headername, addtspage, resizable=True,
                                     element_justification="").Finalize()
        self.addtswindow.Maximize()
        table = self.addtswindow['-TABLE-']
        tabledata.clear()
        table.Update(tabledata)
        # remove first 2 cols in table
        displaycolumns = deepcopy(headings)
        displaycolumns.remove('Дог.')
        displaycolumns.remove('Акт')
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

        print("prep done")
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
                self.ss = self.addtswindow["ss"].Get()
                self.kp = self.addtswindow["kp"].Get()
                page2 = Pages()
                page3 = Pages()
                if values["level"] == "Комплект":
                    page2.tsavailable = ["Составная часть", "Элемент"]
                    page2.actnumber = self.actnumber
                    page2.dogovornumber = self.dogovornumber
                    page2.ss = self.ss
                    page2.kp = self.kp

                    page2.addtspage(master=False, headername="Добавление 2-го уровня")
                    table.Update(table1)
                else:
                    page3.tsavailable = ["Элемент"]
                    page3.actnumber = self.actnumber
                    page3.dogovornumber = self.dogovornumber
                    page3.ss = self.ss
                    page3.kp = self.kp

                    page3.addtspage(master=False, headername="Добавление 3-го уровня")
                    table.Update(table2)

            elif event == "nopart":
                if values[event]:
                    self.addtswindow["part"].update("б/н", disabled=True)
                else:
                    self.addtswindow["part"].update("", disabled=False)

            elif event == "Сохранить":
                if master == "slave":
                    self.tsdata = self.get_tsvalues(values)
                else:
                    if self.tsavailable == ["Составная часть", "Элемент"]:
                        self.insert_values_into_table(self.get_tsvalues(values), table1)
                    if self.tsavailable == ["Элемент"]:
                        self.insert_values_into_table(self.get_tsvalues(values), table2)
                if master:
                    baza = db.DataBase()
                    baza.add(self.get_tsvalues(values))

            elif event == "Новое ТС":
                whitelist = ['dogovor', 'act', 'serial2', 'level', 'ss', 'kp', '-TABLE-', 'folder0', 'rgg1', 'nopart']
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
                slave.addtspage(master="slave", headername="Редактирование элемента")
                if values['level'] == "Комплект" and table1:
                    table1[pos] = slave.tsdata
                    table.Update(table1)
                else:
                    table2[pos] = slave.tsdata
                    table.Update(table2)

            elif event == sg.WIN_CLOSED or event == "-CloseAddTsPage-":
                if values["level"] == "Комплект" and not master:
                    table1.clear()
                if values["level"] == "Элемент" and not master:
                    table2.clear()
                self.addtswindow.close()
                break

    def fun_slave(self):
        allnames = ['dogovor', 'act', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'uv', 'folder',
                    'rgg', 'rggpp', 'level', 'ss', 'kp', '-TABLE-']
        hideitems = ['nameSAVE', 'modelSAVE', 'partSAVE', 'nopart', 'vendorSAVE', 'serial1SAVE', 'Новое ТС',
                     '-ADDMORE-']
        for element in hideitems:
            self.addtswindow[element].Update(visible=False)
        for element, toput in zip(allnames, self.tsdata):
            self.addtswindow[element].update(toput)

    def insert_values_into_table(self, values, table):
        table.append(values)

    def get_tsvalues(self, values):
        allowed_list = ["dogovor", "act", "name", "model", "part", "vendor", "serial1", "serial2", "uv", "folder",
                        "rgg", "rggpp", "level", "ss", "kp"]
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

    def edit_ts_page(self):
        editlayout = [
            [
                sg.Column([
                    [sg.T]
                ])
            ],
        ]
        pass
        # show all
        # search everywhere
        # search by act / dogovor
        # search by name
        # search by model
        # search by (contains part)
        # search by vendor
        # search by szz1
        # search by rg

        # multiple search?


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
                    elif event == "-AddKomers-":
                        # Добавление огранизации
                        pass

                    elif event == sg.WIN_CLOSED or event == "-CloseAddPage-":
                        pages.window.UnHide()
                        pages.addwindow.close()
                        break

            elif event == "-Edit-":
                # view + edit
                pass

            elif event == sg.WIN_CLOSED:
                break
            # mainpage event, values
        pages.window.close()

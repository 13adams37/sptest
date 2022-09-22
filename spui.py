# from dearpygui import *
# may be later :(
import PySimpleGUI as sg

NULLLIST = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
table1, table2 = [], []


class Pages:
    def __init__(self):
        self.window = None
        self.addtswindow = None
        self.addwindow = None
        self.credentialswindow = None

        self.dogovornumber = None
        self.actnumber = None
        self.ss = None
        self.kp = None
        self.tsdata = []
        # self.tabledata = None
        self.tsavailable = ["Изделие", "Элемент", "Составная часть"]

    def mainpage(self):
        mainpage = [
            [sg.Button('Добавление', key="-Add-", enable_events=True,
                       expand_x=True,
                       expand_y=True,
                       pad=(30, 30),
                       s=(30, 5),
                       button_color=(sg.theme_text_color(), sg.theme_background_color()),
                       border_width=0,
                       )],
            [sg.Button('Редактирование', key="-Edit-", enable_events=True,
                       expand_x=True,
                       expand_y=True,
                       pad=(30, 30),
                       s=(30, 5),
                       button_color=(sg.theme_text_color(), sg.theme_background_color()),
                       border_width=0,
                       )]
        ]
        self.window = sg.Window('MainPage', mainpage, resizable=True).Finalize()

    def addaddpage(self):
        addpage = [
            [sg.Button('Добавить организацию', key="-AddKomers-", enable_events=True,
                       expand_x=True,
                       expand_y=True,
                       s=(30, 5),
                       button_color=(sg.theme_text_color(), sg.theme_background_color()),
                       border_width=0,
                       pad=(30, 30))],
            [sg.Button('Добавить проверенное ТС', key="-AddTs-", enable_events=True,
                       expand_x=True,
                       expand_y=True,
                       s=(30, 5),
                       button_color=(sg.theme_text_color(), sg.theme_background_color()),
                       border_width=0,
                       pad=(30, 30))],
            [sg.Button('Закрыть', key="-CloseAddPage-", enable_events=True,
                       expand_x=True,
                       s=(30, 5),
                       button_color=(sg.theme_text_color(), sg.theme_background_color()),
                       border_width=0,
                       pad=(30, 30))]
        ]
        self.addwindow = sg.Window('AddPage', addpage, resizable=True, element_justification="c").Finalize()

    @property
    def credentialspage(self):
        self.actnumber, self.dogovornumber = None, None  # reset
        credentials = [
            [sg.Text('Договор'), sg.InputCombo(["get bd"], key='-DOGOVOR-')],
            [sg.Text('Акт'), sg.InputCombo(["get bd"], key='-AKT-')],
            [sg.Button('Без номеров', size=(10, 0), button_color='gray', p=(20, 0)),
             sg.Submit('Дальше', size=(15, 0), button_color='green', p=(40, 0)),
             sg.Cancel('Отмена', button_color='red')]
        ]
        self.credentialswindow = sg.Window('DogovorPage', credentials, resizable=True,
                                           element_justification="c").Finalize()
        while True:
            event, values = self.credentialswindow.read()
            if event == "Дальше":
                if values['-DOGOVOR-'] and values['-AKT-'] != '':
                    self.dogovornumber = values["-DOGOVOR-"]
                    self.actnumber = values["-AKT-"]
                else:
                    sg.Window('Ошибочка', [[sg.T('Заполните поля!')], [sg.Button('Понял')]],
                              element_justification="c", no_titlebar=True).read(close=True)
                    self.credentialswindow.close()
                    return 0
                self.credentialswindow.close()
                return 1
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
                [[sg.Text('Договор'),
                  sg.InputText(key='dogovor', default_text=self.dogovornumber, disabled=True, s=(5, 0),
                               text_color="black"),
                  sg.Text('Акт'), sg.InputText(key='act', default_text=self.actnumber, disabled=True, s=(5, 0),
                                               text_color="black")]]
                , justification="c"
            )],
            [sg.Column(
                [[sg.Text('Наименование ТС'), sg.InputCombo(["нужна БД"], key='name', size=(45, 0)),
                  sg.Checkbox("Сохр.", k="nameSAVE")],
                 # input + spisok. link model, vendor
                 [sg.Text('Модель'), sg.InputCombo(["нужна БД"], key='model', size=(45, 0)),
                  sg.Checkbox("Сохр.", k="modelSAVE")],
                 # input, link tsname, vendor
                 [sg.Text('Заводской номер'), sg.InputText(key='part', enable_events=True),
                  sg.Checkbox("б/н", k="nopart", enable_events=True), sg.Checkbox("Сохр.", k="partSAVE")],
                 [sg.Text('Производитель'), sg.InputCombo(["нужна БД"], key='vendor', size=(45, 0)),
                  sg.Checkbox("Сохр.", k="vendorSAVE")],
                 # input + spisok. link tsname, model
                 [sg.Text('СЗЗ-1'), sg.InputText(key='serial1'), sg.Checkbox("Сохр.", k="serial1SAVE")],
                 [sg.Text('СЗЗ-2'), sg.InputText(key='serial2')]]  # count values
                , justification="r", element_justification="r"
            )],  # locked + kol-vo objects in LEVEL
            [sg.Column(
                [[sg.Checkbox("УФ", key='uv'),
                  sg.Input(k="folder", visible=False), sg.FolderBrowse('Папка с фото', k='folder'),
                  sg.Text('РГГ'), sg.Input(k='rgg', visible=False), sg.FileBrowse("Фото РГГ", k="rgg"),
                  sg.Text('РГГ пп'), sg.InputText(key='rggpp', s=(7, 0))]]
                , justification="c")],
            [sg.Column(
                [[sg.Text('Признак (уровень)'),
                  sg.Combo(self.tsavailable, readonly=True, enable_events=True, key="level",
                           default_value=self.tsavailable[0]),
                  sg.Button("+", key="-ADDMORE-", visible=False, p=(15, 0), s=(4, 2))],
                 [sg.Text('Степень секретности'), sg.Combo(["С", "СС"], readonly=True, key='ss',
                                                           default_value=self.ss, s=(5, 0), enable_events=True),
                  sg.Text('Категория помещения'), sg.Combo(["1", "2"], readonly=True, key='kp',
                                                           default_value=self.kp, s=(5, 0), enable_events=True)]],
                justification="c", element_justification="c"
            )],
            [sg.Table(tabledata, headings=headings, justification='l', key="-TABLE-", visible=False,
                      auto_size_columns=True, max_col_width=5,
                      right_click_menu=['&Right', ['Редактировать', 'Удалить']])],
            [sg.Text('Закрыть', key="-CloseAddTsPage-", enable_events=True, justification="left", expand_x=True),
             sg.Button("Сохранить"),
             sg.Submit('Обновить', size=(10, 0), k="-REFR-", button_color='gray', p=(20, 0)),
             sg.Button("Новое ТС"),
             ]
        ]
        self.addtswindow = sg.Window(headername, addtspage, resizable=True,
                                     element_justification="").Finalize()
        table = self.addtswindow['-TABLE-']
        tabledata.clear()
        if self.tsavailable == ["Составная часть"]:
            self.addtswindow['level'].update()
        if "Изделие" in self.tsavailable or "Элемент" in self.tsavailable:
            self.addtswindow["-ADDMORE-"].update(visible=True)
            self.addtswindow["-TABLE-"].update(visible=True)
        else:
            self.addtswindow["-ADDMORE-"].update(visible=False)
            self.addtswindow["-TABLE-"].update(visible=False)
        if not master:
            self.addtswindow["folder"].update(visible=False)

        # fucking slaves get your ass back here
        if master == "slave":
            self.fun_slave()

        while True:  # TSPage
            event, values = self.addtswindow.read()

            if event == "-REFR-":
                print(values["-TABLE-"])  # get a picked table element position
                print(table.Get())
            elif event == "level" and not master == "slave":
                if values[event] == "Изделие" or values[event] == "Элемент":
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
                if values["level"] == "Изделие":
                    page2.tsavailable = ["Элемент", "Составная часть"]
                    page2.actnumber = self.actnumber
                    page2.dogovornumber = self.dogovornumber
                    page2.ss = self.ss
                    page2.kp = self.kp
                    # page2.tsdata = page3.tsdata

                    page2.addtspage(master=False, headername="Добавление 2-го уровня")
                    table.Update(table1)
                    print("updating table1")
                else:
                    page3.tsavailable = ["Составная часть"]
                    page3.actnumber = self.actnumber
                    page3.dogovornumber = self.dogovornumber
                    page3.ss = self.ss
                    page3.kp = self.kp

                    page3.addtspage(master=False, headername="Добавление 3-го уровня")
                    table.Update(table2)  # insert tsvalues into table2
                    print("updating table2")

            elif event == "nopart":
                if values[event]:
                    self.addtswindow["part"].update("б/н", disabled=True)
                else:
                    self.addtswindow["part"].update("", disabled=False)

            elif event == "Сохранить":
                # push to db if master
                if master == "slave":
                    self.tsdata = self.get_tsvalues(values)
                else:
                    if self.tsavailable == ["Элемент", "Составная часть"]:
                        print("save table1")
                        self.insert_values_into_table(self.get_tsvalues(values), table1)
                    if self.tsavailable == ["Составная часть"]:
                        print("save table2")
                        self.insert_values_into_table(self.get_tsvalues(values), table2)

            elif event == "Новое ТС":
                whitelist = ['dogovor', 'act', 'serial2', 'level', 'ss', 'kp', '-TABLE-', 'folder0', 'rgg1', 'nopart']
                savelist = ['name', 'model', 'part', 'vendor', 'serial1']
                rmlist = []
                for value in values:
                    print(value)
                    if "SAVE" not in value and value not in whitelist:
                        rmlist.append(value)
                print("rmlist1 =", rmlist)

                for item in savelist:
                    if values[item + "SAVE"]:
                        print("saving item =", item)
                        rmlist.remove(item)
                    print("not passed", item)

                if values['nopart'] and values['partSAVE']:
                    self.addtswindow["part"].update("б/н", disabled=True)
                    # rmlist.remove('part')
                elif values['nopart'] and not values['partSAVE']:
                    self.addtswindow["part"].update("", disabled=False)
                    self.addtswindow['nopart'].Update(False)

                for item in rmlist:
                    if type(values[item]) is bool:
                        self.addtswindow[item].Update(False)
                    else:
                        self.addtswindow[item].Update('')
                print(rmlist)
                # delete table
                if "Изделие" in self.tsavailable:
                    table1.clear()
                    table.Update("")
                if self.tsavailable == ["Элемент", "Составная часть"]:
                    table2.clear()
                    table.Update("")

            elif event == "Удалить":
                test = []
                pos = int(values["-TABLE-"][0])
                tbl = table.Get()

                print(pos)
                print(tbl)
                print(tbl[pos])
                print(values)

                # confirm deletion, then delete
            elif event == "Редактировать":
                pos = int(values["-TABLE-"][0])
                tbl = table.Get()
                # SAVE
                slave = Pages()
                slave.tsdata = tbl[pos]
                slave.addtspage(master="slave", headername="fucking slave")
                if "Изделие" in self.tsavailable:
                    table1[pos] = slave.tsdata
                    table.Update(table1)
                if self.tsavailable == ["Элемент", "Составная часть"]:
                    table2[pos] = slave.tsdata
                    table.Update(table2)

                # create new tswindow, without save checkboxes and newts buttons

            elif event == sg.WIN_CLOSED or event == "-CloseAddTsPage-":
                if values["level"] == "Изделие" and not master:
                    print("deleting table1")
                    table1.clear()
                if values["level"] == "Элемент" and not master:
                    print("deleting table2")
                    table2.clear()
                self.addtswindow.close()
                break

    def fun_slave(self):
        # items = ['Null', 'Null', '1337LEET', '', '', '', '', '', False, '', '', '', 'Элемент', '', '', []]
        allnames = ['dogovor', 'act', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'uv', 'folder',
                    'rgg', 'rggpp', 'level', 'ss', 'kp', '-TABLE-']  # 16
        hideitems = ['nameSAVE', 'modelSAVE', 'partSAVE', 'nopart', 'vendorSAVE', 'serial1SAVE', 'Новое ТС', '-ADDMORE-']
        for element in hideitems:
            self.addtswindow[element].Update(visible=False)
        for element, toput in zip(allnames, self.tsdata):
            print(element, toput)
            self.addtswindow[element].update(toput)
        # self.addtswindow['-TABLE-'].Update(self.tsdata)

    def insert_values_into_table(self, values, table):
        table.append(values)

    def get_tsvalues(self, values):
        allowed_list = ["dogovor", "act", "name", "model", "part", "vendor", "serial1", "serial2", "uv", "folder",
                        "rgg", "rggpp", "level", "ss", "kp"]
        listed = []

        for value in values:
            if value in allowed_list:
                listed.append(values[value])
        if values["level"] == "Элемент" or "Изделие":
            temptable = []
            tables = self.addtswindow["-TABLE-"].Get()
            for table in tables:
                temptable.append(table)
            print("temp table =", temptable)
            listed.append(temptable)
        print("listed =", listed)
        return listed


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

            elif event == sg.WIN_CLOSED:
                break
            # mainpage event, values
        pages.window.close()

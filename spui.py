# from dearpygui import *
# may be later :(
import PySimpleGUI as sg

NULLLIST = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
table1, table2 = [], []


class Pages:
    def __init__(self):
        self.window = None
        self.addtswindow = None
        self.addwindow = None
        self.credentialswindow = None

        self.dogovornumber = None
        self.actnumber = None
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
        headings = ['Дог.', 'Акт', 'Наим.', 'Модель', 'S/N', 'Произв.', 'С1', 'С2', 'УФ', 'РГГ', 'РГГ пп', 'П', 'Сек',
                    'Кат.', 'Состав']
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
                [[sg.Text('Наименование ТС'), sg.InputCombo(["get from bd + kostil"], key='name', size=(45, 0)),
                  sg.Checkbox("Save", k="-TSSAVE-")],
                 # input + spisok. link model, vendor
                 [sg.Text('Модель'),
                  sg.InputCombo(["get from bd + kostil"], key='model', size=(45, 0)),
                  sg.Checkbox("Сохр.", k="-MODELSAVE-")],
                 # input, link tsname, vendor
                 [sg.Text('Заводской номер'), sg.InputText(key='partnumber', enable_events=True),
                  sg.Checkbox("б/н", k="nopart", enable_events=True)],  # mb add save button
                 [sg.Text('Производитель'), sg.InputCombo(["get from bd + kostil"], key='vendor', size=(45, 0)),
                  sg.Checkbox("Сохр.", k="-VENDORSAVE-")],
                 # input + spisok. link tsname, model
                 [sg.Text('СЗЗ-1'), sg.InputText(key='serial1'), sg.Checkbox("Сохр.", k="-CZZAUTO-")],
                 # locked, checkbox + nextint
                 [sg.Text('СЗЗ-2'), sg.InputText(key='serial2')]]
                , justification="r", element_justification="r"
            )],  # locked + kol-vo objects in LEVEL
            [sg.Column(
                [[sg.Checkbox("УФ", key='uv'), sg.Text('РГГ'), sg.InputText(key='rgg', visible=False),
                  sg.FileBrowse(),
                  sg.Text('РГГ пп'), sg.InputText(key='rggpp', s=(7, 0))]]
                , justification="c")],
            [sg.Column(
                [[sg.Text('Признак (уровень)'),
                  sg.Combo(self.tsavailable, readonly=True, enable_events=True, key="level",
                           default_value=self.tsavailable[0]),
                  sg.Button("+", key="-ADDMORE-", visible=False, p=(15, 0), s=(4, 2))],
                 [sg.Text('Степень секретности'), sg.Combo(["С", "СС"], readonly=True, key='ss', s=(5, 0)),  # spisok
                  sg.Text('Категория помещения'), sg.Combo(["1", "2"], readonly=True, key='kp', s=(5, 0))]],
                justification="c", element_justification="c"
            )],
            [sg.Table(tabledata, headings=headings, justification='l', key="-TABLE-", visible=False,
                      auto_size_columns=True, max_col_width=5)],
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

        while True:  # TSPage
            event, values = self.addtswindow.read()

            if event == "-REFR-":
                print(values["-TABLE-"])  # get a picked table element position
                print(table.Get())
            elif event == "level":
                if values[event] == "Изделие" or values[event] == "Элемент":
                    self.addtswindow["-ADDMORE-"].update(visible=True)
                    self.addtswindow["-TABLE-"].update(visible=True)
                else:
                    self.addtswindow["-ADDMORE-"].update(visible=False)
                    self.addtswindow["-TABLE-"].update(visible=False)
            elif event == "-ADDMORE-":
                # вызов нового окна, обработка его возращаемного значения и добавление в таблицу
                page2 = Pages()
                page3 = Pages()
                if values["level"] == "Изделие":
                    page2.tsavailable = ["Элемент", "Составная часть"]
                    page2.actnumber = self.actnumber
                    page2.dogovornumber = self.dogovornumber
                    page2.tsdata = page3.tsdata

                    page2.addtspage(master=False, headername="Добавление 2-го уровня")
                    table.Update(table1)
                    # if not master:
                    #     table1.clear()
                    #     print("deleting table1")
                    print("updating table1")
                else:
                    page3.tsavailable = ["Составная часть"]
                    page3.actnumber = self.actnumber
                    page3.dogovornumber = self.dogovornumber

                    page3.addtspage(master=False, headername="Добавление 3-го уровня")
                    table.Update(table2)  # insert tsvalues into table2
                    # if not master:
                    #     table2.clear()
                    #     print("deleting table2")
                    print("updating table2")

                print("debug master")

            elif event == "nopart":
                if values[event]:
                    self.addtswindow["partnumber"].update("б/н", disabled=True)
                else:
                    self.addtswindow["partnumber"].update("", disabled=False)

            elif event == "Сохранить":
                # ts_values = self.get_ts_values(values)
                # self.tsdata.append(ts_values)  # extend or append?
                # if self.tsdata != ts_values:
                #     # self.tsdata += ts_values
                #     self.tsdata.extend(ts_values)
                # else:
                #     print("you shall not pass")

                # table1.extend(self.tsdata) if values["level"] == "Изделие" else table2.append(self.tsdata)

                # push to db if master

                if values["level"] == "Элемент":
                    # put tsvalues (L2) into table1
                    self.insert_values_into_table(self.get_tsvalues(values), table1)
                else:
                    # put tsvalues (L3) into table2
                    self.insert_values_into_table(self.get_tsvalues(values), table2)

            elif event == "Новое ТС":
                # clear fileds without checkboxes
                print("new ts")

            elif event == sg.WIN_CLOSED or event == "-CloseAddTsPage-":
                if values["level"] == "Изделие" and not master:
                    print("deleting table1")
                    table1.clear()
                elif values["level"] == "Элемент" and not master:
                    print("deleting table2")
                    table2.clear()
                self.addtswindow.close()
                break

    def insert_values_into_table(self, values, table):
        table.append(values)

    def get_tsvalues(self, values):
        allowed_list = ["dogovor", "act", "name", "model", "partnumber", "vendor", "serial1", "serial2", "uv", "rgg",
                        "rggpp", "level", "ss", "kp"]
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

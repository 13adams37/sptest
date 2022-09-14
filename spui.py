# from dearpygui import *
# may be later :(
import PySimpleGUI as sg


class Pages:
    def __init__(self):
        self.window = None
        self.addtswindow = None
        self.addwindow = None
        self.credentialswindow = None

        self.dogovornumber = None
        self.actnumber = None
        self.tsdata = None
        self.tsstate = None

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

    def addtspage(self):
        headings = ['Дог.', 'Акт', 'Наим.', 'Модель', 'S/N', 'Произв.', 'С1', 'С2', 'УФ', 'РГГ', 'РГГ пп', 'П', 'Сек',
                    'Кат.']
        self.tsdata = [
            ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ],
        ]
        addtspage = [
            [sg.Column(
                [[sg.Text('Договор'),
                  sg.InputText(key='-DOGOVOR-', default_text=self.dogovornumber, disabled=True, s=(5, 0),
                               text_color="black"),
                  sg.Text('Акт'), sg.InputText(key='-AKT-', default_text=self.actnumber, disabled=True, s=(5, 0),
                                               text_color="black")]]
                , justification="c"
            )],
            [sg.Column(
                [[sg.Text('Наименование ТС'), sg.InputCombo(["get from bd + kostil"], key='-TSNAME-', size=(45, 0)),
                  sg.Checkbox("Save", k="-TSSAVE-")],
                 # input + spisok. link model, vendor
                 [sg.Text('Модель'),
                  sg.InputCombo(["get from bd + kostil"], key='-MODEL-', size=(45, 0)),
                  sg.Checkbox("Save", k="-MODELSAVE-")],
                 # input, link tsname, vendor
                 [sg.Text('Заводской номер'), sg.InputText(key='-PARTNUMBER-')],  # mb add save button
                 [sg.Text('Производитель'), sg.InputCombo(["get from bd + kostil"], key='-VENDOR-', size=(45, 0)),
                  sg.Checkbox("Save", k="-VENDORSAVE-")],
                 # input + spisok. link tsname, model
                 [sg.Text('СЗЗ-1'), sg.InputText(key='-CZZ1-'), sg.Checkbox("Авто", k="-CZZAUTO-")],
                 # locked, checkbox + nextint
                 [sg.Text('СЗЗ-2'), sg.InputText(key='-CZZ2-')]]
                , justification="r", element_justification="r"
            )],  # locked + kol-vo objects in LEVEL
            [sg.Column(
                [[sg.Checkbox("УФ", key='-UF-'), sg.Text('РГГ'), sg.InputText(key='-RGG-', visible=False),
                  sg.FileBrowse(),
                  sg.Text('РГГ пп'), sg.InputText(key='-RGGPP-', s=(7, 0))]]
                , justification="c")],
            [sg.Column(
                [[sg.Text('Признак (уровень)'),
                  sg.Combo(["Изделие", "Элемент", "Составная часть"], readonly=True, enable_events=True,
                           key="-LEVEL-"), sg.Button("+", key="-ADDMORE-", visible=False, p=(15, 0), s=(4, 2))],
                 [sg.Text('Степень секретности'), sg.Combo(["С", "СС"], readonly=True, key='-SS-', s=(5, 0)),  # spisok
                  sg.Text('Категория помещения'), sg.Combo(["1", "2"], readonly=True, key='-KP-', s=(5, 0))]],
                justification="c", element_justification="c"
            )],
            [sg.Table(self.tsdata, headings=headings, justification='l', key="-TABLE-", visible=False)],
            [sg.Text('Закрыть', key="-CloseAddTsPage-", enable_events=True, justification="left", expand_x=True),
             sg.Button("Сохранить"),
             sg.Submit('Обновить', size=(10, 0), k="-REFR-", button_color='gray', p=(20, 0)),
             sg.Button("Новое ТС"),
             ]
        ]
        self.addtswindow = sg.Window('AddTsPage', addtspage, resizable=True, element_justification="").Finalize()
        # state handler:
        # 0 = master, can add two slaves, or not, depends of TS type!
        # 1 = slave1 of master, can add slave2 or no, depends on type of TS!
        # 2 = slave2 of slave1, slave2 cant add more slaves

        while True:  # TSPage
            event, values = self.addtswindow.read()
            # TSPage realisation
            if event == "-REFR-":
                print(values)
            elif event == "-LEVEL-":
                if values[event] == "Изделие" or values[event] == "Элемент":
                    self.addtswindow["-ADDMORE-"].update(visible=True)
                    self.addtswindow["-TABLE-"].update(visible=True)
                else:
                    self.addtswindow["-ADDMORE-"].update(visible=False)
                    self.addtswindow["-TABLE-"].update(visible=False)
            elif event == "-ADDMORE-":
                # addtspage.append(self.addtspage())  # вызвал сам себя
                # вызов нового окна, обработка его возращаемного значения и добавление в таблицу
                if values["-LEVEL-"] == "Изделие":
                    self.add_second_ts_page()
                else:
                    self.add_third_ts_page()

                print("debug master")

            elif event == sg.WIN_CLOSED or event == "-CloseAddTsPage-":
                self.addtswindow.close()
                return 0

    def get_ts_values(self):
        pass

    def add_second_ts_page(self):
        headings = ['Дог.', 'Акт', 'Наим.', 'Модель', 'S/N', 'Произв.', 'С1', 'С2', 'УФ', 'РГГ', 'РГГ пп', 'П', 'Сек',
                    'Кат.']
        second_data = [
            ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ],
        ]
        second_page = [
            [sg.Column(
                [[sg.Text('Договор'),
                  sg.InputText(key='-DOGOVOR-', default_text=self.dogovornumber, disabled=True, s=(5, 0),
                               text_color="black"),
                  sg.Text('Акт'), sg.InputText(key='-AKT-', default_text=self.actnumber, disabled=True, s=(5, 0),
                                               text_color="black")]]
                , justification="c"
            )],
            [sg.Column(
                [[sg.Text('Наименование ТС'), sg.InputCombo(["get from bd + kostil"], key='-TSNAME-', size=(45, 0)),
                  sg.Checkbox("Save", k="-TSSAVE-")],
                 # input + spisok. link model, vendor
                 [sg.Text('Модель'),
                  sg.InputCombo(["get from bd + kostil"], key='-MODEL-', size=(45, 0)),
                  sg.Checkbox("Save", k="-MODELSAVE-")],
                 # input, link tsname, vendor
                 [sg.Text('Заводской номер'), sg.InputText(key='-PARTNUMBER-')],  # mb add save button
                 [sg.Text('Производитель'), sg.InputCombo(["get from bd + kostil"], key='-VENDOR-', size=(45, 0)),
                  sg.Checkbox("Save", k="-VENDORSAVE-")],
                 # input + spisok. link tsname, model
                 [sg.Text('СЗЗ-1'), sg.InputText(key='-CZZ1-'), sg.Checkbox("Авто", k="-CZZAUTO-")],
                 # locked, checkbox + nextint
                 [sg.Text('СЗЗ-2'), sg.InputText(key='-CZZ2-')]]
                , justification="r", element_justification="r"
            )],  # locked + kol-vo objects in LEVEL
            [sg.Column(
                [[sg.Checkbox("УФ", key='-UF-'), sg.Text('РГГ'), sg.InputText(key='-RGG-', visible=False),
                  sg.FileBrowse(),
                  sg.Text('РГГ пп'), sg.InputText(key='-RGGPP-', s=(7, 0))]]
                , justification="c")],
            [sg.Column(
                [[sg.Text('Признак (уровень)'),
                  sg.Combo(["Элемент", "Составная часть"], readonly=True, enable_events=True,
                           key="-LEVEL-"), sg.Button("+", key="-ADDMORE-", visible=False, p=(15, 0), s=(4, 2))],
                 [sg.Text('Степень секретности'), sg.Combo(["С", "СС"], readonly=True, key='-SS-', s=(5, 0)),  # spisok
                  sg.Text('Категория помещения'), sg.Combo(["1", "2"], readonly=True, key='-KP-', s=(5, 0))]],
                justification="c", element_justification="c"
            )],
            [sg.Table(second_data, headings=headings, justification='l', key="-TABLE-", visible=False)],
            [sg.Text('Закрыть', key="-CloseAddTsPage-", enable_events=True, justification="left", expand_x=True),
             sg.Button("Сохранить"),
             sg.Submit('Обновить', size=(10, 0), k="-REFR-", button_color='gray', p=(20, 0)),
             sg.Button("Новое ТС"),
             ]
        ]
        second_ts_window = sg.Window('AddSecondTsPage', second_page, resizable=True, element_justification="").Finalize()
        while True:  # TSPage
            event, values = second_ts_window.read()
            # TSPage realisation
            if event == "-REFR-":
                print(values)
            elif event == "-LEVEL-":
                if values[event] == "Элемент":
                    second_ts_window["-ADDMORE-"].update(visible=True)
                    second_ts_window["-TABLE-"].update(visible=True)
                else:
                    second_ts_window["-ADDMORE-"].update(visible=False)
                    second_ts_window["-TABLE-"].update(visible=False)
            elif event == "-ADDMORE-":
                self.add_third_ts_page()
                print("debug window 2")

            elif event == sg.WIN_CLOSED or event == "-CloseAddTsPage-":
                second_ts_window.close()
                return 0

    def add_third_ts_page(self):
        headings = ['Дог.', 'Акт', 'Наим.', 'Модель', 'S/N', 'Произв.', 'С1', 'С2', 'УФ', 'РГГ', 'РГГ пп', 'П', 'Сек',
                    'Кат.']
        # third_data = [
        #     ['', '', '', '', '', '', '', '', '', '', '', '', '', '', ],
        # ]
        third_data = [
            [],
        ]
        third_page = [
            [sg.Column(
                [[sg.Text('Договор'),
                  sg.InputText(key='-DOGOVOR-', default_text=self.dogovornumber, disabled=True, s=(5, 0),
                               text_color="black"),
                  sg.Text('Акт'), sg.InputText(key='-AKT-', default_text=self.actnumber, disabled=True, s=(5, 0),
                                               text_color="black")]]
                , justification="c"
            )],
            [sg.Column(
                [[sg.Text('Наименование ТС'), sg.InputCombo(["get from bd + kostil"], key='-TSNAME-', size=(45, 0)),
                  sg.Checkbox("Save", k="-TSSAVE-")],
                 # input + spisok. link model, vendor
                 [sg.Text('Модель'),
                  sg.InputCombo(["get from bd + kostil"], key='-MODEL-', size=(45, 0)),
                  sg.Checkbox("Save", k="-MODELSAVE-")],
                 # input, link tsname, vendor
                 [sg.Text('Заводской номер'), sg.InputText(key='-PARTNUMBER-')],  # mb add save button
                 [sg.Text('Производитель'), sg.InputCombo(["get from bd + kostil"], key='-VENDOR-', size=(45, 0)),
                  sg.Checkbox("Save", k="-VENDORSAVE-")],
                 # input + spisok. link tsname, model
                 [sg.Text('СЗЗ-1'), sg.InputText(key='-CZZ1-'), sg.Checkbox("Авто", k="-CZZAUTO-")],
                 # locked, checkbox + nextint
                 [sg.Text('СЗЗ-2'), sg.InputText(key='-CZZ2-')]]
                , justification="r", element_justification="r"
            )],  # locked + kol-vo objects in LEVEL
            [sg.Column(
                [[sg.Checkbox("УФ", key='-UF-'), sg.Text('РГГ'), sg.InputText(key='-RGG-', visible=False),
                  sg.FileBrowse(),
                  sg.Text('РГГ пп'), sg.InputText(key='-RGGPP-', s=(7, 0))]]
                , justification="c")],
            [sg.Column(
                [[sg.Text('Признак (уровень)'),
                  sg.Combo(["Составная часть"], default_value="Составная часть", readonly=True, disabled=True,
                           enable_events=True, key="-LEVEL-")],
                 [sg.Text('Степень секретности'), sg.Combo(["С", "СС"], readonly=True, key='-SS-', s=(5, 0)),  # spisok
                  sg.Text('Категория помещения'), sg.Combo(["1", "2"], readonly=True, key='-KP-', s=(5, 0))]],
                justification="c", element_justification="c"
            )],
            [sg.Text('Закрыть', key="-CloseAddTsPage-", enable_events=True, justification="left", expand_x=True),
             sg.Button("Сохранить"),
             sg.Submit('Обновить', size=(10, 0), k="-REFR-", button_color='gray', p=(20, 0)),
             sg.Button("Новое ТС"),
             ]
        ]
        third_ts_window = sg.Window('AddThirdTsPage', third_page, resizable=True, element_justification="").Finalize()
        while True:  # TSPage
            event, values = third_ts_window.read()
            # TSPage realisation
            if event == "-REFR-":
                print(values)
            elif event == "-ADDMORE-":
                print("debug window 3")

            elif event == sg.WIN_CLOSED or event == "-CloseAddTsPage-":
                third_ts_window.close()
                return 0


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
                    # AddPage realisation
                    if event == "-AddTs-":
                        pages.addwindow.Hide()
                        if pages.credentialspage:  # if closed check + state check!!!!!
                            pages.tsstate = 0
                            pages.addtspage()
                            while True:
                                print("blya")
                                break

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

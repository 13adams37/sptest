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
            [sg.Text('Договор'), sg.InputText(key='-DOGOVOR-')],  # type + list
            [sg.Text('Акт'), sg.InputText(key='-AKT-')],  # type + list
            [sg.Button('Без номеров', size=(10, 0), button_color='gray', p=(20, 0)),
             sg.Submit('Дальше', size=(15, 0), button_color='green', p=(40, 0)),
             sg.Cancel('Отмена', button_color='red')]
        ]
        self.credentialswindow = sg.Window('DogovorPage', credentials, resizable=True,
                                           element_justification="right").Finalize()
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
            if event == "Без номеров":
                self.dogovornumber = "Null"
                self.actnumber = "Null"
                self.credentialswindow.close()
                return 1
            if event in ('Отмена', sg.WIN_CLOSED):
                self.credentialswindow.close()
                return 0

    def addtspage(self):
        addtspage = [
            [sg.Column(
                [[sg.Text('Договор'),
                  sg.InputText(key='-DOGOVOR-', default_text=self.dogovornumber, disabled=True, s=(5, 0)),
                  sg.Text('Акт'), sg.InputText(key='-AKT-', default_text=self.actnumber, disabled=True, s=(5, 0))]]

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
                  sg.Combo(["Изделие", "Элемент", "Составная часть"], readonly=True, key="-LEVEL-")],
                 [sg.Text('Степень секретности'), sg.Combo(["С", "СС"], readonly=True, key='-SS-', s=(5, 0)),  # spisok
                  sg.Text('Категория помещения'), sg.Combo(["1", "2"], readonly=True, key='-KP-', s=(5, 0))]],
                justification="c", element_justification="c"
            )],
            [sg.Text('Закрыть', key="-CloseAddTsPage-", enable_events=True, justification="left", expand_x=True),
             sg.Button("Сохранить"),
             sg.Submit('Обновить', size=(10, 0), button_color='gray', p=(20, 0)),
             sg.Button("Новое ТС"),
             ]
        ]
        self.addtswindow = sg.Window('AddTsPage', addtspage, resizable=True, element_justification="").Finalize()

        while True:  # TSPage
            event, values = self.addtswindow.read()
            # TSPage realisation

            if event == sg.WIN_CLOSED or event == "-CloseAddTsPage-":
                self.addtswindow.close()
                break


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
                        if pages.credentialspage:  # if closed check
                            pages.addtspage()

                        pages.addwindow.UnHide()
                        # pages.actnumber, pages.dogovornumber = None, None

                    if event == "-AddKomers-":
                        # Добавление огранизации
                        pass

                    if event == sg.WIN_CLOSED or event == "-CloseAddPage-":
                        pages.window.UnHide()
                        pages.addwindow.close()
                        break

            if event == sg.WIN_CLOSED:
                break
            # mainpage event, values
        pages.window.close()

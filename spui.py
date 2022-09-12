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
            [sg.Text('Добавление', key="-Add-", enable_events=True, justification="center", expand_x=True,
                     expand_y=True, auto_size_text=True, pad=(30, 30))],
            [sg.Text('Редактирование', key="-Edit-", enable_events=True, justification="center", expand_x=True,
                     expand_y=True, pad=(30, 30))]
        ]
        self.window = sg.Window('MainPage', mainpage, resizable=True).Finalize()

    def addaddpage(self):
        addpage = [
            [sg.Text('Добавить организацию', key="-AddKomers-", enable_events=True, justification="center",
                     expand_x=True,
                     expand_y=True,
                     pad=(30, 30))],
            [sg.Text('Добавить проверенное ТС', key="-AddTs-", enable_events=True, justification="center",
                     expand_x=True,
                     expand_y=True,
                     pad=(30, 30))],
            [sg.Text('Закрыть', key="-CloseAddPage-", enable_events=True, justification="center",
                     expand_x=True,
                     pad=(30, 30))]
        ]
        self.addwindow = sg.Window('AddPage', addpage, resizable=True).Finalize()

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
            [sg.Text('Договор'), sg.InputText(key='-DOGOVOR-', default_text=self.dogovornumber, disabled=True)],
            [sg.Text('Акт'), sg.InputText(key='-AKT-', default_text=self.actnumber, disabled=True)],
            [sg.Text('Наименование ТС'), sg.InputText(key='-TSNAME-')],  # input + spisok. link model, vendor
            [sg.Text('Модель'), sg.InputText(key='-MODEL-')],  # input, link tsname, vendor
            [sg.Text('Заводской номер'), sg.InputText(key='-PARTNUMBER-')],  # mb add save button
            [sg.Text('Производитель'), sg.InputText(key='-VENDOR-')],  # input + spisok. link tsname, model
            [sg.Text('СЗЗ-1'), sg.InputText(key='-CZZ1-')],  # locked, checkbox + nextint
            [sg.Text('СЗЗ-2'), sg.InputText(key='-CZZ2-')],  # locked + kol-vo objects in LEVEL
            [sg.Text('УФ'), sg.InputText(key='-UF-')],  # checkbox
            [sg.Text('РГГ'), sg.InputText(key='-RGG-')],
            [sg.Text('РГГ пп'), sg.InputText(key='-RGGPP-')],
            [sg.Text('Признак (уровень)'), sg.InputText(key='-LEVEL-')],
            [sg.Text('Степень секретности'), sg.InputText(key='-SS-')],  # spisok
            [sg.Text('Категорий помещения'), sg.InputText(key='-KP-')],  # spisok
            [sg.Text('Закрыть', key="-CloseAddTsPage-", enable_events=True, justification="left",
                     expand_x=True), sg.Submit('Обновить', size=(10, 0), button_color='gray', p=(20, 0))]
        ]
        self.addtswindow = sg.Window('AddTsPage', addtspage, resizable=True,
                                     element_justification="right").Finalize()

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

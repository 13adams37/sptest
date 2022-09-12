# from dearpygui import *
# may be later :(
import PySimpleGUI as sg


class Pages:
    def __init__(self):
        self.addtswindow = None
        self.addwindow = None

    def addaddpage(self):
        addpage = [
            [sg.Text('Добавить организацию', key="-AddKomers-", enable_events=True, justification="center",
                     expand_x=True,
                     expand_y=True)],
            [sg.Text('Добавить проверенное ТС', key="-AddTs-", enable_events=True, justification="center",
                     expand_x=True,
                     expand_y=True)],
            [sg.Text('Закрыть', key="-CloseAddPage-", enable_events=True, justification="center",
                     expand_x=True)]
        ]
        self.addwindow = sg.Window('AddPage', addpage, resizable=True).Finalize()

    def addtspage(self):
        addtspage = [
            [sg.Text('Договор'), sg.InputText(key='-DOGOVOR-')],
            [sg.Text('Акт'), sg.InputText(key='-AKT-')],
            [sg.Text('Наименование ТС'), sg.InputText(key='-TSNAME-')],
            [sg.Text('Модель'), sg.InputText(key='-MODEL-')],
            [sg.Text('Заводской номер'), sg.InputText(key='-PARTNUMBER-')],
            [sg.Text('Производитель'), sg.InputText(key='-VENDOR-')],
            [sg.Text('СЗЗ-1'), sg.InputText(key='-CZZ1-')],
            [sg.Text('СЗЗ-2'), sg.InputText(key='-CZZ2-')],
            [sg.Text('УФ'), sg.InputText(key='-UF-')],
            [sg.Text('РГГ'), sg.InputText(key='-RGG-')],
            [sg.Text('РГГ пп'), sg.InputText(key='-RGGPP-')],
            [sg.Text('Признак (уровень)'), sg.InputText(key='-LEVEL-')],
            [sg.Text('Степень секретности'), sg.InputText(key='-SS-')],
            [sg.Text('Категорий помещения'), sg.InputText(key='-KP-')],
            [sg.Text('Закрыть', key="-CloseAddTsPage-", enable_events=True, justification="center",
                     expand_x=True)]
        ]
        self.addtswindow = sg.Window('AddPage', addtspage, resizable=True,
                                     element_justification="right").Finalize()


class SpUi:

    def makeui(self):
        pages = Pages()
        sg.theme('DarkAmber')

        mainpage = [
            [sg.Text('Добавление', key="-Add-", enable_events=True, justification="center", expand_x=True,
                     expand_y=True)],
            [sg.Text('Редактирование', key="-Edit-", enable_events=True, justification="center", expand_x=True,
                     expand_y=True)]
        ]
        window = sg.Window('MainPage', mainpage, resizable=True).Finalize()

        while True:  # MainPage
            event, values = window.read()

            if event == "-Add-":
                window.Hide()
                pages.addaddpage()

                while True:  # Add Page
                    event, values = pages.addwindow.read()

                    if event == "-AddTs-":
                        pages.addwindow.Hide()
                        pages.addtspage()
                        while True:  # TSPage
                            event, values = pages.addtswindow.read()
                            # Реализация окна добавления ТС
                            if event == sg.WIN_CLOSED or event == "-CloseAddTsPage-":
                                pages.addwindow.UnHide()
                                pages.addtswindow.close()
                                break

                    if event == sg.WIN_CLOSED or event == "-CloseAddPage-":
                        window.UnHide()
                        pages.addwindow.close()
                        break

            if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
                break
            # event, values
        window.close()

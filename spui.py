# from dearpygui import *
# may be later :(
import PySimpleGUI as sg


class SpUi:
    mainpage = [
        [sg.Text('test0')],
        [sg.Text('org name'), sg.InputText()],
        [sg.Submit('Дальше', size=(10, 0), button_color='green'), sg.Cancel('Выход', button_color='red')]
    ]

    def makeui(self):
        sg.theme('DarkAmber')
        window = sg.Window('Window Title', self.mainpage)
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Выход':  # if user closes window or clicks cancel
                break
            print('You entered ', values[0])
        window.close()

import json
import re
import PySimpleGUI as sg
import pyperclip

import db
import MSWord
from copy import deepcopy

NULLLIST = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
headings = ['Объект', 'Наименование', 'Модель', 'Серийный номер', 'Производитель', 'СЗЗ 1', 'СЗЗ 2', 'Кол-во', 'УФ',
            'РГ', 'РГ пп', 'Признак', 'Состав']
table1, table2 = [], []
last_event = ""
fontbig = ("Arial", 24)
fontbutton = ("Helvetica", 20)
fontmid = ("Arial Baltic", 18)
fontmidlow = ("Arial Baltic", 16)
char_width = sg.Text.char_width_in_pixels(fontmidlow)

baza = db.DataBase()
tdb = db.db


def _onKeyRelease(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")

    if event.keycode == 65 and ctrl and event.keysym.lower() != "a":
        event.widget.event_generate("<<SelectAll>>")

    # if event.keycode == 83 and ctrl and event.keysym.lower() != "s":
    if event.keycode == 83 and ctrl:  # ctrl + s, save
        event.widget.event_generate("<<MySave>>")

    if event.keycode == 78 and ctrl:  # ctrl + n, clear
        event.widget.event_generate("<<MyClear>>")


def popup_yes_no(main_text='Заглушка'):
    layout = [[
        sg.Column([
            [sg.T("         ")],
            [sg.T(f"{main_text}", font=fontbig)],
        ], justification="c", element_justification="c")
    ], [
        sg.Column([
            [sg.Cancel('Да', font=fontbutton, s=(15, 0)),
             sg.Submit("Нет", font=fontbutton, s=(15, 0))],
        ], justification="c", element_justification="c")
    ]]
    popupwin = sg.Window('Подтверждение', layout, resizable=False, return_keyboard_events=True,
                         keep_on_top=True).Finalize()

    while True:
        event, values = popupwin.read()

        if event == sg.WIN_CLOSED:
            popupwin.close()
            return 0

        elif event.startswith("\r") or event == 'Да':
            popupwin.close()
            return 1

        elif event.startswith("Escape") or event == 'Нет':
            popupwin.close()
            return 0


def popup_input_text(main_text='Заглушка'):
    layout = [[
        sg.Column([
            [sg.T("         ")],
            [sg.T(f"{main_text}", font=fontbig)],
        ], justification="c", element_justification="c")
    ], [
        sg.Column([
            [sg.Input(size=(25, 0), font=fontbig, k="-IN-"),
             ],
        ], justification="c", element_justification="c")
    ],
        [
            sg.Column([
                [sg.Button('Подтвердить', font=fontbutton, s=(15, 0)),
                 sg.Button("Отмена", font=fontbutton, s=(15, 0))
                 ],
            ], justification="c", element_justification="c")
        ]
    ]
    popupwin = sg.Window('Подтверждение', layout, resizable=False, return_keyboard_events=True).Finalize()
    popupwin['-IN-'].SetFocus(True)
    if "<Key>" not in popupwin.TKroot.bind_all():
        popupwin.TKroot.bind_all("<Key>", _onKeyRelease, "+")

    while True:
        event, values = popupwin.read()

        if event == sg.WIN_CLOSED:
            popupwin.close()
            return None

        elif (event.startswith("\r") or event == 'Подтвердить') and values["-IN-"]:
            popupwin.close()
            return values["-IN-"]

        elif event.startswith("Escape") or event == 'Отмена':
            popupwin.close()
            return None


def real_popup_input_text_with_hints(headername, middle_text="",
                                     index_name='objects'):
    def myFunc(e):
        return e[1]

    input_width = 80
    num_items_to_show = 18

    settings_query = baza.get_by_id("1337")

    choices = baza.get_unique_index_names(f"{index_name}")
    choices.sort(key=myFunc)

    hintedinputlayout = [
        [
            sg.Column([
                [sg.T("         ")],
                [sg.T(f"{middle_text}", font=fontbig)],
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
            sg.Button('Выбрать', key="-SELECT-", font=fontbutton),
        ]
    ]

    hintedinputwindow = sg.Window(headername, hintedinputlayout, resizable=True, return_keyboard_events=True,
                                  element_justification="").Finalize()
    hintedinputwindow.Maximize()
    if "<Key>" not in hintedinputwindow.TKroot.bind_all():
        hintedinputwindow.TKroot.bind_all("<Key>", _onKeyRelease, "+")

    list_element: sg.Listbox = hintedinputwindow.Element('-BOX-')
    prediction_list, prediction_ids, input_text, sel_item = [], [], "", 0

    while True:
        event, values = hintedinputwindow.read()

        if event == "-SELECT-" and values["-IN-"]:
            if baza.search_if_exists("$.object", values['-IN-']):
                hintedinputwindow.close()
                return values['-IN-']

        elif event == "-CLOSE-" or event == sg.WIN_CLOSED:
            hintedinputwindow.close()
            return None

        elif event.startswith('Escape'):
            hintedinputwindow['-IN-'].update('')

        elif event.startswith('Down') and len(prediction_list):
            sel_item = (sel_item + 1) % len(prediction_list)
            list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

        elif event.startswith('Up') and len(prediction_list):
            sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
            list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

        elif event == '\r':
            if len(values['-BOX-']) > 0:
                hintedinputwindow['-IN-'].update(value=values['-BOX-'][0])
            try:
                if values['-BOX-'][0] == values['-IN-']:
                    hintedinputwindow.close()
                    return values['-IN-']
            except IndexError:
                continue
                # hintedinputwindow.close()
                # return values['-IN-']

        elif event == '-IN-':
            text = values['-IN-'].lower()
            if text == input_text:
                continue
            else:
                input_text = text
            prediction_list = []
            if text:
                cnt = 0
                if settings_query['search']:
                    for item in choices:
                        if item.lower().__contains__(text):
                            prediction_list.append(item)
                            cnt += 1
                            if cnt == int(settings_query['max_len']):
                                break
                else:
                    for item in choices:
                        if item.lower().startswith(text):
                            prediction_list.append(item)
                            cnt += 1
                            if cnt == int(settings_query['max_len']):
                                break

            list_element.update(values=prediction_list)
            sel_item = 0
            list_element.update(set_to_index=sel_item)

        elif event == '-BOX-' and values['-BOX-']:
            hintedinputwindow['-IN-'].update(value=values['-BOX-'][0])

    hintedinputwindow.close()


def popup_input_text_with_hints(headername, middle_text="Удаление и изменение",
                                index_name='objects'):  # delete and edit page
    def myFunc(e):
        return e[1]

    input_width = 80
    num_items_to_show = 18

    settings_query = baza.get_by_id("1337")

    choices = baza.get_unique_index_names(f"{index_name}")
    choices.sort(key=myFunc)

    hintedinputlayout = [
        [
            sg.Column([
                [sg.T("         ")],
                [sg.T(f"{middle_text}", font=fontbig)],
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
            sg.Button('Удалить', key="-DELETE-", font=fontbutton),
            sg.Button("Переименовать", key="-RENAME-", font=fontbutton),
        ]
    ]

    hintedinputwindow = sg.Window(headername, hintedinputlayout, resizable=True, return_keyboard_events=True,
                                  element_justification="").Finalize()
    hintedinputwindow.Maximize()
    if "<Key>" not in hintedinputwindow.TKroot.bind_all():
        hintedinputwindow.TKroot.bind_all("<Key>", _onKeyRelease, "+")

    list_element: sg.Listbox = hintedinputwindow.Element('-BOX-')
    prediction_list, prediction_ids, input_text, sel_item = [], [], "", 0

    while True:
        event, values = hintedinputwindow.read()

        if event == "-DELETE-" and values["-IN-"]:
            if baza.search_if_exists("$.object", values['-IN-']):
                if popup_yes_no(f'Вы действительно хотите удалить "{values["-IN-"]}"?'):
                    for item in baza.search('$.object', f'{values["-IN-"]}'):
                        baza.delete_by_id(item[0])

                    choices = baza.get_unique_index_names(f"{index_name}")
                    choices.sort(key=myFunc)
                    prediction_list.clear()
                    cnt = 0
                    text = values['-IN-'].lower()
                    if settings_query['search']:
                        for item in choices:
                            if item.lower().__contains__(text):
                                prediction_list.append(item)
                                cnt += 1
                                if cnt == int(settings_query['max_len']):
                                    break
                    else:
                        for item in choices:
                            if item.lower().startswith(text):
                                prediction_list.append(item)
                                cnt += 1
                                if cnt == int(settings_query['max_len']):
                                    break

                    list_element.update(values=prediction_list)
                    sel_item = 0
                    list_element.update(set_to_index=sel_item)

        elif event == "-RENAME-" and values["-IN-"]:
            if baza.search_if_exists("$.object", values['-IN-']):
                popup_text = popup_input_text("Введите новое название")
                if popup_text is not None:
                    for item in baza.search('$.object', f'{values["-IN-"]}'):
                        obj = item[1].copy()
                        obj['object'] = popup_text
                        if obj['table']:
                            for item1 in obj['table']:
                                item1['object'] = popup_text
                                if item1['table']:
                                    for item2 in item1['table']:
                                        item2['object'] = popup_text
                        baza.update_element_dict(item[0], obj)

                    choices = baza.get_unique_index_names(f"{index_name}")
                    choices.sort(key=myFunc)
                    prediction_list.clear()
                    cnt = 0
                    text = popup_text
                    hintedinputwindow['-IN-'].update(popup_text)
                    if settings_query['search']:
                        for item in choices:
                            if item.lower().__contains__(text):
                                prediction_list.append(item)
                                cnt += 1
                                if cnt == int(settings_query['max_len']):
                                    break
                    else:
                        for item in choices:
                            if item.lower().startswith(text):
                                prediction_list.append(item)
                                cnt += 1
                                if cnt == int(settings_query['max_len']):
                                    break
                    list_element.update(values=prediction_list)
                    sel_item = 0
                    list_element.update(set_to_index=sel_item)

        elif event == "-CLOSE-" or event == sg.WIN_CLOSED:
            hintedinputwindow.close()
            break

        elif event.startswith('Escape'):
            hintedinputwindow['-IN-'].update('')

        elif event.startswith('Down') and len(prediction_list):
            sel_item = (sel_item + 1) % len(prediction_list)
            list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

        elif event.startswith('Up') and len(prediction_list):
            sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
            list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

        elif event == '\r':
            if len(values['-BOX-']) > 0:
                hintedinputwindow['-IN-'].update(value=values['-BOX-'][0])

        elif event == '-IN-':
            text = values['-IN-'].lower()
            if text == input_text:
                continue
            else:
                input_text = text
            prediction_list = []
            if text:
                cnt = 0
                if settings_query['search']:
                    for item in choices:
                        if item.lower().__contains__(text):
                            prediction_list.append(item)
                            cnt += 1
                            if cnt == int(settings_query['max_len']):
                                break
                else:
                    for item in choices:
                        if item.lower().startswith(text):
                            prediction_list.append(item)
                            cnt += 1
                            if cnt == int(settings_query['max_len']):
                                break

            list_element.update(values=prediction_list)
            sel_item = 0
            list_element.update(set_to_index=sel_item)

        elif event == '-BOX-' and values['-BOX-']:
            hintedinputwindow['-IN-'].update(value=values['-BOX-'][0])

    hintedinputwindow.close()


# def super_predictor(index_type, index_name, text):  # later
#     #  index_type - uniquenames, uniqueidnames, names
#     def myFunc(e):
#         return e[1]
#
#     settings_query = baza.get_by_id("1337")
#
#     if index_type == "unique_names":
#         choices = baza.get_unique_index_names(f"{index_name}")
#     elif index_type == "unique_idnames":
#         choices = baza.get_unique_index_idnames(f"{index_name}")
#     else:
#         choices = baza.get_index_names(f"{index_name}")
#
#     choices.sort(key=myFunc)
#
#     prediction_list = []
#     cnt = 0
#     if index_type == "unique_names" or "names":  # only names
#         if settings_query['search']:
#             for item in choices:
#                 if item.lower().__contains__(text):
#                     prediction_list.append(item)
#                     cnt += 1
#                     if cnt == int(settings_query['max_len']):
#                         break
#         else:
#             for item in choices:
#                 if item.lower().startswith(text):
#                     prediction_list.append(item)
#                     cnt += 1
#                     if cnt == int(settings_query['max_len']):
#                         break
#         return prediction_list
#     else:  # id, names
#         if settings_query['search']:
#             for item in choices:
#                 if item.lower().__contains__(text):
#                     prediction_list.append(item)
#                     cnt += 1
#                     if cnt == int(settings_query['max_len']):
#                         break
#         else:
#             for item in choices:
#                 if item.lower().startswith(text):
#                     prediction_list.append(item)
#                     cnt += 1
#                     if cnt == int(settings_query['max_len']):
#                         break
#         return prediction_list


def replace_bool(input_data):
    output_data = deepcopy(input_data)
    for i in output_data:
        i[8] = str(i[8])
    return output_data


def count_char_length(input_data):
    total = 0
    for k in input_data:  # [[]] to []
        if k[12]:
            temp = 0
            for i in k[12]:  # [[]] to []
                i[8] = str(i[8])
                for word in i:
                    temp += len(word)
            if temp >= total:
                total = temp
    if total * char_width <= 240:
        return 240
    return total * char_width


def table_list_simplify(data):
    simple_data = []
    for item in data:
        simple_data.append(str(item[1]))
        simple_data.append(str(item[2]))
        simple_data.append(str(item[3]))
        simple_data.append(str(item[4]))
        simple_data.append(" | ")
        for item1 in item[12]:
            simple_data.append(str(item1[1]))
            simple_data.append(str(item1[2]))
            simple_data.append(str(item1[3]))
            simple_data.append(str(item1[4]))
            simple_data.append(" | ")
    return simple_data


class Pages:
    def __init__(self):
        self.settingswindow = None
        self.window = None
        self.addtswindow = None
        self.addwindow = None
        self.credentialswindow = None
        self.viewwindow = None
        self.addkomerswindow = None
        self.edittswidow = None
        self.exportwordwindow = None
        self.importwindow = None
        self.seqwindow = None
        self.conclusionwindow = None

        self.object = None
        self.tsdata = []
        self.tsavailable = ["Комплект", "Составная часть", "Элемент"]
        self.choices_name, self.choices_model, self.choices_part, self.choices_vendor, self.predictions_list = [], [], [], [], []
        self.input_text, self.last_event = '', ''

        # settings
        settings_query = baza.get_by_id("1337")
        self.search_type = settings_query['search']
        self.hints_type = settings_query['hints']
        self.jump_type = settings_query['jump']
        self.prediction_len = int(settings_query['max_len'])

    def mainpage(self):
        mainpage = [
            [sg.Column(
                [[sg.Button('Добавление ТС', key="-Add-", enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            pad=(30, 30),
                            s=(30, 5),
                            button_color=(sg.theme_text_color(), sg.theme_background_color()),
                            border_width=0,
                            font=fontbig,
                            ),
                  sg.Button('Редактирование и просмотр ТС', key="-Edit-", enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            pad=(30, 30),
                            s=(30, 5),
                            button_color=(sg.theme_text_color(), sg.theme_background_color()),
                            border_width=0,
                            font=fontbig
                            )], ], )],
            [sg.Column(
                [[sg.Button('Импорт и экспорт базы', key="-Import-", enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            pad=(30, 30),
                            s=(30, 5),
                            button_color=(sg.theme_text_color(), sg.theme_background_color()),
                            border_width=0,
                            font=fontbig
                            ),
                  sg.Button('Экспорт в Word', key="-Export-", enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            pad=(30, 30),
                            s=(30, 5),
                            button_color=(sg.theme_text_color(), sg.theme_background_color()),
                            border_width=0,
                            font=fontbig
                            )], ], justification='c')],
            [sg.Column(
                [[sg.Button('Дополнительно', key="-Extra-", enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            pad=(30, 30),
                            s=(30, 5),
                            button_color=(sg.theme_text_color(), sg.theme_background_color()),
                            border_width=0,
                            font=fontbig
                            ),
                  sg.Button('Настройки', key="-Settings-", enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            pad=(30, 30),
                            s=(30, 5),
                            button_color=(sg.theme_text_color(), sg.theme_background_color()),
                            border_width=0,
                            font=fontbig
                            ),
                  ], ], justification='c')]
        ]
        self.window = sg.Window('Главное меню', mainpage, resizable=True).Finalize()

    def settingspage(self):
        temp_settings_query = baza.get_by_id("1337")
        settingslayout = [
            [
                sg.Text('Поиск: ', font=fontbig),
                sg.DropDown(values=['По содержанию', 'С начала'],
                            default_value="По содержанию" if temp_settings_query['search'] else "С начала",
                            font=fontmid, key='search',
                            readonly=True)
            ],
            [
                sg.Text('Подсказки при вводе (Добавление ТС): ', font=fontbig),
                sg.DropDown(values=['Вкл', 'Выкл'], default_value="Вкл" if temp_settings_query['hints'] else "Выкл",
                            font=fontmid, key='hints', readonly=True)
            ],
            [
                sg.Text('Переход к новому полю через Enter (Добавление ТС): ', font=fontbig),
                sg.DropDown(values=['Вкл', 'Выкл'], default_value="Вкл" if temp_settings_query['jump'] else "Выкл",
                            font=fontmid, key='jump', readonly=True)
            ],
            [
                sg.Text('Максимальное количество вывода элементов (0 - все) ', font=fontbig),
                sg.InputText(default_text=int(temp_settings_query['max_len']), font=fontmid, key='max_len', s=(8, 0))
            ],
            [
                sg.Text('Назад', key="-CLOSE-", enable_events=True, justification="l", expand_x=True,
                        font=fontbutton)
            ]
        ]
        self.settingswindow = sg.Window('Настройки', settingslayout, resizable=True, return_keyboard_events=True,
                                        element_justification="c").Finalize()
        self.settingswindow['search'].SetFocus(True)

        while True:
            event, values = self.settingswindow.read()

            if event == sg.WIN_CLOSED:
                self.settingswindow.close()
                break

            elif event == "-CLOSE-" or event.startswith('Escape'):
                text = values['max_len']
                if text == '':
                    self.settingswindow['max_len'].Update(baza.get_by_id(1337)['max_len'])
                    continue
                else:
                    try:
                        value = int(text)
                    except ValueError:  # oops
                        self.settingswindow['max_len'].Update(baza.get_by_id(1337)['max_len'])
                        continue

                temp_settings = {'search': True if values['search'] == 'По содержанию' else False,
                                 'hints': True if values['hints'] == 'Вкл' else False,
                                 'jump': True if values['jump'] == 'Вкл' else False,
                                 'max_len': values['max_len']}

                baza.update_element_dict('1337', temp_settings)
                self.hints_type = temp_settings['hints']
                self.jump_type = temp_settings['jump']
                self.search_type = temp_settings['search']
                self.prediction_len = int(temp_settings['max_len'])
                self.settingswindow.close()
                break

    @property
    def credentialspage(self):
        choices = baza.get_unique_index_names("objects")

        credentialslayout = [
            [sg.Text('Объект', font=fontbig)],
            [sg.Input(key='-OBJECT-', font=fontbig, enable_events=True, s=(25, 0))],
            [sg.pin(sg.Col(
                [[sg.Listbox(values=[], size=(80, 4), enable_events=True, key='-BOX-',
                             select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                key='-BOX-CONTAINER-', pad=(0, 0), visible=True if self.hints_type else False))],
            [sg.Button('Дальше', size=(15, 0), button_color='green', font=fontbutton),
             sg.Cancel('Отмена', button_color='red', font=fontbutton)]
        ]
        self.credentialswindow = sg.Window('Выбор объекта', credentialslayout, resizable=True,
                                           return_keyboard_events=True, element_justification="c")
        self.credentialswindow.Finalize()
        self.credentialswindow['-OBJECT-'].SetFocus(True)

        if "<Key>" not in self.credentialswindow.TKroot.bind_all():
            self.credentialswindow.TKroot.bind_all("<Key>", _onKeyRelease, "+")

        list_element: sg.Listbox = self.credentialswindow.Element('-BOX-')
        list_element.TKListbox.configure(activestyle='none')
        prediction_list, prediction_ids, input_text, sel_item = [], [], "", 0

        while True:
            event, values = self.credentialswindow.read()

            if event in ('Отмена', sg.WIN_CLOSED):
                self.credentialswindow.close()
                return 0

            elif event == "Дальше" and values["-OBJECT-"]:
                self.object = values["-OBJECT-"]
                self.credentialswindow['-OBJECT-'].update('')
                self.credentialswindow.close()
                return 1

            elif event.startswith('Escape'):
                self.credentialswindow['-OBJECT-'].update('')

            elif event.startswith('Down') and len(prediction_list):
                sel_item = (sel_item + 1) % len(prediction_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event.startswith('Up') and len(prediction_list):
                sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event == '\r' and values["-OBJECT-"]:
                if len(values['-BOX-']) > 0:
                    self.credentialswindow['-OBJECT-'].update(value=values['-BOX-'][0])

                try:
                    if values['-BOX-'][0] == values['-OBJECT-']:
                        self.credentialswindow['-OBJECT-'].update(value=values['-BOX-'][0])
                        self.object = values['-OBJECT-']
                        self.credentialswindow.close()
                        return 1
                except IndexError:
                    self.object = values["-OBJECT-"]
                    self.credentialswindow['-OBJECT-'].update('')
                    self.credentialswindow.close()
                    return 1

            elif event == '-OBJECT-':
                text = values['-OBJECT-'].lower()
                if text == input_text:
                    continue
                else:
                    input_text = text
                prediction_list = []
                if text and self.hints_type:
                    cnt = 0
                    if self.search_type:
                        for item in choices:
                            if item.lower().__contains__(text):
                                prediction_list.append(item)
                                cnt += 1
                                if cnt == self.prediction_len:
                                    break
                    else:
                        for item in choices:
                            if item.lower().startswith(text):
                                prediction_list.append(item)
                                cnt += 1
                                if cnt == self.prediction_len:
                                    break

                list_element.update(values=prediction_list)
                sel_item = 0
                list_element.update(set_to_index=sel_item)

            elif event == '-BOX-' and values['-BOX-']:
                # fix
                self.credentialswindow['-OBJECT-'].update(value=values['-BOX-'][0])

    def addtspage(self, master, headername, ts_id=(None, None)):
        global table1, table2
        window_saved = False
        sel_item = 0
        col_widths = list(map(lambda x: len(x) + 2, headings))
        tabledata = []
        event_list = ['name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'amount', 'rgg', 'rggpp']
        addtspage = [
            [sg.Column(
                [[sg.Text('Объект', font=fontmid), sg.InputText(key='object', default_text=self.object, disabled=True,
                                                                s=(int(len(self.object) * 1.2), 5), text_color="black",
                                                                font=fontmidlow, justification='c')]]
                , justification="c"
            )],
            [sg.Column(
                [[sg.Text('Наименование ТС', font=fontmid),
                  sg.Input(key='name', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="nameSAVE", font=fontmid)],

                 [sg.pin(sg.Col(
                     [[sg.Listbox(values=[], size=(35, 4), enable_events=True, key='-BOXname-',
                                  select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                     key='-CONTAINERname-', pad=(105, 0), visible=False))],

                 [sg.Text('Модель', font=fontmid),
                  sg.Input(key='model', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="modelSAVE", font=fontmid)],

                 [sg.pin(sg.Col(
                     [[sg.Listbox(values=[], size=(35, 4), enable_events=True, key='-BOXmodel-',
                                  select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                     key='-CONTAINERmodel-', pad=(105, 0), visible=False, justification='c'))],

                 [sg.Text('Заводской номер', font=fontmid),
                  sg.Input(key='part', enable_events=True, font=fontmid, s=(39, 0)),
                  sg.Checkbox("б/н", k="nopart", enable_events=True, font=fontmid),
                  sg.Checkbox("Сохр.", k="partSAVE", font=fontmid)],

                 [sg.pin(sg.Col(
                     [[sg.Listbox(values=[], size=(35, 4), enable_events=True, key='-BOXpart-',
                                  select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                     key='-CONTAINERpart-', pad=(105, 0), visible=False, justification='c'))],

                 [sg.Text('Производитель', font=fontmid),
                  sg.Input(key='vendor', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="vendorSAVE", font=fontmid)],

                 [sg.pin(sg.Col(
                     [[sg.Listbox(values=[], size=(35, 4), enable_events=True, key='-BOXvendor-',
                                  select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                     key='-CONTAINERvendor-', pad=(105, 0), visible=False, justification='c'))],

                 [sg.Text('СЗЗ-1', font=fontmid), sg.InputText(key='serial1', font=fontmid, s=(15, 0)),
                  sg.Checkbox("Сохр.", k="serial1SAVE", font=fontmid)],
                 [sg.Text('СЗЗ-2', font=fontmid), sg.InputText(key='serial2', s=(3, 0), font=fontmid),
                  sg.Text('Кол-во', font=fontmid), sg.InputText(default_text="1", key='amount', font=fontmid, s=(3, 0))]
                 ]
                , justification="c", element_justification="r"
            )],
            [sg.Column(
                [[sg.Checkbox("УФ", font=fontmid, key='uv'),
                  sg.Text('РГ', font=fontmid),
                  sg.Input(k='rgg', enable_events=True, font=fontmid, s=(10, 0)),
                  sg.Checkbox("Сохр.", k="rggSAVE", font=fontmid),
                  sg.Text('РГ пп', font=fontmid), sg.InputText(key='rggpp', s=(5, 0), font=fontmid)]]
                , justification="c")],
            [sg.Column(
                [[sg.Text('Признак (уровень)', font=fontmid),
                  sg.Combo(self.tsavailable, readonly=True, enable_events=True, key="level",
                           default_value=self.tsavailable[0], font=fontmidlow),
                  sg.Button("+", key="-ADDMORE-", visible=False, p=(15, 0), s=(3, 1), font=fontmid)],
                 ],
                justification="c", element_justification="c"
            )],
            [sg.Table(
                values=tabledata,
                headings=headings,
                auto_size_columns=False,
                vertical_scroll_only=False,
                hide_vertical_scroll=False,
                right_click_menu=['&Right', ['Редактировать', 'Удалить']],
                col_widths=col_widths,
                font=fontmidlow,
                justification='c',
                key='-TABLE-'), ],
            [sg.Text('Назад', key="-CloseAddTsPage-", enable_events=True, justification="l", expand_x=True,
                     font=fontbutton),
             sg.Button("Копировать", k="-COPY-", font=fontbutton),
             sg.Button("Вставить", k="-PASTE-", font=fontbutton),
             sg.Button("Удалить из БД", k="bd_delete", font=fontbutton, visible=False),
             sg.Button("Сохранить", k="_SAVE_", font=fontbutton),
             sg.Button("Очистить", font=fontbutton),
             ]
        ]
        self.addtswindow = sg.Window(headername, addtspage, resizable=True, return_keyboard_events=True,
                                     element_justification="").Finalize()
        self.addtswindow.Maximize()
        self.addtswindow['name'].SetFocus(True)
        self.get_choices()

        if "<Key>" not in self.addtswindow.TKroot.bind_all():
            self.addtswindow.TKroot.bind_all("<Key>", _onKeyRelease, "+")
        self.addtswindow.bind("<<MySave>>", "_SAVE_")
        self.addtswindow.bind("<<MyClear>>", "Очистить")

        table = self.addtswindow['-TABLE-']
        table_widget = table.Widget

        displaycolumns = deepcopy(headings)
        displaycolumns.remove('Объект')
        table.ColumnsToDisplay = displaycolumns
        table_widget.configure(displaycolumns=displaycolumns)

        table.expand(expand_x=True, expand_y=True)
        for cid in headings:
            table_widget.column(cid, stretch=True)

        if self.tsavailable == ["Элемент"]:
            self.addtswindow['level'].update()

        if "Комплект" in self.tsavailable or "Составная часть" in self.tsavailable:
            self.addtswindow["-ADDMORE-"].update(visible=True)
            self.addtswindow["-TABLE-"].update(visible=True)
        else:
            self.addtswindow["-ADDMORE-"].update(visible=False)
            self.addtswindow["-TABLE-"].update(visible=False)

        # fucking slaves get your ass back here
        if master == "slave":
            self.fun_slave()
            if self.tsdata[3] == 'б/н':
                self.addtswindow["part"].update("б/н", disabled=True)
                self.addtswindow['nopart'].update(True)

        if master == "editor":
            self.fun_vieweditor()
            if ts_id != (None, None):
                if ts_id[1] == 0:
                    self.addtswindow['-CloseAddTsPage-'].Update('Выход')
                    self.addtswindow['_SAVE_'].Update('Сохранить в БД')
                    self.addtswindow["bd_delete"].Update(visible=True)
            if self.tsavailable == ["Комплект", "Составная часть", "Элемент"]:
                table1 = self.tsdata[12]
            if self.tsavailable == ["Составная часть", "Элемент"]:
                table2 = self.tsdata[12]
            self.last_event = "name"
            self.resize_and_update_table(self.tsdata[12])
            if self.tsdata[3] == 'б/н':
                self.addtswindow["part"].update("б/н", disabled=True)
                self.addtswindow['nopart'].update(True)

        if master == True:
            self.addtswindow['_SAVE_'].Update('Добавить в БД')
            self.addtswindow['-CloseAddTsPage-'].Update('Выход')

        def make_predictions(index, container):
            choices = eval(f"self.choices_{index}")
            text = values[index].lower()
            if text == self.input_text:
                pass
            else:
                self.input_text = text
                self.predictions_list = []
                if text:
                    cnt = 0
                    if self.search_type:
                        for itm in choices:
                            if itm.lower().__contains__(text):
                                self.predictions_list.append(itm)
                                cnt += 1
                                if cnt == self.prediction_len:
                                    break
                    else:
                        for itm in choices:
                            if itm.lower().startswith(text):
                                self.predictions_list.append(itm)
                                cnt += 1
                                if cnt == self.prediction_len:
                                    break

                if len(self.predictions_list) == 1:
                    if text == self.predictions_list[0].lower():
                        self.predictions_list = []

                list_element.update(values=self.predictions_list)
                sel_item = 0
                list_element.update(set_to_index=sel_item)

                if len(self.predictions_list) > 0:
                    self.addtswindow[container].update(visible=True)
                else:
                    self.addtswindow[container].update(visible=False)
                    self.addtswindow[f'-BOX{index}-'].update('')

        while True:
            event, values = self.addtswindow.read()

            if event == sg.WIN_CLOSED or event == "-CloseAddTsPage-" or event.startswith('Escape'):
                try:
                    if event.startswith('Escape'):
                        get_focused_elementname = self.addtswindow.find_element_with_focus().Key

                        if get_focused_elementname in ['name', 'model', 'part', 'vendor']:
                            container = self.addtswindow[f'-CONTAINER{get_focused_elementname}-']
                        else:
                            container = None

                        if container and container.visible:
                            container.update('')
                            container.update(visible=False)
                            self.addtswindow[f'-BOX{get_focused_elementname}-'].update('')
                            continue

                except AttributeError:
                    pass

                if self.tsavailable == ["Комплект", "Составная часть", "Элемент"] and not master:
                    table1.clear()
                elif self.tsavailable == ["Составная часть", "Элемент"] and not master:
                    table2.clear()
                if not window_saved and event is not sg.WIN_CLOSED:
                    if not popup_yes_no('Уверены что хотите выйти без сохранения?'):
                        continue
                self.addtswindow.close()
                break

            elif event.startswith('Down') and len(self.predictions_list):
                sel_item = (sel_item + 1) % len(self.predictions_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event.startswith('Up') and len(self.predictions_list):
                sel_item = (sel_item + (len(self.predictions_list) - 1)) % len(self.predictions_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event == '-COPY-':
                pyperclip.copy(json.dumps(
                    {'sp': baza.makejson(self.get_tsvalues(values))}
                ))

            elif event == '-PASTE-':
                def cut_dict_by_depth(d, max_depth):
                    if popup_yes_no(f'Содержимое для вставки не помещается полностью.\n'
                                    f'Вставить удалив непомещающиеся элементы?'):
                        current_depth = 1
                        if current_depth == max_depth:
                            d['table'] = []
                        else:
                            if d['table']:
                                for cnt, it3m in enumerate(d['table']):
                                    current_depth = 2
                                    if current_depth == max_depth:
                                        it3m['table'] = []
                        return True
                    else:
                        return False

                def get_max_depth(data):
                    max_depth = 0
                    if isinstance(data, dict):
                        max_depth = 1
                        if data['table']:
                            max_depth = 2 if max_depth <= 1 else max_depth  # first table is 2 depth
                            for data1 in data['table']:
                                if data1['table']:
                                    max_depth = 3 if max_depth <= 2 else max_depth
                    return max_depth

                def rename_element(temp_content):
                    if temp_content['table']:
                        for item in temp_content['table']:
                            item['object'] = object_name
                            if current_level == 'Комплект':
                                item['level'] = 'Составная часть'
                            elif current_level == 'Составная часть':
                                item['level'] = 'Элемент'
                            else:
                                print('RENAME EXCEPTION')

                            if item['table']:
                                for item1 in item['table']:
                                    item1['object'] = object_name
                                    item1['level'] = 'Элемент'

                def get_current_max_depth():
                    if current_level == 'Комплект':
                        return 3
                    elif current_level == 'Составная часть':
                        return 2
                    elif current_level == 'Элемент':
                        return 1
                    else:
                        print('MAX DEPTH IS NOT DEFINED')

                def add_content_to_table():
                    temp_content = deepcopy(pasted_content)
                    temp_table = self.dict_2_list(temp_content)[12]
                    if current_max_depth == 3:
                        for item in temp_table:
                            table1.append(item)
                    elif current_max_depth == 2:
                        # table ?
                        for item in temp_table:
                            table2.append(item)
                    else:
                        print('ADD TO TABLE FAILURE')

                pasted_content = {}
                try:
                    pasted_content = json.loads(pyperclip.paste())['sp']
                except (TypeError, ValueError):
                    sg.popup_no_frame(f'Ошибка вставки!'
                                      f'\nВставленный элемент не относится к программе.',
                                      auto_close_duration=1, auto_close=True, font=fontbig)
                    continue

                current_level, object_name = values['level'], values['object']
                pasted_content['object'] = object_name
                pasted_content['level'] = current_level

                content_max_depth = get_max_depth(pasted_content)
                current_max_depth = get_current_max_depth()

                if content_max_depth > current_max_depth:
                    if not cut_dict_by_depth(pasted_content, current_max_depth):
                        continue

                # raname
                rename_element(pasted_content)

                self.resize_and_update_table(self.dict_2_list(deepcopy(pasted_content))[12])
                add_content_to_table()
                pasted_content.pop('table')

                for name, val in pasted_content.items():
                    self.addtswindow[name].update(val)

            elif event == '\r':
                if self.last_event:
                    if len(values[f'-BOX{self.last_event}-']) > 0:
                        self.addtswindow[self.last_event].update(value=values[f'-BOX{self.last_event}-'][0])
                        self.addtswindow[f'-CONTAINER{self.last_event}-'].update(visible=False)
                        self.addtswindow[f'-BOX{self.last_event}-'].update('')
                        continue

                if self.jump_type:
                    try:
                        get_focused_elementname = self.addtswindow.find_element_with_focus().Key
                        next_element = event_list[0 if get_focused_elementname == 'rggpp' else event_list.index(
                            get_focused_elementname) + 1]
                        self.addtswindow[next_element].set_focus()
                        self.addtswindow[next_element].Widget.icursor('end')

                    except AttributeError:
                        print('AttError')
                        pass
                    except ValueError:
                        print('ValError')
                        pass

            elif event.startswith('-BOX') and values[event]:
                self.addtswindow[self.last_event].update(value=values[event][0])
                self.addtswindow[f'-CONTAINER{self.last_event}-'].update(visible=False)

            elif event in ('name', 'model', 'part', 'vendor') and self.hints_type:
                self.last_event = event
                list_element: sg.Listbox = self.addtswindow.Element(f'-BOX{event}-')
                make_predictions(event, f'-CONTAINER{event}-')
                for inp in ['name', 'model', 'part', 'vendor']:
                    if inp != event:
                        self.addtswindow[f'-CONTAINER{inp}-'].update(visible=False)

            elif event == "level" and not master == "slave":
                if values[event] == "Комплект" or values[event] == "Составная часть":
                    self.addtswindow["-ADDMORE-"].update(visible=True)
                    self.addtswindow["-TABLE-"].update(visible=True)
                else:
                    self.addtswindow["-ADDMORE-"].update(visible=False)
                    self.addtswindow["-TABLE-"].update(visible=False)

            elif event == "-ADDMORE-":
                window_saved = False
                page2 = Pages()
                page3 = Pages()

                if values["level"] == "Комплект":
                    table2.clear()
                    page2.tsavailable = ["Составная часть", "Элемент"]
                    page2.object = self.object

                    page2.addtspage(master=False, headername="Добавление 2-го уровня")

                    self.resize_and_update_table(table1)

                else:
                    page3.tsavailable = ["Элемент"]
                    page3.object = self.object

                    page3.addtspage(master=False, headername="Добавление 3-го уровня")

                    self.resize_and_update_table(table2)

            elif event == "nopart":
                if values[event]:
                    self.addtswindow["part"].update("б/н", disabled=True)
                else:
                    self.addtswindow["part"].update("", disabled=False)

            elif event == "_SAVE_":
                if values['name'] or values['model'] or values['part'] or values['vendor']:
                    validation_state = True
                    # user input validation

                    # int validation
                    if (self.validate_input(values['serial1'], 1, 'СЗЗ-1') and
                        self.validate_input(values['serial2'], 1, 'СЗЗ-2') and
                        self.validate_input(values['amount'], 1, 'Количество') and
                        self.validate_input(values['rggpp'], 2, 'РГГ ПП')) is not True:
                        validation_state = False

                    if table1 and not ts_id[1]:  # insides check
                        table_partdata = []
                        table_serialdata = []
                        for item in table1:
                            if item[3] in table_partdata and item[3] != '' and item[3] != 'б/н':
                                if popup_yes_no(
                                        f'Серийный номер "{item[3]}"\nуже существует в таблице!\n'
                                        f'Вы действительно хотите использовать дубликат?'):
                                    pass
                                else:
                                    validation_state = False
                                    continue
                            else:
                                table_partdata.append(item[3])

                            if item[5] in table_serialdata and item[5] != '':
                                if popup_yes_no(
                                        f'СЗЗ "{item[5]}"\nуже существует в таблице!\n'
                                        f'Вы действительно хотите использовать дубликат?'):
                                    pass
                                else:
                                    validation_state = False
                                    continue
                            else:
                                table_serialdata.append(item[5])

                            if item[12]:
                                for item1 in item[12]:
                                    if item1[3] in table_partdata and item1[3] != '' and item1[3] != 'б/н':
                                        if popup_yes_no(
                                                f'Серийный номер "{item1[3]}"\nуже существует в таблице!\n'
                                                f'Вы действительно хотите использовать дубликат?'):
                                            pass
                                        else:
                                            validation_state = False
                                            continue
                                    else:
                                        table_partdata.append(item1[3])

                                    if item1[5] in table_serialdata and item1[5] != '':
                                        if popup_yes_no(
                                                f'СЗЗ "{item1[5]}"\nуже существует в таблице!\n'
                                                f'Вы действительно хотите использовать дубликат?'):
                                            pass
                                        else:
                                            validation_state = False
                                            continue
                                    else:
                                        table_serialdata.append(item1[5])

                        table_partdata.clear()
                        table_serialdata.clear()

                    if values['serial1']:
                        serials = baza.get_index_names('serials')

                        for item in serials:
                            if values['serial1'] == item[1]:
                                if ts_id[0] == item[0]:  # edit check
                                    continue
                                else:
                                    sg.popup_no_frame(f'Найден дубликат СЗЗ-1 'f"{values['serial1']}"''
                                                      '\n Его использование невозможно!',
                                                      auto_close_duration=5,
                                                      auto_close=True, font=fontbig)
                                    validation_state = False
                                    continue

                    if not (values['serial1'] or values['serial2'] or values['uv']):
                        validation_state = False
                        sg.popup_no_frame(f'Одно из полей (СЗЗ-1, СЗЗ-2, УФ) должно быть заполнено!',
                                          auto_close_duration=3,
                                          auto_close=True, font=fontbig, button_type=5)

                    if values['part'] and values['part'] != 'б/н':
                        names = baza.get_index_names('parts')

                        for item in names:
                            if values['part'] == item[1]:
                                if ts_id[0] == item[0]:  # edit check
                                    pass
                                else:
                                    if item[0] != '444':
                                        main_content = db.db[item[0]]
                                        if master == True or (master == 'editor' and ts_id[1] == 0) and \
                                                values['part'] == main_content['part']:
                                            answer = popup_input_text(
                                                f'Серийный номер "{values["part"]}" существует в базе!\n'
                                                f'{main_content["name"]}\n'
                                                f'{main_content["model"]}\n'
                                                f'{main_content["part"]}\n'
                                                f'{main_content["vendor"]}\n\n'
                                                'Введите 1 для добавления ТС как нового.\n'
                                                f"{'Введите 2 для замены ТС в базе. (производит удаление)' if values['part'] == main_content['part'] else ''}\n"
                                                'Закройте окно для отмены действия.')
                                            if answer == '1':
                                                # add new record
                                                break
                                            elif answer == '2':
                                                if validation_state:
                                                    baza.delete_by_id(item[0])
                                            else:
                                                validation_state = False
                                                break
                                    else:
                                        answer = popup_yes_no(
                                            f'Серийный номер "{values["part"]}"\nсуществует в базе (или в базе за прошлые года)\n'
                                            f'Вы хотите его использовать?')

                                        if answer:
                                            break
                                        else:
                                            validation_state = False
                                            break

                    if not validation_state:
                        continue

                    if master == 'slave' or (master == 'editor' and (ts_id == (None, None) or ts_id[1] == 1)):
                        self.tsdata = self.get_tsvalues(values)
                        sg.popup_no_frame(f'"{values["name"]}" изменён.', auto_close_duration=1,
                                          auto_close=True, font=fontbig, button_type=5)
                        self.addtswindow.close()

                    elif master == 'editor' and ts_id != (None, None) and ts_id[1] == 0:
                        baza.update_element(ts_id[0], self.get_tsvalues(values))
                        sg.popup_no_frame(f'"{values["name"]}" изменён в базе.', auto_close_duration=1,
                                          auto_close=True, font=fontbig, button_type=5)

                    elif master == True:  # ♂oh shit im sorry♂
                        baza.add(self.get_tsvalues(values))
                        sg.popup_no_frame(f'"{values["name"]}" добавлен в базу.', auto_close_duration=1,
                                          auto_close=True, font=fontbig, button_type=5)

                    else:
                        if self.tsavailable == ["Составная часть", "Элемент"]:
                            self.insert_values_into_table(self.get_tsvalues(values), table1)
                        if self.tsavailable == ["Элемент"]:
                            self.insert_values_into_table(self.get_tsvalues(values), table2)
                        sg.popup_no_frame(f'"{values["name"]}" добавлен.', auto_close_duration=1,
                                          auto_close=True, font=fontbig, button_type=5)
                    window_saved = True

            elif event == "Очистить":
                if not window_saved:
                    if not popup_yes_no('Уверены что хотите очистить без сохранения?'):
                        continue
                whitelist = ['object', 'level', '-TABLE-', 'nopart', 'amount']
                savelist = ['name', 'model', 'part', 'vendor', 'serial1', 'rgg']
                rmlist = []
                window_saved = False

                self.addtswindow['name'].set_focus()

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
                    table2.clear()
                    table.Update("")

                if self.tsavailable == ["Составная часть", "Элемент"]:
                    table2.clear()
                    table.Update("")

                if self.tsavailable != ['Элемент']:
                    table.expand(expand_x=True, expand_y=True)

                for cid in headings:
                    table_widget.column(cid, stretch=True)

                for cid, width in zip(headings, list(map(lambda x: len(x) + 3, headings))):
                    table_widget.column(cid, width=width)

            elif event == "Удалить":
                pos = int(values["-TABLE-"][0])

                if popup_yes_no('Вы уверены что хотите удалить?'):
                    if "Комплект" in self.tsavailable:
                        table1.pop(pos)
                        self.resize_and_update_table(table1)
                    else:
                        table2.pop(pos)
                        self.resize_and_update_table(table2)

            elif event == "Редактировать" and values["-TABLE-"]:
                pos = int(values["-TABLE-"][0])
                tbl = table.Get()
                slave = Pages()
                slave.object = self.object
                slave.tsdata = tbl[pos]

                if values['level'] == "Комплект":
                    slave.tsavailable = ["Составная часть", "Элемент"]
                    print(table1)
                    table2 = deepcopy(table1[pos][12])
                else:
                    slave.tsavailable = ["Элемент"]

                if master == "editor":
                    slave.addtspage(master="editor", headername="Редактирование элемента", ts_id=(ts_id[0], 1))
                else:
                    slave.addtspage(master="slave", headername="Редактирование элемента")

                if slave.tsavailable == ["Составная часть", "Элемент"]:
                    table1[pos] = slave.tsdata

                    self.resize_and_update_table(table1)
                if slave.tsavailable == ["Элемент"]:
                    table2[pos] = slave.tsdata
                    self.resize_and_update_table(table2)

            elif event == "bd_delete":
                if popup_yes_no('Вы уверены что хотите удалить?'):
                    baza.delete_by_id(ts_id[0])
                    self.addtswindow.close()

    def validate_input(self, user_input, option, field_name):
        if len(user_input) == 0:
            return True

        if option == 1:
            try:
                int(user_input)
                return True

            except ValueError:
                sg.popup_no_frame(f'Поле "{field_name}" принимает только числовые значения!',
                                  auto_close_duration=2,
                                  auto_close=True, font=fontbig, button_type=5)
                return False

        elif option == 2:
            pattern = re.compile(r'^(\d+(?:(?:[-,]|, )\d+)*)$')

            if pattern.match(user_input):
                return True
            else:
                sg.popup_no_frame(
                    f'Поле "{field_name}" принимает только числовые значения или значения формата "1-2", "1, 2"!',
                    auto_close_duration=2,
                    auto_close=True, font=fontbig, button_type=5)
                return False
        else:
            return None

    def fun_slave(self):
        allnames = ['object', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'amount', 'uv',
                    'rgg', 'rggpp', 'level', '-TABLE-']
        hideitems = ['nameSAVE', 'modelSAVE', 'partSAVE', 'vendorSAVE', 'serial1SAVE', 'rggSAVE', 'Очистить']
        for element in hideitems:
            self.addtswindow[element].Update(visible=False)
        for element, toput in zip(allnames, self.tsdata):
            self.addtswindow[element].update(toput)

    def get_choices(self):
        if self.hints_type:
            self.choices_name = baza.get_unique_index_names('names')
            self.choices_part = baza.get_unique_index_names('parts')
            self.choices_model = baza.get_unique_index_names('models')
            self.choices_vendor = baza.get_unique_index_names('vendors')

    def resize_and_update_table(self, data):
        table = self.addtswindow['-TABLE-']
        table_widget = table.Widget
        data_bool = replace_bool(deepcopy(data))
        all_data = [headings] + data_bool
        col_widths = [min([max(map(len, columns)), 12]) * char_width for columns in
                      zip(*all_data)]
        col_widths[12] = count_char_length(data_bool)

        headerwidth = 0
        temp_col = []
        for item in col_widths:
            headerwidth += item
        w, v = self.addtswindow.get_screen_dimensions()
        if w + 80 > headerwidth:
            resize = w - headerwidth
            resize = int(resize / 13) + 7
            for cols in col_widths:
                cols += resize
                temp_col.append(cols)
            col_widths.clear()
            col_widths = temp_col.copy()

        table.update(values=data)

        for cid in headings:
            table_widget.column(cid, stretch=False)

        for cid, width in zip(headings, col_widths):
            table_widget.column(cid, width=width)

    def fun_vieweditor(self):
        allnames = ['object', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'amount', 'uv',
                    'rgg', 'rggpp', 'level', '-TABLE-']
        hideitems = ['nameSAVE', 'modelSAVE', 'partSAVE', 'vendorSAVE', 'serial1SAVE', 'rggSAVE', 'Очистить']
        for element in hideitems:
            self.addtswindow[element].Update(visible=False)
        for element, toput in zip(allnames, self.tsdata):
            self.addtswindow[element].update(toput)

    def insert_values_into_table(self, values, table):
        table.append(values)

    def get_tsvalues(self, values):
        allowed_list = ["object", "name", "model", "part", "vendor", "serial1", "serial2", 'amount', "uv",
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

    def trim_table(self, dict_obj):
        temp = dict_obj.copy()
        del temp['table']
        return temp

    def edit_ts_page(self, headername):
        def myFunc(e):
            return e[1]

        input_width = 80
        num_items_to_show = 18

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
                                     select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=False, font=fontbig,
                                     horizontal_scroll=True)]],
                        key='-BOX-CONTAINER-', pad=(0, 0)))]
                ], justification="c", element_justification="c")
            ],
            [
                sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                        enable_events=True, expand_x=True),
                sg.Button('Дополнительно', key="-EXTRAS-", font=fontbutton),
                sg.Button("Открыть", key="-OPEN-", font=fontbutton),
            ]
        ]

        self.edittswidow = sg.Window(headername, editlayout, resizable=True, return_keyboard_events=True,
                                     element_justification="").Finalize()
        self.edittswidow.Maximize()
        if "<Key>" not in self.edittswidow.TKroot.bind_all():
            self.edittswidow.TKroot.bind_all("<Key>", _onKeyRelease, "+")

        list_element: sg.Listbox = self.edittswidow.Element('-BOX-')
        list_element.TKListbox.configure(activestyle='none')
        prediction_list, prediction_ids, item_id, input_text, prev_name, sel_item = [], [], "", "", "", 0
        radid = ("objects", "names", "models", "parts", "vendors", "serials")

        def get_active_radio(val):
            for rad in radid:
                if val[rad]:
                    return rad

        def get_displyed(response, extra_spaces=""):
            if response is not None:
                output = f'{response["object"]} {response["name"]} {response["model"]} {response["part"]} {response["vendor"]} {response["serial1"]}'
                return f"{extra_spaces}{re.sub(' +', ' ', output)}"

        def make_prediction(text, index_name='names'):
            prediction_list.clear()
            prediction_ids.clear()

            index = index_name
            index_name = 'serial1' if index_name == 'serials' else index_name[:-1]
            prev_id = ""

            if text:
                cnt = 0  # counter
                index_values = db.db.get_index_values(index)
                if self.search_type:
                    for content in index_values:
                        if content[1].lower().__contains__(text) and content[0] != prev_id and content[0] != '444':
                            content_id = content[0]
                            prev_id = content_id
                            main_content = db.db[content_id]

                            if main_content[index_name].lower().__contains__(text):
                                prediction_list.append(get_displyed(main_content))
                                prediction_ids.append(content_id)
                                cnt += 1

                            if main_content['table']:
                                for element_1 in main_content['table']:
                                    if element_1[index_name].lower().__contains__(text):
                                        prediction_list.append(get_displyed(element_1, '  '))
                                        prediction_ids.append(content_id)
                                        cnt += 1

                                    if element_1['table']:
                                        for element_2 in element_1['table']:
                                            if element_2[index_name].lower().__contains__(text):
                                                prediction_list.append(get_displyed(element_2, '    '))
                                                prediction_ids.append(content_id)
                                                cnt += 1

                            if self.prediction_len == 0:
                                pass
                            elif cnt >= self.prediction_len != 0:
                                break

                else:
                    for content in index_values:
                        if content[1].lower().startswith(text) and content[0] != prev_id and content[0] != '444':
                            content_id = content[0]
                            prev_id = content_id
                            main_content = db.db[content_id]

                            if main_content[index_name].lower().startswith(text):
                                prediction_list.append(get_displyed(main_content))
                                prediction_ids.append(content_id)
                                cnt += 1

                            if main_content['table']:
                                for element_1 in main_content['table']:
                                    if element_1[index_name].lower().startswith(text):
                                        prediction_list.append(get_displyed(element_1, '  '))
                                        prediction_ids.append(content_id)
                                        cnt += 1

                                    if element_1['table']:
                                        for element_2 in element_1['table']:
                                            if element_2[index_name].lower().startswith(text):
                                                prediction_list.append(get_displyed(element_2, '    '))
                                                prediction_ids.append(content_id)
                                                cnt += 1

                            if self.prediction_len == 0:
                                pass
                            elif cnt >= self.prediction_len != 0:
                                break

            list_element.update(values=prediction_list)
            list_element.update(set_to_index=sel_item)

        def open_editwindow(it_id):
            if it_id:
                obj = baza.get_by_id(it_id)
                editor = Pages()
                editor.tsdata = self.dict_2_list(obj)
                editor.object = editor.tsdata[0]
                editor.addtspage(master="editor", headername="Редактирование и просмотр ТС",
                                 ts_id=(it_id, 0))
                table1.clear()
                table2.clear()

        while True:
            event, values = self.edittswidow.read()

            if event == "-OPEN-" and values["-IN-"]:
                if len(values['-BOX-']) > 0:
                    item_id = prediction_ids[list_element.TKListbox.curselection()[0]]
                    open_editwindow(item_id)
                    radio = get_active_radio(values)

                    choices = baza.get_index_names(radio)
                    choices.sort(key=myFunc)

                    make_prediction(values['-IN-'].lower(), radio)

            elif event == "-CLOSE-" or event == sg.WIN_CLOSED:
                self.edittswidow.close()
                break

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
                    item_id = prediction_ids[list_element.TKListbox.curselection()[0]]
                    open_editwindow(item_id)
                    radio = get_active_radio(values)

                    choices = baza.get_index_names(radio)
                    choices.sort(key=myFunc)

                    make_prediction(values['-IN-'].lower(), radio)

            elif event == '-IN-':
                text = values['-IN-'].lower()
                if text == input_text:
                    continue
                else:
                    input_text = text

                make_prediction(text, get_active_radio(values))

            elif event == '-BOX-' and values['-BOX-']:
                curs_pos = list_element.TKListbox.curselection()[0]
                item_id = prediction_ids[curs_pos]
                open_editwindow(item_id)
                radio = get_active_radio(values)

                choices = baza.get_index_names(radio)
                choices.sort(key=myFunc)

                make_prediction(values['-IN-'].lower(), radio)

                list_element.update(set_to_index=curs_pos, scroll_to_index=curs_pos)

            elif event in radid:
                choices = baza.get_index_names(event)
                choices.sort(key=myFunc)

                self.edittswidow['-IN-'].update("")
                prediction_list, item_id = [], ""
                list_element.update(values=prediction_list)
                sel_item = 0

            elif event == '-EXTRAS-':
                popup_input_text_with_hints('Изменение объекта', 'Изменение объекта')

                self.edittswidow['-IN-'].update("")
                prediction_list, item_id = [], ""
                list_element.update(values=prediction_list)
                sel_item = 0
                radio = get_active_radio(values)

                choices = baza.get_index_names(radio)
                choices.sort(key=myFunc)

                make_prediction(values['-IN-'].lower(), radio)

        self.edittswidow.close()

    def word_output_page(self, headername):
        mswordlib = MSWord.Word()
        wordlayout = [
            [
                sg.Column([
                    [sg.T("         ")],
                    [sg.T("Экспорт в Word", font=fontbig)],
                    [sg.T("         ")],
                    [sg.Input(size=(30, 0), enable_events=True, key='-IN-', justification="l", font=fontbig)],
                    [sg.pin(sg.Col(
                        [[sg.Listbox(values=[], size=(80, 15), enable_events=True, key='-BOX-',
                                     select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                        key='-BOX-CONTAINER-', pad=(0, 0)))]
                ], justification="c", element_justification="c")
            ],
            [
                sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                        enable_events=True, expand_x=True),
                sg.Button("Экспортировать", key="-OPEN-", font=fontbutton),
            ]
        ]

        self.exportwordwindow = sg.Window(headername, wordlayout, resizable=True, return_keyboard_events=True,
                                          element_justification="").Finalize()
        self.exportwordwindow.Maximize()
        list_element: sg.Listbox = self.exportwordwindow.Element('-BOX-')
        list_element.TKListbox.configure(activestyle='none')
        if "<Key>" not in self.exportwordwindow.TKroot.bind_all():
            self.exportwordwindow.TKroot.bind_all("<Key>", _onKeyRelease, "+")

        prediction_list, input_text, sel_item = [], "", 0
        choices = baza.get_unique_index_names('objects')

        while True:
            event, values = self.exportwordwindow.read()

            if event == "-CLOSE-" or event == sg.WIN_CLOSED:
                self.exportwordwindow.close()
                break

            elif event.startswith('Escape'):
                self.exportwordwindow['-IN-'].update('')

            elif event.startswith('Down') and len(prediction_list):
                sel_item = (sel_item + 1) % len(prediction_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event.startswith('Up') and len(prediction_list):
                sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event == '\r':
                if len(values['-BOX-']) > 0:
                    self.exportwordwindow['-IN-'].update(value=values['-BOX-'][0])

            elif event == '-BOX-' and values['-BOX-']:
                self.exportwordwindow['-IN-'].update(value=values['-BOX-'][0])

            elif event == '-IN-':
                text = values['-IN-'].lower()
                if text == input_text:
                    continue
                else:
                    input_text = text
                prediction_list = []
                if text:
                    cnt = 0
                    if self.search_type:
                        for item in choices:
                            if item.lower().__contains__(text):
                                prediction_list.append(item)
                                cnt += 1
                                if cnt == self.prediction_len:
                                    break
                    else:
                        for item in choices:
                            if item.lower().startswith(text):
                                prediction_list.append(item)
                                cnt += 1
                                if cnt == self.prediction_len:
                                    break

                list_element.update(values=prediction_list)
                sel_item = 0
                list_element.update(set_to_index=sel_item)

            elif event == '-OPEN-' and values["-IN-"]:
                def make_listed_items(elements):
                    items = []
                    for element in elements:
                        item = element[1]
                        if type(item) == dict:
                            items.append(item)
                        else:
                            items.append(elements)
                            break
                    return items

                if baza.search_if_exists("$.object", values['-IN-']):
                    objects = make_listed_items(baza.search("$.object", values['-IN-']))
                    conclusion_data = self.set_conclusion_items_page(objects)
                    if conclusion_data is None:
                        continue
                    try:
                        mswordlib.act_table(objects, f"АКТ {values['-IN-']}")
                        mswordlib.conclusion_table(conclusion_data, f"ЗАКЛЮЧЕНИЕ {values['-IN-']}")
                        mswordlib.methods_table(objects, f"МЕТОДЫ {values['-IN-']}")
                        mswordlib.ims_table(objects, f"СПИСОК ИМС {values['-IN-']}")
                        sg.popup_no_frame(f'"{values["-IN-"]}" экспортирован в Word.', auto_close_duration=1,
                                          auto_close=True, font=fontbig, button_type=5)

                        sg.popup_ok(f'СЗЗ 1 = {mswordlib.serial1_count}\n'
                                    f'СЗЗ 2 = {mswordlib.serial2_count}\n', no_titlebar=True, font=fontbig)
                    except PermissionError:
                        sg.Window('Ошибка',
                                  [[sg.T('Закройте документ(ы)!', font=fontbig)],
                                   [sg.Button('Понял', font=fontbutton)]],
                                  element_justification="c", no_titlebar=True, size=(600, 100), auto_close=True,
                                  auto_close_duration=5).read(close=True)

        self.exportwordwindow.close()

    def import_page(self, headername):
        importlayout = [
            [
                sg.Column([
                    [sg.T("         ")],
                    [sg.T("Импорт и экспорт базы", font=fontbig)],
                    [sg.T("         ")],
                    [sg.Input(size=(30, 0), enable_events=True, key='-IN-', justification="l", font=fontbig)],
                    [sg.pin(sg.Col(
                        [[sg.Listbox(values=[], size=(80, 15), enable_events=True, key='-BOX-',
                                     select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                        key='-BOX-CONTAINER-', pad=(0, 0)))]
                ], justification="c", element_justification="c")
            ],
            [
                sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                        enable_events=True, expand_x=True),
                sg.Button("Импортировать", key="-IMPORT-", font=fontbutton),
                sg.Button("Экспортировать", key="-EXPORT-", font=fontbutton),
            ]
        ]

        self.importwindow = sg.Window(headername, importlayout, resizable=True, return_keyboard_events=True,
                                      element_justification="").Finalize()
        self.importwindow.Maximize()
        if "<Key>" not in self.importwindow.TKroot.bind_all():
            self.importwindow.TKroot.bind_all("<Key>", _onKeyRelease, "+")

        list_element: sg.Listbox = self.importwindow.Element('-BOX-')
        list_element.TKListbox.configure(activestyle='none')
        prediction_list, input_text, sel_item = [], "", 0
        choices = baza.get_unique_index_names('objects')

        while True:
            event, values = self.importwindow.read()

            if event == "-CLOSE-" or event == sg.WIN_CLOSED:
                self.importwindow.close()
                break

            elif event.startswith('Escape'):
                self.importwindow['-IN-'].update('')

            elif event.startswith('Down') and len(prediction_list):
                sel_item = (sel_item + 1) % len(prediction_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event.startswith('Up') and len(prediction_list):
                sel_item = (sel_item + (len(prediction_list) - 1)) % len(prediction_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event == '\r':
                if len(values['-BOX-']) > 0:
                    self.importwindow['-IN-'].update(value=values['-BOX-'][0])

            elif event == '-BOX-' and values['-BOX-']:
                self.importwindow['-IN-'].update(value=values['-BOX-'][0])

            elif event == '-IN-':
                text = values['-IN-'].lower()
                if text == input_text:
                    continue
                else:
                    input_text = text
                prediction_list = []
                if text:
                    cnt = 0
                    if self.search_type:
                        for item in choices:
                            if item.lower().__contains__(text):
                                prediction_list.append(item)
                                cnt += 1
                                if cnt == self.prediction_len:
                                    break
                    else:
                        for item in choices:
                            if item.lower().startswith(text):
                                prediction_list.append(item)
                                cnt += 1
                                if cnt == self.prediction_len:
                                    break

                list_element.update(values=prediction_list)
                sel_item = 0
                list_element.update(set_to_index=sel_item)

            elif event == '-EXPORT-' and values["-IN-"]:
                if baza.search_if_exists("$.object", values['-IN-']):
                    objects = baza.search("$.object", values['-IN-'])
                    path = sg.popup_get_folder('NAVI bomji', no_window=True)
                    if path and path is not None:
                        with open(f"{path}"'/'f"{values['-IN-']}.json", "w") as f:
                            f.truncate(0)
                            json.dump(objects, f)
                            sg.popup_no_frame(f'"{values["-IN-"]}" экспортирован.', auto_close_duration=1,
                                              auto_close=True, font=fontbig, button_type=5)
                            self.importwindow.close()
                            break

            elif event == '-IMPORT-':
                file_path = sg.popup_get_file("file search", file_types=(("JSON", "*.json "),), no_window=True)
                if file_path is not None and '.json' in file_path:
                    def change_obj(what, to):
                        temp = what.copy()
                        temp['object'] = to
                        if temp['table']:
                            for item1 in temp['table']:
                                item1['object'] = to
                                if item1['table']:
                                    for item2 in item1['table']:
                                        item2['table'] = to
                        return temp

                    def search_if_item_in_index(item, index_values):
                        if item and item != "" and item is not None and item != 'б/н':
                            return True if item in index_values else False

                    def duplicate_actions(obj_content, name):
                        full_name = "серийный номер" if name == "part" else "СЗЗ"
                        pop_answer = popup_yes_no(
                            f'Найден дубликат: {full_name}. \n'
                            f'Наименование - {str(obj_content["name"])}\n'
                            f'Модель - {str(obj_content["model"])}\n'
                            f'SN - {str(obj_content["part"])}\n'
                            f'Производитель - {str(obj_content["vendor"])}\n'
                            f'СЗЗ - {str(obj_content["serial1"])}\n\n'
                            f'Вы хотите заменить {full_name}?')
                        if pop_answer:
                            pass_state = True
                            while pass_state is True:
                                entered_text = popup_input_text(f'Изменение "{full_name}"')
                                if entered_text is None:
                                    pass_state = False
                                    return False
                                elif entered_text not in baza.get_unique_index_names(
                                        "parts" if name == 'part' else 'serials') and entered_text != "":
                                    obj_content[name] = entered_text
                                    pass_state = False
                                else:
                                    sg.popup_no_frame(
                                        f'Введённый вами номер уже есть в базе!',
                                        auto_close_duration=1,
                                        auto_close=True, font=fontbig, button_type=5)
                                    pass_state = True

                            return True
                        else:
                            return False

                    with open(f"{file_path}", "r", encoding="utf8") as file:
                        file_content = json.load(file)

                        for content in file_content:
                            obj_id = content[0]
                            obj_body = content[1]
                            parts_index = baza.get_unique_index_names('parts')
                            serials_index = baza.get_unique_index_names('serials')
                            save_state = True

                            if not baza.search_by_id_if_exists(obj_id):
                                if search_if_item_in_index(obj_body['part'], parts_index) and save_state:
                                    duplicate_actions(obj_body, 'part')

                                if obj_body['table'] and save_state:
                                    for item in obj_body['table']:
                                        if search_if_item_in_index(item['part'], parts_index) and save_state:
                                            duplicate_actions(item, 'part')

                                        if item['table']:
                                            for item1 in item['table']:
                                                if search_if_item_in_index(item1['part'], parts_index) and save_state:
                                                    duplicate_actions(item1, 'part')

                                if search_if_item_in_index(obj_body['serial1'], serials_index) and save_state:
                                    duplicate_actions(obj_body, 'serial1')

                                if obj_body['table'] and save_state:
                                    for item in obj_body['table']:
                                        if search_if_item_in_index(item['serial1'], serials_index) and save_state:
                                            duplicate_actions(item, 'serial1')

                                        if item['table']:
                                            for item1 in item['table']:
                                                if search_if_item_in_index(item1['serial1'],
                                                                           serials_index) and save_state:
                                                    duplicate_actions(item1, 'serial1')

                                if values["-IN-"]:
                                    baza.add_dict(change_obj(obj_body, values["-IN-"]), obj_id)
                                else:
                                    baza.add_dict(obj_body, obj_id)
                                sg.popup_no_frame(
                                    f'"{str(obj_body["name"])}"\n'
                                    f'{str(obj_body["model"])}\n'
                                    f'{str(obj_body["part"])}\n'
                                    f'{str(obj_body["vendor"])}\n'
                                    f'\nимпортирован.',
                                    auto_close_duration=1,
                                    auto_close=True, font=fontbig, button_type=5)

                            else:
                                sg.popup_no_frame(
                                    f'Наименование - {str(obj_body["name"])}\n'
                                    f'Модель - {str(obj_body["model"])}\n'
                                    f'SN - {str(obj_body["part"])}\n'
                                    f'Производитель - {str(obj_body["vendor"])}\n'
                                    f'СЗЗ - {str(obj_body["serial1"])}\n\n'
                                    f'\nуже существует.',
                                    auto_close_duration=3,
                                    auto_close=True, font=fontbig, button_type=5)
        self.importwindow.close()

    def set_conclusion_items_page(self, items_list):
        def Text(text, size, justification, expand_x=None, key=None):
            return sg.Text(text, size=size, pad=(1, 1), expand_x=expand_x, justification=justification, key=key)

        def generate_display_layout(vals):
            # Заполнение текста в фрейме
            text_to_display = \
                f'{vals["name"]} {vals["model"]} {vals["part"]} {vals["vendor"]} {vals["serial1"]} {vals["serial2"]}'
            return [[Text(text_to_display, 95, 'l', True)], ]

        def generate_displayed_items(content, text_key):
            # Отображение элементов с чекбоксами
            item_layout = [sg.Checkbox('', font=fontbig, enable_events=True, key=f'{text_key}'),
                           sg.Frame('', generate_display_layout(content), pad=((0, 5), (0, 5)), relief=sg.RELIEF_FLAT)]
            return item_layout

        def generate_frame(object_values, frame_key):
            # Вывод внутренних элементов в Комплекте
            # Получает 1 Комплект, выводит все элементы в комплекте (3 уровня)

            frame_layout = []
            if object_values['table']:
                for count1, level2 in enumerate(object_values['table']):
                    key = f'{frame_key}_{count1}'
                    frame_layout.append(generate_displayed_items(level2, key))
                    if level2['table']:
                        for count2, level3 in enumerate(level2['table']):
                            frame_layout.append(generate_displayed_items(level3, f'{key}_{count2}'))
            return sg.Frame(
                f'{object_values["name"]} {object_values["model"]} {object_values["part"]} {object_values["vendor"]} '
                f'{object_values["serial1"]}', frame_layout, pad=((0, 5), 0))

        column_layout = [
            [generate_frame(content, count)]
            for count, content in enumerate(items_list)
        ]
        layout = [
            [
                sg.Column(column_layout, scrollable=True, vertical_scroll_only=False, expand_x=True, expand_y=True,
                          size_subsample_width=0.3),
            ],
            [
                sg.Button('Далее', k='-NEXT-', font=fontbutton, expand_x=False),
            ],
        ]
        window = sg.Window(f'{items_list[0]["object"]}', layout, margins=(10, 10), resizable=True,
                           element_justification='c', font=fontbig).Finalize()
        window.Maximize()

        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, 'Exit'):
                window.close()
                return None
            elif event == '-NEXT-':
                test_data = deepcopy(items_list)
                keys_with_true_values = [key for key, value in values.items() if value == True]
                # for list loop, get a path, add key to item
                for item in keys_with_true_values:
                    result = list(map(int, item.split("_")))
                    selected_item = {}
                    if len(result) == 1:
                        selected_item = test_data[result[0]]
                    elif len(result) == 2:
                        selected_item = test_data[result[0]]['table'][result[1]]
                    elif len(result) == 3:
                        selected_item = test_data[result[0]]['table'][result[1]]['table'][result[2]]
                    selected_item['selected'] = True
                window.close()
                return test_data

    def set_items_sequence_page(self, headername, object_name):
        input_width = 80
        num_items_to_show = 18

        def get_displyed(vals):
            if vals is not None:
                output = [vals['object'], vals['name'], vals['model'], vals['part'], vals['vendor'],
                          vals['serial1']]
                return ' '.join(output).split()

        test_vals = []
        test_ids = []

        def get_numerated_items(obj_name):
            test_vals.clear()
            test_ids.clear()
            index_values_dirty = db.db.get_index_values('objects')
            prev_id = ''
            index_values = list(filter(lambda x: x[1] == obj_name, index_values_dirty))

            for count, content in enumerate(index_values):
                if content[0] != prev_id and content[0] != '444':
                    content_id = content[0]
                    prev_id = content_id
                    main_content = db.db[content_id]

                    if main_content['object'].startswith(obj_name):
                        test_vals.append([count, f'{" ".join(get_displyed(main_content))}'])  # bad
                        test_ids.append(content_id)

            self.seqwindow['-BOX-'].update(values=test_vals)

        def re_renumerate_items(items_ids):  # gets ids, returns updated test_vals and test_ids, and updates -BOX-
            test_vals.clear()
            test_ids.clear()

            for count, item in enumerate(items_ids):
                main_content = db.db[item]
                test_vals.append([count, f'{" ".join(get_displyed(main_content))}'])
                test_ids.append(item)

            self.seqwindow['-BOX-'].update(values=test_vals)

        def get_selected_items_pos(vals):  # gets values, returns listed positions
            positions = []

            for item in vals:
                positions.append(item[0])

            return positions

        def put_selected_items(positions,
                               start_inserting_at,
                               original_list):  # gets list of ids and start position, returns new ids list
            elements_to_move = [original_list[i] for i in positions]

            for i in sorted(positions, reverse=True):
                del original_list[i]

            original_list[start_inserting_at:start_inserting_at] = elements_to_move

            return original_list

        def alphabetical_sort(items_ids):  # gets item_ids, returns sorted list of id and content by name
            pass

        seqlayout = [
            [
                sg.Column([
                    [sg.T("         ")],
                    [sg.T("Изменение последовательности", font=fontbig)],
                    [sg.T("         ")],
                    [sg.pin(sg.Col(
                        [[sg.Listbox(values=test_vals, size=(input_width, num_items_to_show), enable_events=True,
                                     key='-BOX-',
                                     select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, no_scrollbar=False, font=fontbig,
                                     horizontal_scroll=True)]],
                        key='-BOX-CONTAINER-', pad=(0, 0)))]
                ], justification="c", element_justification="c")
            ],
            [
                sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                        enable_events=True, expand_x=True),
                sg.Button("Сохранить", key="-SAVE-", font=fontbutton),
            ]
        ]

        self.seqwindow = sg.Window(headername, seqlayout, resizable=True, return_keyboard_events=True,
                                   element_justification="").Finalize()
        self.seqwindow.Maximize()
        if "<Key>" not in self.seqwindow.TKroot.bind_all():
            self.seqwindow.TKroot.bind_all("<Key>", _onKeyRelease, "+")

        list_element: sg.Listbox = self.seqwindow.Element('-BOX-')
        list_element.TKListbox.configure(activestyle='none')

        get_numerated_items(object_name)

        while True:
            event, values = self.seqwindow.read()

            if event == sg.WIN_CLOSED or event == "-CLOSE-" or event.startswith('Escape'):
                self.seqwindow.close()
                break

            elif event == '\r':
                starting_position = None
                while True:
                    try:
                        starting_position = int(popup_input_text('Введите позицию начала вставки'))
                        break
                    except ValueError:
                        pass
                    except TypeError:
                        break

                if starting_position is not None:
                    new_ids_list = put_selected_items(get_selected_items_pos(values['-BOX-']),
                                                      starting_position,
                                                      test_ids).copy()
                    re_renumerate_items(new_ids_list)

            elif event == '-SAVE-':
                for item in test_ids:
                    content = db.db[item]
                    baza.delete_by_id(item)
                    baza.add_dict(content, item)


class SpUi:

    def makeui(self):
        pages = Pages()
        sg.theme('DarkAmber')
        pages.mainpage()

        while True:  # MainPage
            event, values = pages.window.read()
            if event == "-Add-":
                pages.window.Hide()

                if pages.credentialspage:  # close check
                    pages.addtspage(master=True, headername="Добавление технического средства")
                    table1.clear()
                    table2.clear()

                pages.window.UnHide()

            elif event == "-Edit-":
                pages.window.Hide()
                pages.edit_ts_page("Редактирование")

                pages.window.UnHide()

            elif event == "-Export-":
                pages.window.Hide()
                pages.word_output_page("Экспорт в Word")

                pages.window.UnHide()

            elif event == "-Import-":
                pages.window.Hide()
                pages.import_page("Импорт и экспорт")

                pages.window.UnHide()

            elif event == "-Extra-":
                pages.window.Hide()
                while True:
                    object_name = real_popup_input_text_with_hints('Выбор объекта', "Введите название объекта")
                    if object_name is None:
                        break
                    else:
                        pages.set_items_sequence_page("Изменение последовательности", object_name)
                        break

                pages.window.UnHide()

            elif event == "-Settings-":
                pages.window.Hide()
                pages.settingspage()

                pages.window.UnHide()

            elif event == sg.WIN_CLOSED:
                break

        pages.window.close()

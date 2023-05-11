import json
import re
import db
import MSWord
import PySimpleGUI as sg
import pyperclip
import sys
import threading
import multiprocessing

from tabulate import tabulate
from os import path
from copy import deepcopy

__version__ = "0.4.6"
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
char_width_mid = sg.Text.char_width_in_pixels(fontmid)
stop_animated_thread, animated_thread_work = 0, 0
serial_1, serial_2 = 0, 0

find_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
path_to_icon = path.abspath(path.join(find_dir, 'favicon.ico'))
sg.set_global_icon(path_to_icon)

baza = db.DataBase(db_name=db.db)
settings_db = db.DataBase(db_name=db.settings_db)
tdb = db.db
multiprocessing.freeze_support()

listbox_width = 120
listbox_hight = settings_db.get_by_id("1337")["input_rows"]


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

    if event.keycode == 83 and ctrl:  # ctrl + s, save
        event.widget.event_generate("<<MySave>>")

    if event.keycode == 78 and ctrl:  # ctrl + n, clear
        event.widget.event_generate("<<MyClear>>")


def start_word_export(objects, conclusion_data, export_path, object_name):
    global serial_1, serial_2, stop_animated_thread, animated_thread_work
    child_conn, parent_conn = multiprocessing.Pipe()
    MSWord.main_docs_dict, processes = {}, []
    processor_args = [
        ('act_table', objects, child_conn, [export_path, object_name]),
        ('conclusion_table', conclusion_data, child_conn, [export_path, object_name]),
        ('methods_table', objects, child_conn, [export_path, object_name]),
        ('ims_table', objects, child_conn, [export_path, object_name])
    ]

    for arg in processor_args:
        p = multiprocessing.Process(target=MSWord.processes_runner, args=arg, daemon=False)
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    serial_1, serial_2 = parent_conn.recv()
    stop_animated_thread, animated_thread_work = 1, 0


def popup_yes(main_text='Заглушка'):
    layout = [[
        sg.Column([
            [sg.T("         ")],
            [sg.T(f"{main_text}", font=fontbig, justification='c')],
        ], justification="c", element_justification="c")
    ], [
        sg.Column([
            [sg.Cancel('Ок', font=fontbutton, s=(15, 0)), ],
        ], justification="c", element_justification="c")
    ]]
    popupwin = sg.Window('Подтверждение', layout, resizable=False, return_keyboard_events=True,
                         keep_on_top=True).Finalize()

    while True:
        event, values = popupwin.read()

        if event == sg.WIN_CLOSED:
            popupwin.close()
            return 0

        elif event.startswith("\r") or event == 'Ок':
            popupwin.close()
            return 1


def popup_yes_no_layouted(layouted):
    layout = [
        layouted,
        [
            sg.Column([
                [sg.Cancel('Да', font=fontbutton, s=(15, 0)),
                 sg.Submit("Нет", font=fontbutton, s=(15, 0))],
            ], justification="c", element_justification="c")
        ]]
    popupwin = sg.Window('Подтверждение', layout, resizable=True, return_keyboard_events=True,
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
                         element_justification='c',
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


def popup_input_text_layout(layout_param):
    layout = [
        layout_param,
        [
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
    settings_query = settings_db.get_by_id("1337")
    choices = sorted(baza.get_unique_index_names(f"{index_name}"))

    hintedinputlayout = [
        [
            sg.Column([
                [sg.T("         ")],
                [sg.T(f"{middle_text}", font=fontbig)],
                [sg.T("         ")],
                [sg.Input(size=(listbox_width, 0), enable_events=True, key='-IN-', justification="l", font=fontbig)],
                [sg.pin(sg.Col(
                    [[sg.Listbox(values=[], size=(listbox_width, listbox_hight), enable_events=True, key='-BOX-',
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

    hintedinputwindow['-IN-'].SetFocus(True)
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
    settings_query = settings_db.get_by_id("1337")
    choices = sorted(baza.get_unique_index_names(f"{index_name}"))

    hintedinputlayout = [
        [
            sg.Column([
                [sg.T("         ")],
                [sg.T(f"{middle_text}", font=fontbig)],
                [sg.T("         ")],
                [sg.Input(size=(listbox_width, 0), enable_events=True, key='-IN-', justification="l", font=fontbig)],
                [sg.pin(sg.Col(
                    [[sg.Listbox(values=[], size=(listbox_width, listbox_hight), enable_events=True, key='-BOX-',
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

    hintedinputwindow['-IN-'].SetFocus(True)
    list_element: sg.Listbox = hintedinputwindow.Element('-BOX-')
    prediction_list, prediction_ids, input_text, sel_item = [], [], "", 0

    while True:
        event, values = hintedinputwindow.read()

        if event == "-DELETE-" and values["-IN-"]:
            if baza.search_if_exists("$.object", values['-IN-']):
                if popup_yes_no(f'Вы действительно хотите удалить "{values["-IN-"]}"?'):
                    for item in baza.search('$.object', f'{values["-IN-"]}'):
                        baza.delete_by_id(item[0])

                    choices = sorted(baza.get_unique_index_names(f"{index_name}"))
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

                    choices = sorted(baza.get_unique_index_names(f"{index_name}"))
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
        self.edittswidow = None
        self.exportwordwindow = None
        self.importwindow = None
        self.seqwindow = None
        self.conclusionwindow = None
        self.addts_window_saved = False

        self.object = None
        self.tsdata = []
        self.tsavailable = ["Комплект", "Составная часть", "Элемент"]
        self.choices_name, self.choices_model, self.choices_part, self.choices_vendor, self.predictions_list = [], [], [], [], []
        self.input_text, self.last_event = '', ''

        # settings
        settings_query = settings_db.get_by_id("1337")
        self.search_type = settings_query['search']
        self.hints_type = settings_query['hints']
        self.savestates = settings_query['savestates']
        self.jump_type = settings_query['jump']
        self.prediction_len = int(settings_query['max_len'])
        self.theme = settings_query['theme']
        self.author = settings_query['author']

    def mainpage(self):
        mainpage = [
            [sg.Column(
                [[sg.Button('Добавление', key="-Add-", enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            pad=(30, 30),
                            s=(30, 5),
                            button_color=(sg.theme_text_color(), sg.theme_background_color()),
                            border_width=0,
                            font=fontbig,
                            ),
                  sg.Button('Редактирование и просмотр', key="-Edit-", enable_events=True,
                            expand_x=True,
                            expand_y=True,
                            pad=(30, 30),
                            s=(30, 5),
                            button_color=(sg.theme_text_color(), sg.theme_background_color()),
                            border_width=0,
                            font=fontbig
                            )], ], justification='c')],
            [sg.Column(
                [[sg.Button('Импорт\rэкспорт', key="-Import-", enable_events=True,
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
                [[sg.Button('Изменение\nпоследовательности', key="-Extra-", enable_events=True,
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
        temp_settings_query = settings_db.get_by_id("1337")
        global listbox_hight
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
                sg.Text('Чекбоксы для сохрнения полей при очистке (Добавление ТС): ', font=fontbig),
                sg.DropDown(values=['Вкл', 'Выкл'],
                            default_value="Вкл" if temp_settings_query['savestates'] else "Выкл",
                            font=fontmid, key='savestates', readonly=True)
            ],
            [
                sg.Text('Переход к новому полю через Enter (Добавление ТС): ', font=fontbig),
                sg.DropDown(values=['Вкл', 'Выкл'], default_value="Вкл" if temp_settings_query['jump'] else "Выкл",
                            font=fontmid, key='jump', readonly=True)
            ],
            [
                sg.Text('Максимальное количество вывода элементов (0 - все) ', font=fontbig),
                sg.InputText(default_text=int(temp_settings_query['max_len']), font=fontmid, key='max_len', s=(4, 0)
                             , justification='c')
            ],
            [
                sg.Text('Выбор темы (применение после перезагрузки) ', font=fontbig),
                sg.DropDown(values=sg.theme_list(),
                            default_value=temp_settings_query['theme'] if temp_settings_query['theme'] else "DarkAmber",
                            font=fontmid, key='theme', readonly=True, enable_events=True)
            ],
            [
                sg.Text('Количество строк в списках (масштабирование под разрешение экрана) ', font=fontbig),
                sg.InputText(default_text=int(temp_settings_query['input_rows']), font=fontmid, key='input_rows',
                             s=(4, 0), justification='c')
            ],
            [
                sg.Text('Автор ', font=fontbig),
                sg.InputText(default_text=temp_settings_query['author'], font=fontmid, key='author',
                             s=(40, 0), justification='c')
            ],
            [
                sg.Text('Назад', key="-CLOSE-", enable_events=True, justification="l", expand_x=True,
                        font=fontbutton)
            ]
        ]
        self.settingswindow = sg.Window(f'Настройки. Версия {__version__}', settingslayout, resizable=True,
                                        return_keyboard_events=True,
                                        element_justification="c").Finalize()
        self.settingswindow['search'].SetFocus(True)

        if "<Key>" not in self.settingswindow.TKroot.bind_all():
            self.settingswindow.TKroot.bind_all("<Key>", _onKeyRelease, "+")

        while True:
            event, values = self.settingswindow.read()

            if event == sg.WIN_CLOSED:
                self.settingswindow.close()
                break

            elif event == "-CLOSE-" or event.startswith('Escape'):
                try:
                    int(values['max_len'])
                except ValueError:
                    self.settingswindow['max_len'].Update(temp_settings_query['max_len'])
                    popup_yes('Поле "Максимальное количество вывода элементов" принимает только численные значения!')
                    continue

                try:
                    int(values['input_rows'])
                except ValueError:
                    self.settingswindow['input_rows'].Update(temp_settings_query['input_rows'])
                    popup_yes('Поле "Количество строк в списках" принимает только численные значения!')
                    continue

                if values['author'] == "":
                    self.settingswindow['author'].Update(temp_settings_query['author'])
                    popup_yes('Поле "Автор" не должно быть пустым!')
                    continue

                temp_settings = {'search': True if values['search'] == 'По содержанию' else False,
                                 'hints': True if values['hints'] == 'Вкл' else False,
                                 'savestates': True if values['savestates'] == 'Вкл' else False,
                                 'jump': True if values['jump'] == 'Вкл' else False,
                                 'max_len': values['max_len'],
                                 'theme': values['theme'],
                                 'input_rows': values['input_rows'],
                                 'author': values['author']}

                settings_db.update_element_dict('1337', temp_settings)
                self.hints_type = temp_settings['hints']
                self.jump_type = temp_settings['jump']
                self.search_type = temp_settings['search']
                self.savestates = temp_settings['savestates']
                self.prediction_len = int(temp_settings['max_len'])
                self.theme = temp_settings['theme']
                self.author = temp_settings['author']
                listbox_hight = int(temp_settings['input_rows'])
                self.settingswindow.close()
                del temp_settings
                break

    @property
    def credentialspage(self):
        choices = sorted(baza.get_unique_index_names("objects"))

        credentialslayout = [
            [sg.Text('Объект', font=fontbig)],
            [sg.Input(key='-OBJECT-', font=fontbig, enable_events=True, s=(25, 0))],
            [sg.pin(sg.Col(
                [[sg.Listbox(values=[], size=(80, 4), enable_events=True, key='-BOX-',
                             select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                key='-BOX-CONTAINER-', pad=(0, 0), visible=True if self.hints_type else False))],
            [sg.Button('Далее', size=(15, 0), font=fontbutton),
             sg.Cancel('Отмена', font=fontbutton)]
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

            elif event == "Далее" and values["-OBJECT-"]:
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
                if sel_item == list_element.TKListbox.curselection()[0]:
                    self.credentialswindow['-OBJECT-'].update(value=values['-BOX-'][0])
                    self.credentialswindow.write_event_value("Далее", values["-BOX-"])
                else:
                    sel_item = list_element.TKListbox.curselection()[0]

    def addtspage(self, master, headername, ts_id=(None, None)):
        global table1, table2
        sel_item = 0
        col_widths = list(map(lambda x: len(x) + 2, headings))
        tabledata = []
        event_list = ['name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'amount', 'rgg', 'rggpp']
        addtspage = [
            [sg.Column(
                [[sg.Text('Объект', font=fontmid), sg.InputText(key='object', default_text=self.object, disabled=True,
                                                                s=(int(len(self.object) * 1.2), 5), text_color="black",
                                                                font=fontmidlow, justification='c'),
                  sg.InputText(key='author', default_text=self.author, disabled=True, visible=False,
                               s=(int(len(self.author) * 1.2), 5), text_color="black", font=fontmidlow,
                               justification='c')]], justification="c"
            )],
            [sg.Column(
                [[sg.Text('Наименование ТС', font=fontmid),
                  sg.Input(key='name', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="nameSAVE", font=fontmid, visible=self.savestates)],

                 [sg.pin(sg.Col(
                     [[sg.Listbox(values=[], size=(35, 4), enable_events=True, key='-BOXname-',
                                  select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                     key='-CONTAINERname-', pad=(105, 0), visible=False))],

                 [sg.Text('Модель', font=fontmid),
                  sg.Input(key='model', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="modelSAVE", font=fontmid, visible=self.savestates)],

                 [sg.pin(sg.Col(
                     [[sg.Listbox(values=[], size=(35, 4), enable_events=True, key='-BOXmodel-',
                                  select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                     key='-CONTAINERmodel-', pad=(105, 0), visible=False, justification='c'))],

                 [sg.Text('Заводской номер', font=fontmid),
                  sg.Input(key='part', enable_events=True, font=fontmid, s=(39, 0)),
                  sg.Checkbox("б/н", k="nopart", enable_events=True, font=fontmid),
                  sg.Checkbox("Сохр.", k="partSAVE", font=fontmid, visible=self.savestates)],

                 [sg.pin(sg.Col(
                     [[sg.Listbox(values=[], size=(35, 4), enable_events=True, key='-BOXpart-',
                                  select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                     key='-CONTAINERpart-', pad=(105, 0), visible=False, justification='c'))],

                 [sg.Text('Производитель', font=fontmid),
                  sg.Input(key='vendor', size=(45, 0), font=fontmid, enable_events=True),
                  sg.Checkbox("Сохр.", k="vendorSAVE", font=fontmid, visible=self.savestates)],

                 [sg.pin(sg.Col(
                     [[sg.Listbox(values=[], size=(35, 4), enable_events=True, key='-BOXvendor-',
                                  select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                     key='-CONTAINERvendor-', pad=(105, 0), visible=False, justification='c'))],

                 [sg.Text('СЗЗ-1', font=fontmid), sg.InputText(key='serial1', font=fontmid, s=(15, 0)),
                  sg.Checkbox("Сохр.", k="serial1SAVE", font=fontmid, visible=self.savestates)],
                 [sg.Checkbox("УФ", font=fontmid, key='uv'),
                  sg.Text('СЗЗ-2', font=fontmid), sg.InputText(key='serial2', s=(3, 0), font=fontmid),
                  sg.Text('Кол-во', font=fontmid), sg.InputText(default_text="1", key='amount', font=fontmid, s=(3, 0))]
                 ]
                , justification="c", element_justification="r"
            )],
            [sg.Column(
                [[sg.Text('РГ', font=fontmid),
                  sg.Input(k='rgg', enable_events=True, font=fontmid, s=(10, 0)),
                  sg.Checkbox("Сохр.", k="rggSAVE", font=fontmid, visible=self.savestates),
                  sg.Text('РГ пп', font=fontmid), sg.InputText(key='rggpp', s=(5, 0), font=fontmid)]]
                , justification="c")],
            [sg.Column(
                [[sg.Text(f'Признак (уровень) - {self.tsavailable[0]}', font=fontmid),
                  sg.Combo(self.tsavailable, readonly=True, enable_events=True, key="level",
                           default_value=self.tsavailable[0], font=fontmidlow, visible=False),  # unhandled errors
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
                enable_events=True,
                key='-TABLE-'), ],
            [sg.Text('Назад', key="-CloseAddTsPage-", enable_events=True, justification="l", expand_x=True,
                     font=fontbutton),
             sg.Button("Копировать", k="-COPY-", font=fontbutton),
             sg.Button("Вставить", k="-PASTE-", font=fontbutton),
             sg.Text("", pad=(200, 0)),
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
        table_selected = 0

        displaycolumns = deepcopy(headings)
        displaycolumns.remove('Объект')
        table.ColumnsToDisplay = displaycolumns
        table_widget.configure(displaycolumns=displaycolumns)
        list_element: sg.Listbox = self.addtswindow.Element(f'-BOXname-')

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
                try:
                    self.addtswindow["author"].Update(baza.get_by_id(ts_id[0])['author'])
                    self.addtswindow["author"].Update(visible=True)
                except KeyError:
                    self.addtswindow["author"].Update('AUTHOR ERROR')

                if ts_id[1] == 0:
                    self.addtswindow['-CloseAddTsPage-'].Update('Выход')
                    self.addtswindow['_SAVE_'].Update('Сохранить в БД')
                    self.addtswindow["bd_delete"].Update(visible=True)

            if self.tsavailable == ["Комплект", "Составная часть", "Элемент"]:
                table1 = self.tsdata[12]
            if self.tsavailable == ["Составная часть", "Элемент"]:
                table2 = self.tsdata[12]
            if self.tsdata[11] == 'Элемент':
                table.Update(visible=False)
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
                window_is_saved = True
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
                try:
                    if not self.addts_window_saved:
                        if master == 'editor' or master == 'slave':
                            if not self.tsdata == self.get_tsvalues(values):  # is not changed in edit
                                window_is_saved = False
                            if not ts_id[1] and not self.tsdata == self.dict_2_list_no_author(baza.get_by_id(ts_id[0])):
                                window_is_saved = False
                        if type(master) is bool and self.get_tsvalues(values) != [self.object, '', '', '', '', '', '',
                                                                                  '1', False, '', '', values['level'],
                                                                                  []]:
                            window_is_saved = False
                except TypeError:
                    pass

                if event is not sg.WIN_CLOSED:
                    if not window_is_saved and not self.addts_window_saved:
                        if not popup_yes_no('Уверены что хотите выйти без сохранения?'):
                            continue

                if self.tsavailable == ["Комплект", "Составная часть", "Элемент"] and not master:
                    table1.clear()
                elif self.tsavailable == ["Составная часть", "Элемент"] and not master:
                    table2.clear()
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
                    if current_max_depth == 3 and temp_table != table1:
                        for item in temp_table:
                            table1.append(item)
                    elif current_max_depth == 2 and temp_table != table2:
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

                rename_element(pasted_content)

                self.resize_and_update_table(self.dict_2_list(deepcopy(pasted_content))[12])
                add_content_to_table()
                pasted_content.pop('table')
                self.addts_window_saved = False

                for name, val in pasted_content.items():
                    self.addtswindow[name].update(val)

            elif event == '\r':
                if self.last_event:
                    if len(values[f'-BOX{self.last_event}-']) > 0:
                        self.addtswindow[self.last_event].update(value=values[f'-BOX{self.last_event}-'][0])
                        self.addtswindow[f'-CONTAINER{self.last_event}-'].update(visible=False)
                        self.addtswindow[f'-BOX{self.last_event}-'].update('')
                        self.input_text = values[f'-BOX{self.last_event}-'][0].lower()
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
                    if inp != event or values[event] == "":
                        self.addtswindow[f'-CONTAINER{inp}-'].update(visible=False)

            elif event == "level":
                if values[event] == "Комплект" or values[event] == "Составная часть":
                    self.addtswindow["-ADDMORE-"].update(visible=True)
                    self.addtswindow["-TABLE-"].update(visible=True)
                else:
                    self.addtswindow["-ADDMORE-"].update(visible=False)
                    self.addtswindow["-TABLE-"].update(visible=False)

            elif event == "-ADDMORE-":
                page2 = Pages()
                page3 = Pages()

                if values["level"] == "Комплект":
                    table2.clear()
                    page2.tsavailable = ["Составная часть", "Элемент"]
                    page2.object = self.object

                    page2.addtspage(master=False, headername="Добавление 2-го уровня")

                    if table1:
                        self.resize_and_update_table(table1)
                        self.addts_window_saved = False
                else:
                    page3.tsavailable = ["Элемент"]
                    page3.object = self.object

                    page3.addtspage(master=False, headername="Добавление 3-го уровня")

                    if table2:
                        self.resize_and_update_table(table2)
                        self.addts_window_saved = False

            elif event == "nopart":
                if values[event]:
                    self.addtswindow["part"].update("б/н", disabled=True)
                else:
                    self.addtswindow["part"].update("", disabled=False)

            elif event == "-TABLE-" and values["-TABLE-"]:
                if table_selected == int(values["-TABLE-"][0]):
                    self.addtswindow.write_event_value("Редактировать", table_selected)
                else:
                    table_selected = int(values["-TABLE-"][0])

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
                                        try:
                                            main_content = db.db[item[0]]
                                        except KeyError:
                                            continue
                                        main_content_name = main_content["name"]
                                        if master == True or (master == 'editor' and ts_id[1] == 0) and \
                                                values['part'] == main_content['part']:
                                            dubs_layout = [
                                                sg.Column([
                                                    [sg.T(f'Серийный номер "{values["part"]}" существует в базе!\n',
                                                          font=fontbig, justification='c')],
                                                    [sg.T(str(tabulate([["Наименование", main_content["name"]],
                                                                        ["Модель", main_content["model"]],
                                                                        ["Серийный номер", main_content["part"]],
                                                                        ["Производитель", main_content["vendor"]]],
                                                                       numalign="center", stralign="center")),
                                                          font=('Consolas', 20))],
                                                    [sg.T(
                                                        f"\nВведите 1 для сохранения ТС.\n"
                                                        f"{f'Введите 2 для замены ТС в базе. (Будет добавлено новое ТС. {main_content_name} будет УДАЛЁН!)' if values['part'] == main_content['part'] else ''}\n"
                                                        f"Закройте окно для отмены действия.", font=fontbig,
                                                        justification='c')]
                                                ], justification='c', element_justification='c')
                                            ]
                                            answer = popup_input_text_layout(dubs_layout)
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
                                            f'Серийный номер "{values["part"]}"\nсуществует в базе за прошлые года (возможно в текущей базе)\n'
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
                        popup_yes(f'"{values["name"]}" изменён.')
                        self.addtswindow.close()

                    elif master == 'editor' and ts_id != (None, None) and ts_id[1] == 0:
                        baza.update_element(ts_id[0], self.get_tsvalues(values),
                                            author=settings_db.get_by_id('1337')['author'])
                        popup_yes(f'"{values["name"]}" изменён в базе.')
                        self.addts_window_saved = True

                    elif master == True:  # ♂oh shit im sorry♂
                        baza.add(self.get_tsvalues(values), author=self.author)
                        popup_yes(f'"{values["name"]}" добавлен в базу.')
                        self.addts_window_saved = True

                    else:
                        if self.tsavailable == ["Составная часть", "Элемент"]:
                            self.insert_values_into_table(self.get_tsvalues(values), table1)
                        if self.tsavailable == ["Элемент"]:
                            self.insert_values_into_table(self.get_tsvalues(values), table2)
                        popup_yes(f'"{values["name"]}" добавлен.')
                        self.addts_window_saved = True

            elif event == "Очистить":
                if not self.addts_window_saved:
                    if not popup_yes_no('Уверены что хотите очистить без сохранения?'):
                        continue
                whitelist = ['object', 'level', '-TABLE-', 'nopart']
                savelist = ['name', 'model', 'part', 'vendor', 'serial1', 'rgg']
                rmlist = []
                self.addts_window_saved = True
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

                self.addtswindow['amount'].Update('1')

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

            elif event == "Удалить" and values["-TABLE-"]:
                pos = int(values["-TABLE-"][0])
                if popup_yes_no('Вы уверены что хотите удалить?'):
                    self.addts_window_saved = False
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
                    try:
                        table2 = deepcopy(table1[pos][12])
                    except IndexError:
                        print('err in level')
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
                    try:
                        table2[pos] = slave.tsdata
                        self.resize_and_update_table(table2)
                    except IndexError:
                        table1[pos] = slave.tsdata
                        self.resize_and_update_table(table1)

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
            self.choices_name = sorted(baza.get_unique_index_names('names'))
            self.choices_part = sorted(baza.get_unique_index_names('parts'))
            self.choices_model = sorted(baza.get_unique_index_names('models'))
            self.choices_vendor = sorted(baza.get_unique_index_names('vendors'))

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

        for value in allowed_list:
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

    def dict_2_list_no_author(self, dict_obj):
        try:
            dict_obj.pop('author')
        except KeyError:
            pass
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
        class DelayedExecution:
            def __init__(self, func=None, args=None):
                self.func = func
                self.args = args
                self.timer = None

            def start(self):
                if self.timer is not None:
                    self.timer.cancel()
                    self.timer = None

                self.timer = threading.Timer(1, self.func, self.args)
                self.timer.start()

        def myFunc(e):
            return e[1]

        editlayout = [
            [
                sg.Column([
                    [sg.Radio("Объект", "rad0", k='objects', enable_events=True, font=fontbig, default=True),
                     sg.Radio("Название", "rad0", k='names', enable_events=True, font=fontbig),
                     sg.Radio("Модель", "rad0", k="models", enable_events=True, font=fontbig),
                     sg.Radio("Серийный номер", "rad0", k="parts", enable_events=True, font=fontbig),
                     sg.Radio("Производитель", "rad0", k="vendors", enable_events=True, font=fontbig),
                     sg.Radio("СЗЗ", "rad0", k="serials", enable_events=True, font=fontbig)],
                    [sg.T("         ")],
                    [sg.T("ПОИСК ТС", font=fontbig)],
                    [sg.T("         ")],
                    [sg.Input(size=(listbox_width, 0), enable_events=True, key='-IN-', justification="l",
                              font=fontbig)],
                    [sg.pin(sg.Col(
                        [[sg.Listbox(values=[], size=(listbox_width, listbox_hight), enable_events=True, key='-BOX-',
                                     select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=False, font=fontbig,
                                     horizontal_scroll=True, expand_y=True)]],
                        key='-BOX-CONTAINER-', pad=(0, 0)))],
                ], justification="c", element_justification="c")
            ],
            [
                sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                        enable_events=True, expand_x=True),
                sg.Button('Объекты', key="-SHOWALL-", font=fontbutton),
                sg.Button('Дополнительно', key="-EXTRAS-", font=fontbutton),
                sg.Button("Открыть", key="-OPEN-", font=fontbutton),
            ]
        ]

        self.edittswidow = sg.Window(headername, editlayout, resizable=True, return_keyboard_events=True,
                                     element_justification="").Finalize()
        self.edittswidow.Maximize()
        if "<Key>" not in self.edittswidow.TKroot.bind_all():
            self.edittswidow.TKroot.bind_all("<Key>", _onKeyRelease, "+")

        self.edittswidow['-IN-'].SetFocus(True)
        list_element: sg.Listbox = self.edittswidow.Element('-BOX-')
        list_element.TKListbox.configure(activestyle='none')
        prediction_list, prediction_ids, item_id, input_text, prev_name, sel_item, active_radio = \
            [], [], "", "", "", 0, "objects"
        executor = DelayedExecution(func=self.edittswidow.start_thread)

        def get_displyed(response, extra_spaces=""):
            try:
                author = response['author']
            except KeyError:
                author = ''
            if response is not None:
                output = f'{response["object"]} {response["name"]} {response["model"]} {response["part"]} {response["vendor"]} {response["serial1"]} {author}'
                return f"{extra_spaces}{re.sub(' +', ' ', output)}"

        def update_prediction():
            list_element.update(values=prediction_list)
            list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)
            self.edittswidow.Refresh()

        def make_prediction(text, index_name='names'):
            prediction_list.clear()
            prediction_ids.clear()

            index = index_name
            index_name = 'serial1' if index_name == 'serials' else index_name[:-1]
            prev_id = ""

            if text:
                cnt = 0  # counter
                index_values = sorted(list(db.db.get_index_values(index)), key=myFunc)
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

        def open_editwindow(it_id):
            if it_id:
                obj = baza.get_by_id(it_id)
                editor = Pages()
                listed_values = self.dict_2_list(obj)
                if len(listed_values) == 14:
                    editor.author = listed_values.pop(1)
                editor.tsdata = listed_values
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
                    make_prediction(values['-IN-'].lower(), active_radio)
                    update_prediction()

            elif event == "-CLOSE-" or event == sg.WIN_CLOSED:
                self.edittswidow.close()
                break

            elif event.startswith('Escape'):
                if values['-IN-']:
                    self.edittswidow['-IN-'].update('')
                    prediction_list, item_id, sel_item = [], "", 0
                    update_prediction()
                else:
                    self.edittswidow.close()
                    break

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
                    make_prediction(values['-IN-'].lower(), active_radio)
                    update_prediction()

            elif event == '-IN-':
                text = values['-IN-'].lower()

                executor.args = lambda: make_prediction(text, active_radio), '-THREAD DONE-'
                executor.start()

            elif event == '-THREAD DONE-':
                sel_item = 0
                update_prediction()

            elif event == '-SHOWALL-':
                output_string = ""
                for elem in sorted(baza.get_unique_index_names('objects')):
                    output_string += f"{elem}\n"
                sg.popup_scrolled(output_string, font=fontbig, title='Все объекты', no_sizegrip=True, size=(30, 20))

            elif event == '-BOX-' and values['-BOX-']:
                sel_item = list_element.TKListbox.curselection()[0]
                item_id = prediction_ids[sel_item]
                open_editwindow(item_id)
                make_prediction(values['-IN-'].lower(), active_radio)
                update_prediction()

            elif event in ("objects", "names", "models", "parts", "vendors", "serials"):
                active_radio = event
                self.edittswidow.write_event_value('-IN-', values['-IN-'])

            elif event == '-EXTRAS-':
                popup_input_text_with_hints('Изменение объекта', 'Изменение объекта')

                self.edittswidow['-IN-'].update("")
                prediction_list, item_id, sel_item = [], "", 0
                update_prediction()

        self.edittswidow.close()

    def word_output_page(self, headername):
        wordlayout = [
            [
                sg.Column([
                    [sg.T("         ")],
                    [sg.T("Экспорт в Word", font=fontbig)],
                    [sg.T("         ")],
                    [sg.Input(size=(listbox_width, 0), enable_events=True, key='-IN-', justification="l",
                              font=fontbig)],
                    [sg.pin(sg.Col(
                        [[sg.Listbox(values=[], size=(listbox_width, listbox_hight), enable_events=True, key='-BOX-',
                                     select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                        key='-BOX-CONTAINER-', pad=(0, 0)))]
                ], justification="c", element_justification="c")
            ],
            [
                sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                        enable_events=True, expand_x=True),
                sg.Button("Методы", key="-METHODS-", font=fontbutton),
                sg.Button("Экспортировать", key="-OPEN-", font=fontbutton),
            ]
        ]

        self.exportwordwindow = sg.Window(headername, wordlayout, resizable=True, return_keyboard_events=True,
                                          element_justification="").Finalize()
        self.exportwordwindow.Maximize()
        if "<Key>" not in self.exportwordwindow.TKroot.bind_all():
            self.exportwordwindow.TKroot.bind_all("<Key>", _onKeyRelease, "+")

        self.exportwordwindow['-IN-'].SetFocus(True)
        list_element: sg.Listbox = self.exportwordwindow.Element('-BOX-')
        list_element.TKListbox.configure(activestyle='none')
        prediction_list, input_text, sel_item = [], "", 0
        choices = sorted(baza.get_unique_index_names('objects'))
        global serial_1, serial_2, stop_animated_thread, animated_thread_work

        while True:
            event, values = self.exportwordwindow.read(timeout=100)

            if event == "-CLOSE-" or event == sg.WIN_CLOSED:
                sg.popup_animated(None)
                self.exportwordwindow.close()
                break

            elif animated_thread_work:
                sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white',
                                  grab_anywhere=False, time_between_frames=100)

            elif stop_animated_thread:
                animated_thread_work, stop_animated_thread = 0, 0
                sg.popup_animated(None)
                popup_yes(f'{values["-IN-"]} экспортирован в Word.\n'
                          f'СЗЗ 1 = {serial_1}\n'f'СЗЗ 2 = {serial_2}\n')
                self.exportwordwindow.enable()

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
                    if elements:
                        for element in elements:
                            if type(element[1]) == dict:
                                items.append(element[1])
                            else:
                                items.append(elements)
                                break
                        return items

                if baza.search_if_exists("$.object", values['-IN-']):
                    level_status = False
                    if popup_yes_no("Экспортировать частично? \n Да - Частично, Нет - Все"):
                        objects = make_listed_items(self.select_items_method(baza.search("$.object", values['-IN-'])))
                    else:
                        objects = make_listed_items(baza.search("$.object", values['-IN-']))

                    if objects:
                        for item_in_list in objects:
                            if item_in_list['table']:
                                level_status = True
                                break

                    if level_status:
                        if popup_yes_no("Выбрать компоненты для заключения?"):
                            conclusion_data = self.set_conclusion_items_page(objects)
                        else:
                            conclusion_data = objects
                    else:
                        conclusion_data = objects

                    if conclusion_data is None:
                        continue

                    export_path = sg.popup_get_folder('export', icon=path_to_icon, no_window=True)

                    if not export_path or export_path is None:
                        continue

                    self.exportwordwindow.disable()
                    animated_thread_work = 1
                    threading.Thread(target=start_word_export, daemon=True,
                                     args=(objects, conclusion_data, export_path, values['-IN-'])).start()

            elif event == "-METHODS-":
                self.exportwordwindow.close()
                self.methods_page()

        self.exportwordwindow.close()

    def import_page(self, headername):
        importlayout = [
            [
                sg.Column([
                    [sg.T("         ")],
                    [sg.T("Импорт и экспорт базы", font=fontbig)],
                    [sg.T("         ")],
                    [sg.Input(size=(listbox_width, 0), enable_events=True, key='-IN-', justification="l",
                              font=fontbig)],
                    [sg.pin(sg.Col(
                        [[sg.Listbox(values=[], size=(listbox_width, listbox_hight), enable_events=True, key='-BOX-',
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

        self.importwindow['-IN-'].SetFocus(True)
        list_element: sg.Listbox = self.importwindow.Element('-BOX-')
        list_element.TKListbox.configure(activestyle='none')
        prediction_list, input_text, sel_item = [], "", 0
        choices = sorted(baza.get_unique_index_names('objects'))

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
                    selected_data = self.select_items_method(objects)
                    if selected_data is not None:
                        path = sg.popup_get_folder('export', no_window=True)
                        if path and path is not None:
                            with open(f"{path}"'/'f"{values['-IN-']}.json", "w") as f:
                                f.truncate(0)
                                json.dump(selected_data, f)
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
                                        item2['object'] = to
                        return temp

                    def search_if_item_in_index(item, index_values):
                        if item and item != "" and item is not None and item != 'б/н':
                            return True if item in index_values else False

                    def duplicate_actions(obj_content, name):
                        full_name = "серийный номер" if name == "part" else "СЗЗ"
                        dub_layout = [
                            sg.Column([
                                [sg.T(f"Найден дубликат: {full_name}:\n", font=fontbig)],
                                [sg.T(str(tabulate(
                                    [["Наименование", obj_content["name"]], ["Модель", obj_content["model"]],
                                     ["Серийный номер", obj_content["part"]], ["Производитель", obj_content["vendor"]],
                                     ["СЗЗ1", obj_content["serial1"]]], numalign="center", stralign="center")),
                                    font=('Consolas', 20))],
                                [sg.T("\nВы хотите добавить его?", font=fontbig)]
                            ], justification='c', element_justification='c')
                        ]
                        pop_answer = popup_yes_no_layouted(dub_layout)
                        if pop_answer:
                            if popup_yes_no(f'Хотите изменить {full_name}?'):
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
                                    save_state = duplicate_actions(obj_body, 'part')

                                if obj_body['table'] and save_state:
                                    for item in obj_body['table']:
                                        if search_if_item_in_index(item['part'], parts_index) and save_state:
                                            save_state = duplicate_actions(item, 'part')

                                        if item['table']:
                                            for item1 in item['table']:
                                                if search_if_item_in_index(item1['part'], parts_index) and save_state:
                                                    save_state = duplicate_actions(item1, 'part')

                                if search_if_item_in_index(obj_body['serial1'], serials_index) and save_state:
                                    save_state = duplicate_actions(obj_body, 'serial1')

                                if obj_body['table'] and save_state:
                                    for item in obj_body['table']:
                                        if search_if_item_in_index(item['serial1'], serials_index) and save_state:
                                            save_state = duplicate_actions(item, 'serial1')

                                        if item['table']:
                                            for item1 in item['table']:
                                                if search_if_item_in_index(item1['serial1'],
                                                                           serials_index) and save_state:
                                                    save_state = duplicate_actions(item1, 'serial1')
                                if save_state:
                                    if values["-IN-"]:
                                        baza.add_dict(change_obj(obj_body, values["-IN-"]), obj_id)
                                    else:
                                        baza.add_dict(obj_body, obj_id)
                                    sg.popup_no_frame(
                                        f'\nИмпортировано:\n'
                                        f'{tabulate([["Наименование", obj_body["name"]], ["Модель", obj_body["model"]], ["Серийный номер", obj_body["part"]], ["Производитель", obj_body["vendor"]], ["СЗЗ1", obj_body["serial1"]]], numalign="center", stralign="center")}',
                                        auto_close_duration=1,
                                        auto_close=True, font=('Consolas', 20), button_type=5)
                            else:
                                existed_item = baza.get_by_id(obj_id)
                                new_item = obj_body
                                new_item_cutted = new_item

                                del existed_item['object']
                                del new_item_cutted['object']

                                existed_list = ['Существующее', existed_item['name'], existed_item['model'],
                                                existed_item['part'],
                                                existed_item['vendor'], existed_item['serial1']]
                                new_list = ['Новое', new_item['name'], new_item['model'], new_item['part'],
                                            new_item['vendor'], new_item['serial1']]
                                if existed_item != new_item_cutted:
                                    lay_test = [
                                        sg.Column([
                                            [sg.T("Импортированное ТС отличается от ТС в базе.\n", font=fontbig)],
                                            [sg.T(str(tabulate([existed_list, new_list],
                                                               headers=['Статус', 'Наименование', 'Модель',
                                                                        'Серийный номер', 'Производитель', 'СЗЗ1'],
                                                               numalign='center', stralign='center')),
                                                  font=('Consolas', 20))],
                                            [sg.T("\nВы хотите изменить его?", font=fontbig)]
                                        ], justification='c', element_justification='c')
                                    ]
                                    existed_answer = popup_yes_no_layouted(lay_test)
                                    if existed_answer:
                                        if values["-IN-"]:
                                            baza.update_element_dict(change_obj(new_item, values["-IN-"]), obj_id)
                                        else:
                                            baza.update_element_dict(new_item, obj_id)
                        popup_yes("Импортирование завершено.")
        self.importwindow.close()

    def select_items_method(self, items_list):
        def Text(text, size, justification, expand_x=None, key=None):
            return sg.Text(text, size=size, pad=(1, 1), expand_x=expand_x, justification=justification, key=key)

        def generate_display_layout(vals):
            # Заполнение текста в фрейме
            try:
                author = vals['author']
            except KeyError:
                author = ""
            text_to_display = \
                f'{vals["name"]} {vals["model"]} {vals["part"]} {vals["vendor"]} {vals["serial1"]} {vals["serial2"]} {author}'
            text_to_display = " ".join(text_to_display.split())
            return [[Text(text_to_display, 95, 'l', True)]]

        def generate_displayed_items(content, text_key):
            # Отображение элементов с чекбоксами
            item_layout = [sg.Checkbox('', font=fontbig, enable_events=True, key=f'{text_key}'),
                           sg.Frame('', generate_display_layout(content), pad=((0, 5), (0, 5)), relief=sg.RELIEF_FLAT)]
            return item_layout

        def generate_frame(object_values, frame_key):
            # Получает 1 Комплект, выводит информацию
            frame_layout = [generate_displayed_items(object_values[1], f'{frame_key}')]
            return sg.Frame(f'', frame_layout, pad=((0, 5), 0))

        column_layout = [
            [generate_frame(content, count)]
            for count, content in enumerate(items_list)
        ]

        layout = [
            [
                sg.Column(
                    [
                        [sg.Button('Далее', k='-NEXT-', font=fontbutton, auto_size_button=True),
                         sg.Button('Выбрать всё', k='-ALL-', font=fontbutton, auto_size_button=True)],
                    ],
                )
            ],
            [
                sg.Column(column_layout, scrollable=True, vertical_scroll_only=False,
                          expand_x=True, expand_y=True, ),
            ],
        ]
        window = sg.Window(f'{items_list[0][1]["object"]}', layout, margins=(10, 10), resizable=True,
                           element_justification='c', font=fontbig, return_keyboard_events=True
                           ).Finalize()
        window.Maximize()

        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, 'Exit'):
                window.close()
                return None
            elif event == '-NEXT-' or event == '\r':
                # check empty, empty is []
                return_data = []
                test_data = deepcopy(items_list)
                keys_with_true_values = [key for key, value in values.items() if value is True]
                for item in keys_with_true_values:
                    selected_item = test_data[int(item)]
                    return_data.append(selected_item)
                if not return_data:
                    popup_yes("Ничего не выбрано.")
                else:
                    window.close()
                    return return_data
            elif event == '-ALL-':
                window.close()
                return items_list

    def set_conclusion_items_page(self, items_list):
        def Text(text, size, justification, expand_x=None, key=None):
            return sg.Text(text, size=size, pad=(1, 1), expand_x=expand_x, justification=justification, key=key)

        def generate_display_layout(vals):
            # Заполнение текста в фрейме
            text_to_display = \
                f'{vals["name"]} {vals["model"]} {vals["part"]} {vals["vendor"]} {vals["serial1"]} {vals["serial2"]}'
            text_to_display = " ".join(text_to_display.split())
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
            try:
                author = object_values["author"]
            except KeyError:
                author = ""

            frame_text = f'{object_values["name"]} {object_values["model"]} {object_values["part"]} ' \
                         f'{object_values["vendor"]} {object_values["serial1"]} {author}'
            frame_text = " ".join(frame_text.split())
            return sg.Frame(frame_text, frame_layout, pad=((0, 5), 0))

        column_layout = [
            [generate_frame(content, count)]
            for count, content in enumerate(items_list)
        ]

        layout = [
            [
                sg.Column(
                    [
                        [sg.Button('Далее', k='-NEXT-', font=fontbutton, auto_size_button=True), ]
                    ],
                )
            ],
            [
                sg.Column(column_layout, scrollable=True, vertical_scroll_only=False,
                          expand_x=True, expand_y=True, ),
            ],
        ]
        window = sg.Window(f'{items_list[0]["object"]}', layout, margins=(10, 10), resizable=True,
                           element_justification='c', font=fontbig, return_keyboard_events=True
                           ).Finalize()
        window.Maximize()

        while True:
            event, values = window.read()
            if event in (sg.WINDOW_CLOSED, 'Exit'):
                window.close()
                return None
            elif event == '-NEXT-' or event == '\r':
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

        def alphabetical_sort(items_ids, items_values):  # gets item_ids, returns sorted list of id and content by name
            sorted_test_values = sorted(items_values, key=lambda x: x[1])
            sorted_test_ids = [items_ids[items_values.index(itm)] for itm in sorted_test_values]
            return sorted_test_ids

        seqlayout = [
            [
                sg.Column([
                    [sg.T("         ")],
                    [sg.T("Изменение последовательности", font=fontbig)],
                    [sg.T("         ")],
                    [sg.pin(sg.Col(
                        [[sg.Listbox(values=test_vals, size=(listbox_width, listbox_hight), enable_events=True,
                                     key='-BOX-',
                                     select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED, no_scrollbar=False, font=fontbig,
                                     horizontal_scroll=True)]],
                        key='-BOX-CONTAINER-', pad=(0, 0)))]
                ], justification="c", element_justification="c")
            ],
            [
                sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                        enable_events=True, expand_x=True),
                sg.Button("Сортировка по алфавиту", key="-ALPHABET-", font=fontbutton),
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

            elif event == '-ALPHABET-':
                re_renumerate_items(alphabetical_sort(test_ids, test_vals))

    def methods_page(self):
        class MethodsActions:
            def __init__(self, method_id=""):
                self.type = None
                self.name = None
                self.methods = None
                self.method_id = method_id

            def save_method(self):
                dict_to_save = {
                    "type": self.type,
                    "name": self.name,
                    "methods": self.methods
                }
                if self.method_id:
                    methods_db.update_element_dict(self.method_id, dict_to_save)
                else:
                    methods_db.add_dict(dict_to_save)

            def get_name_method_by_name(self, current_values):
                for line_id in get_id_content_methods_sorted():
                    if line_id[1]['name'].lower() == current_values['name'].lower() \
                            and line_id[1]['methods'].lower() == current_values['methods_names'].lower():
                        return True

            def open_methods_window(self, header_name="Создание метода"):
                if self.method_id:
                    old_method = methods_db.get_by_id(self.method_id)
                    self.type = old_method['type']
                    self.name = old_method['name']
                    self.methods = old_method['methods']

                method_action_layout = [
                    [
                        sg.Column([
                            [
                                sg.Text('Условие ', font=fontbig),
                                sg.DropDown(values=['По содержанию', 'Точное соответствие'],
                                            default_value="По содержанию" if self.type is None else self.type,
                                            font=fontmid, key='type', readonly=True)],
                            [
                                sg.Text('Наименование ТС ', font=fontbig),
                                sg.InputText(default_text="" if self.name is None else self.name,
                                             font=fontmid, key='name', s=(45, 0), justification='l')
                            ],
                            [
                                sg.Text('Наименование используемых методов ', font=fontbig),
                                sg.InputText(default_text="" if self.methods is None else self.methods,
                                             font=fontmid, key='methods_names', s=(45, 0), justification='l')
                            ], ], justification="c", element_justification="c")
                    ],
                    [
                        sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                                enable_events=True, expand_x=True),
                        sg.Button('Сохранить', key="-SAVE-", font=fontbutton),
                    ]
                ]

                methods_actions_window = sg.Window(header_name, method_action_layout, resizable=True,
                                                   return_keyboard_events=True, element_justification="").Finalize()
                if "<Key>" not in methods_actions_window.TKroot.bind_all():
                    methods_actions_window.TKroot.bind_all("<Key>", _onKeyRelease, "+")
                methods_actions_window['name'].SetFocus(True)

                while True:
                    event, values = methods_actions_window.read()

                    if event == sg.WIN_CLOSED:
                        methods_actions_window.close()
                        break

                    elif event == "-CLOSE-" or event.startswith('Escape'):
                        if self.type == values['type'] and self.name == values['name'] and \
                                self.methods == values['methods_names']:
                            pass
                        elif values['name'] == "" and values['methods_names'] == "":
                            pass
                        else:
                            if not popup_yes_no('Вы уверены что хотите выйти без сохранения?'):
                                continue
                        methods_actions_window.close()
                        break

                    elif event == '-SAVE-':
                        if values['type'] and values['name'] and values['methods_names']:
                            if self.name == values['name'] \
                                    and self.methods == values['methods_names'] \
                                    and not self.method_id:
                                if not popup_yes_no('Вы только что сохранили такой же метод, '
                                                    '\n вы ходите сохранить его повторно (как дубликат)?'):
                                    continue

                            if self.get_name_method_by_name(values) and not self.method_id:
                                if not popup_yes_no('Наименование с такими же методами уже существует в базе, '
                                                    '\n вы ходите сохранить его повторно (как дубликат)?'):
                                    continue

                            self.type = values['type']
                            self.name = values['name']
                            self.methods = values['methods_names']

                            self.save_method()

                            if self.method_id:
                                methods_actions_window.close()

                            popup_yes('Сохранено.')
                        else:
                            popup_yes('Все поля должны быть заполнены!')

        def get_displyed(response):
            if response is not None:
                output = f'{response["name"]} {response["methods"]} {response["type"]}'
                return f"{re.sub(' +', ' ', output)}"

        def display_methods(list_to_display):
            list_element.update(list_to_display)
            list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

        def get_id_content_methods_sorted():
            def sort_by_name(e):
                return e[1]['name'].lower()

            id_content_list = []
            for id_content in iter(db.methods_db):
                id_content_list.append((id_content, methods_db.get_by_id(id_content)))

            return sorted(list(id_content_list), key=sort_by_name)

        def get_all_methods():
            methods_listed = []
            methods_ids_listed = []
            for line in get_id_content_methods_sorted():
                methods_listed.append(get_displyed(line[1]))
                methods_ids_listed.append(line[0])

            display_methods(methods_listed)
            return methods_ids_listed

        def get_methods_by_name(name):
            methods_listed = []
            methods_ids_listed = []
            if self.search_type:
                for methods_id in get_id_content_methods_sorted():
                    if methods_id[1]['name'].lower().__contains__(name):
                        methods_listed.append(get_displyed(methods_id[1]))
                        methods_ids_listed.append(methods_id[0])
            else:
                for methods_id in get_id_content_methods_sorted():
                    if methods_id[1]['name'].lower().startswith(name):
                        methods_listed.append(get_displyed(methods_id[1]))
                        methods_ids_listed.append(methods_id[0])

            display_methods(methods_listed)
            return methods_ids_listed

        methodslayout = [
            [
                sg.Column([
                    [sg.T("         ")],
                    [sg.T("МЕТОДЫ", font=fontbig)],
                    [sg.T("         ")],
                    [sg.Input(size=(listbox_width, 0), enable_events=True, key='-IN-', justification="l",
                              font=fontbig)],
                    [sg.pin(sg.Col(
                        [[sg.Listbox(values=[], size=(listbox_width, listbox_hight), enable_events=True, key='-BOX-',
                                     select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=False, font=fontbig,
                                     horizontal_scroll=True, expand_y=True)]],
                        key='-BOX-CONTAINER-', pad=(0, 0)))],
                ], justification="c", element_justification="c")
            ],
            [
                sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                        enable_events=True, expand_x=True),
                sg.Button('Удалить', key="-DELETE-", font=fontbutton),
                sg.Button('Редактировать', key="-EDIT-", font=fontbutton),
                sg.Button("Создать новый", key="-NEW-", font=fontbutton),
            ]
        ]

        methods_window = sg.Window('Методы', methodslayout, resizable=True, return_keyboard_events=True,
                                   element_justification="").Finalize()
        methods_window.Maximize()
        if "<Key>" not in methods_window.TKroot.bind_all():
            methods_window.TKroot.bind_all("<Key>", _onKeyRelease, "+")

        methods_window['-IN-'].SetFocus(True)
        list_element: sg.Listbox = methods_window.Element('-BOX-')
        list_element.TKListbox.configure(activestyle='none')
        sel_item = 0
        methods_db = db.DataBase(db_name=db.methods_db)
        methods_ids = get_all_methods()

        while True:
            event, values = methods_window.read()

            if event == "-CLOSE-" or event == sg.WIN_CLOSED:
                methods_window.close()
                break

            elif event.startswith('Down') and len(methods_ids):
                sel_item = (sel_item + 1) % len(methods_ids)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event.startswith('Up') and len(methods_ids):
                sel_item = (sel_item + (len(methods_ids) - 1)) % len(methods_ids)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event == '-IN-':
                methods_ids = get_methods_by_name(values['-IN-'].lower())

            elif event == '\r' and len(values['-BOX-']) > 0:
                sel_item = list_element.TKListbox.curselection()[0]
                edited_method = MethodsActions(methods_ids[sel_item])
                edited_method.open_methods_window('Редактирование метода')
                if values['-IN-']:
                    methods_ids = get_methods_by_name(values['-IN-'].lower())
                else:
                    methods_ids = get_all_methods()
                del edited_method

            elif event == '-BOX-' and values['-BOX-']:
                if sel_item == list_element.TKListbox.curselection()[0]:
                    edited_method = MethodsActions(methods_ids[list_element.TKListbox.curselection()[0]])
                    edited_method.open_methods_window('Редактирование метода')
                    if values['-IN-']:
                        methods_ids = get_methods_by_name(values['-IN-'].lower())
                    else:
                        methods_ids = get_all_methods()
                    del edited_method
                else:
                    sel_item = list_element.TKListbox.curselection()[0]

            elif event == '-NEW-':
                new_method = MethodsActions()
                new_method.open_methods_window()
                if values['-IN-']:
                    methods_ids = get_methods_by_name(values['-IN-'].lower())
                else:
                    methods_ids = get_all_methods()
                del new_method

            elif event == '-EDIT-' and values['-BOX-']:
                sel_item = list_element.TKListbox.curselection()[0]
                edited_method = MethodsActions(methods_ids[sel_item])
                edited_method.open_methods_window('Редактирование метода')
                if values['-IN-']:
                    methods_ids = get_methods_by_name(values['-IN-'].lower())
                else:
                    methods_ids = get_all_methods()
                del edited_method

            elif event == '-DELETE-' or event.startswith('Delete') and values['-BOX-']:
                if popup_yes_no(f'Вы действительно хотите удалить метод для "'
                                f'{methods_db.get_by_id(methods_ids[list_element.TKListbox.curselection()[0]])["name"]}'
                                f'"?'):
                    methods_db.delete_by_id(methods_ids[list_element.TKListbox.curselection()[0]])
                    if values['-IN-']:
                        methods_ids = get_methods_by_name(values['-IN-'].lower())
                    else:
                        methods_ids = get_all_methods()


class SpUi:

    def makeui(self):
        pages = Pages()
        eval(f"sg.theme('{db.settings_db['1337']['theme']}')")
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
                    object_name = real_popup_input_text_with_hints('Выбор объекта для изменеия последовательности',
                                                                   "Введите название объекта")
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

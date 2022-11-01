import PySimpleGUI as sg
import db
import MSWord
from copy import deepcopy

NULLLIST = ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
table1, table2 = [], []
last_event = ""
fontbig = ("Arial", 24)
fontbutton = ("Helvetica", 20)
fontmid = ("Arial Baltic", 18)
fontmidlow = ("Arial Baltic", 16)

baza = db.DataBase()
tdb = db.db


class Pages:
    def __init__(self):
        self.window = None
        self.addtswindow = None
        self.addwindow = None
        self.credentialswindow = None
        self.viewwindow = None
        self.addkomerswindow = None
        self.edittswidow = None
        self.exportwordwindow = None

        self.object = None
        self.tsdata = []
        self.tsavailable = ["Комплект", "Составная часть", "Элемент"]
        self.choices_name, self.choices_model, self.choices_part, self.choices_vendor, self.predictions_list = [], [], [], [], []
        self.input_text, self.last_event = '', ''

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
                       )],
            [sg.Button('Экспорт в Word', key="-Export-", enable_events=True,
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
        credentials = [
            [sg.Text('Объект', font=fontbig)],
            [sg.Input(key='-OBJECT-', font=fontbig, enable_events=True, s=(15, 0))],
            [sg.Submit('Дальше', size=(15, 0), button_color='green', font=fontbutton),
             sg.Cancel('Отмена', button_color='red', font=fontbutton)]
        ]
        self.credentialswindow = sg.Window('Выбор объекта', credentials, resizable=True,
                                           element_justification="c")
        self.credentialswindow.Finalize()
        self.credentialswindow['-OBJECT-'].SetFocus(True)
        while True:
            event, values = self.credentialswindow.read()

            if event == "Дальше":
                if values['-OBJECT-'] != '':
                    self.object = values["-OBJECT-"]
                    self.credentialswindow.close()
                    return 1
                else:
                    self.credentialswindow["-OBJECT-"].Update("")
                    sg.Window('Ошибочка',
                              [[sg.T('Заполните поле!', font=fontbig)], [sg.Button('Понял', font=fontbutton)]],
                              element_justification="c", no_titlebar=True, size=(400, 100), auto_close=True,
                              auto_close_duration=5).read(close=True)

            elif event in ('Отмена', sg.WIN_CLOSED):
                self.credentialswindow.close()
                return 0

    def addtspage(self, master, headername, ts_id=None):
        global table1, table2
        window_saved = False
        sel_item = 0
        headings = ['Объект', 'Наим.', 'Модель', 'S/N', 'Произв.', 'С1', 'С2', 'Кол-во', 'УФ', 'РГГ', 'РГГ пп',
                    'П', 'Состав']
        col_widths = list(map(lambda x: len(x) + 2, headings))  # find the widths of columns in character.
        # tabledata = [NULLLIST, ]
        tabledata = []
        addtspage = [
            [sg.Column(
                [[sg.Text('Объект', font=fontmid), sg.InputText(key='object', default_text=self.object, disabled=True,
                                                                s=(7, 5), text_color="black", font=fontmidlow)]]
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
             sg.Button("Удалить из БД", k="bd_delete", font=fontbutton, visible=False),
             sg.Button("Сохранить", k="_SAVE_", font=fontbutton),
             sg.Button("Новое ТС", font=fontbutton),
             ]
        ]
        self.addtswindow = sg.Window(headername, addtspage, resizable=True, return_keyboard_events=True,
                                     element_justification="").Finalize()
        self.addtswindow.Maximize()
        self.addtswindow['name'].SetFocus(True)
        self.get_choices()

        char_width = sg.Text.char_width_in_pixels(fontmidlow)
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

        if master == "editor":
            self.fun_vieweditor()
            table.Update(self.tsdata[12])
            if self.tsavailable == ["Комплект", "Составная часть", "Элемент"]:
                table1 = self.tsdata[12]
            if self.tsavailable == ["Составная часть", "Элемент"]:
                table2 = self.tsdata[12]
            self.last_event = "name"
            if ts_id is not None:
                self.addtswindow["bd_delete"].Update(visible=True)

        if master == True:
            self.addtswindow['_SAVE_'].Update('Добавить в БД')

        def make_predictions(index, container):
            choices = eval(f"self.choices_{index}")
            text = values[index].lower()
            if text == self.input_text:
                pass
            else:
                self.input_text = text
                self.predictions_list = []
                if text:
                    self.predictions_list = [item for item in choices if item.lower().__contains__(text)]

                list_element.update(values=self.predictions_list)
                sel_item = 0
                list_element.update(set_to_index=sel_item)

            if len(self.predictions_list) > 0:
                self.addtswindow[container].update(visible=True)
            else:
                self.addtswindow[container].update(visible=False)
                self.addtswindow[f'-BOX{index}-'].update('')

        event_list = ['name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'amount', 'rgg', 'rggpp']

        while True:
            event, values = self.addtswindow.read()

            if event == sg.WIN_CLOSED:
                self.addtswindow.close()
                if self.tsavailable == ["Комплект", "Составная часть", "Элемент"]:
                    table1.clear()
                else:
                    table2.clear()
                break

            elif event == "-CloseAddTsPage-" or event.startswith('Escape'):
                if values["level"] == "Комплект" and not master:
                    table1.clear()
                if values["level"] == "Составная часть" and not master:
                    table2.clear()
                if not window_saved:
                    if not sg.PopupYesNo("Уверены что хотите выйти без сохранения?", auto_close_duration=7,
                                         auto_close=True) == "Yes":
                        continue
                self.addtswindow.close()
                break

            elif event.startswith('Down') and len(self.predictions_list):
                sel_item = (sel_item + 1) % len(self.predictions_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event.startswith('Up') and len(self.predictions_list):
                sel_item = (sel_item + (len(self.predictions_list) - 1)) % len(self.predictions_list)
                list_element.update(set_to_index=sel_item, scroll_to_index=sel_item)

            elif event == '\r':
                if self.last_event:
                    if len(values[f'-BOX{self.last_event}-']) > 0:
                        self.addtswindow[self.last_event].update(value=values[f'-BOX{self.last_event}-'][0])
                        self.addtswindow[f'-CONTAINER{self.last_event}-'].update(visible=False)

                get_focused_elementname = self.addtswindow.find_element_with_focus().Key
                self.addtswindow[event_list[0 if get_focused_elementname == 'rggpp' else event_list.index(
                    get_focused_elementname) + 1]].SetFocus(True)

            elif event in ('name', 'model', 'part', 'vendor'):
                self.last_event = event
                list_element: sg.Listbox = self.addtswindow.Element(f'-BOX{event}-')
                make_predictions(event, f'-CONTAINER{event}-')

            elif event == "level" and not master == "slave":
                if values[event] == "Комплект" or values[event] == "Составная часть":
                    self.addtswindow["-ADDMORE-"].update(visible=True)
                    self.addtswindow["-TABLE-"].update(visible=True)
                else:
                    self.addtswindow["-ADDMORE-"].update(visible=False)
                    self.addtswindow["-TABLE-"].update(visible=False)

            elif event == "-ADDMORE-":
                window_saved = False
                # вызов нового окна, обработка его возращаемного значения и добавление в таблицу
                page2 = Pages()
                page3 = Pages()

                def replace_bool(input_data):
                    for i in input_data:
                        i[8] = str(i[8])
                    return input_data

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
                    if total == 0:
                        return 300
                    return total * char_width

                if values["level"] == "Комплект":
                    page2.tsavailable = ["Составная часть", "Элемент"]
                    page2.object = self.object

                    page2.addtspage(master=False, headername="Добавление 2-го уровня")

                    data = replace_bool(table1)
                    all_data = [headings] + data
                    col_widths = [min([max(map(len, columns)), 30]) * char_width for columns in
                                  zip(*all_data)]
                    col_widths[12] = count_char_length(data)

                    headerwidth = 0
                    temp_col = []
                    for item in col_widths:
                        headerwidth += item
                    w, v = self.addtswindow.get_screen_dimensions()
                    if w > headerwidth:
                        resize = w - headerwidth
                        resize = int(resize / 13) + 8
                        for cols in col_widths:
                            cols = cols + resize
                            temp_col.append(cols)
                        col_widths.clear()
                        col_widths = temp_col.copy()

                    table.update(values=table1)

                    for cid in headings:
                        table_widget.column(cid, stretch=False)

                    for cid, width in zip(headings, col_widths):
                        table_widget.column(cid, width=width)

                else:
                    page3.tsavailable = ["Элемент"]
                    page3.object = self.object

                    page3.addtspage(master=False, headername="Добавление 3-го уровня")

                    data = replace_bool(table2)
                    all_data = [headings] + data
                    col_widths = [min([max(map(len, columns)), 30]) * char_width for columns in
                                  zip(*all_data)]
                    col_widths[12] = count_char_length(data)

                    headerwidth = 0
                    temp_col = []
                    for item in col_widths:
                        headerwidth += item
                    w, v = self.addtswindow.get_screen_dimensions()
                    if w > headerwidth:
                        resize = w - headerwidth
                        resize = int(resize / 13) + 8
                        for cols in col_widths:
                            cols = cols + resize
                            temp_col.append(cols)
                        col_widths.clear()
                        col_widths = temp_col.copy()

                    table.update(values=table2)

                    for cid in headings:
                        table_widget.column(cid, stretch=False)

                    for cid, width in zip(headings, col_widths):
                        table_widget.column(cid, width=width)

            elif event == "nopart":
                if values[event]:
                    self.addtswindow["part"].update("б/н", disabled=True)
                else:
                    self.addtswindow["part"].update("", disabled=False)

            elif event == "_SAVE_":
                if master in ('slave', 'editor'):
                    self.tsdata = self.get_tsvalues(values)

                elif master == True:  # ♂oh shit im sorry♂
                    if values['name'] or values['model'] or values['part'] or values['vendor']:
                        baza.add(self.get_tsvalues(values))
                        sg.popup_no_frame(f'"{values["name"]}" добавлено в базу.', auto_close_duration=1,
                                          auto_close=True, font=fontbig, button_type=5)

                else:
                    if self.tsavailable == ["Составная часть", "Элемент"]:
                        self.insert_values_into_table(self.get_tsvalues(values), table1)
                    if self.tsavailable == ["Элемент"]:
                        self.insert_values_into_table(self.get_tsvalues(values), table2)
                    sg.popup_no_frame(f'"{values["name"]}" добавлен.', auto_close_duration=1,
                                      auto_close=True, font=fontbig, button_type=5)
                window_saved = True

            elif event == "Новое ТС":
                whitelist = ['object', 'serial2', 'level', '-TABLE-', 'nopart', 'amount']
                savelist = ['name', 'model', 'part', 'vendor', 'serial1', 'rgg']
                rmlist = []
                window_saved = False

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
                if values['level'] == "Комплект":
                    slave.tsavailable = ["Составная часть", "Элемент"]
                else:
                    slave.tsavailable = ["Элемент"]

                if master == "editor":
                    slave.addtspage(master="editor", headername="Редактирование элемента")
                else:
                    slave.addtspage(master="slave", headername="Редактирование элемента")

                if slave.tsavailable == ["Составная часть", "Элемент"]:
                    table1[pos] = slave.tsdata
                    table.Update(table1)
                if slave.tsavailable == ["Элемент"]:
                    table2[pos] = slave.tsdata
                    table.Update(table2)

            elif event == "bd_delete":
                if sg.PopupYesNo("Уверены что хотите удалить? ", auto_close_duration=7, auto_close=True) == "Yes":
                    baza.delete_by_id(ts_id)
                    self.addtswindow.close()

    def fun_slave(self):
        allnames = ['object', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'amount', 'uv',
                    'rgg', 'rggpp', 'level', '-TABLE-']
        hideitems = ['nameSAVE', 'modelSAVE', 'partSAVE', 'nopart', 'vendorSAVE', 'serial1SAVE', 'rggSAVE', 'Новое ТС']
        for element in hideitems:
            self.addtswindow[element].Update(visible=False)
        for element, toput in zip(allnames, self.tsdata):
            self.addtswindow[element].update(toput)

    def get_choices(self):
        self.choices_name = baza.get_unique_index_names('names')
        self.choices_part = baza.get_unique_index_names('parts')
        self.choices_model = baza.get_unique_index_names('models')
        self.choices_vendor = baza.get_unique_index_names('vendors')

    def fun_vieweditor(self):
        allnames = ['object', 'name', 'model', 'part', 'vendor', 'serial1', 'serial2', 'amount', 'uv',
                    'rgg', 'rggpp', 'level', '-TABLE-']
        hideitems = ['nameSAVE', 'modelSAVE', 'partSAVE', 'vendorSAVE', 'serial1SAVE', 'rggSAVE', 'Новое ТС']
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
                                     select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, no_scrollbar=True, font=fontbig)]],
                        key='-BOX-CONTAINER-', pad=(0, 0)))]
                ], justification="c", element_justification="c")
            ],
            [
                sg.Text('Назад', key="-CLOSE-", font=fontbutton, justification='l',
                        enable_events=True, expand_x=True),
                sg.Submit("Открыть", key="-OPEN-", font=fontbutton),
            ]
        ]

        self.edittswidow = sg.Window(headername, editlayout, resizable=True, return_keyboard_events=True,
                                     element_justification="").Finalize()
        self.edittswidow.Maximize()

        list_element: sg.Listbox = self.edittswidow.Element('-BOX-')
        prediction_list, prediction_ids, input_text, sel_item = [], [], "", 0

        while True:
            event, values = self.edittswidow.read()

            if event == "-OPEN-" and values["-IN-"]:
                if prediction_ids:
                    obj = baza.get_by_id(prediction_ids[sel_item])
                    editor = Pages()
                    editor.tsdata = self.dict_2_list(obj)
                    editor.object = editor.tsdata[0]
                    editor.addtspage(master="editor", headername="Редактирование и просмотр ТС",
                                     ts_id=prediction_ids[sel_item])
                    if baza.search_by_id_if_exists(prediction_ids[sel_item]):
                        baza.update_element(prediction_ids[sel_item], editor.tsdata)
                    table1.clear()
                    table2.clear()
                    for radio in ("objects", "names", "models", "parts", "vendors", "serials"):
                        if values[radio]:
                            choices = baza.get_index_names(radio)
                            choices.sort(key=myFunc)
                    prediction_list = [f"{item[1]} {baza.get_display_values(item[0])}"
                                       for item in choices if
                                       item[1].lower().__contains__(values['-IN-'].lower())]  # text
                    prediction_ids = [item[0] for item in choices if
                                      item[1].lower().__contains__(values['-IN-'].lower())]  # ids
                    list_element.update(values=prediction_list)
                    sel_item = 0
                    list_element.update(set_to_index=sel_item)

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
                    self.edittswidow['-IN-'].update(value=values['-BOX-'])
            elif event == '-IN-':
                text = values['-IN-'].lower()
                if text == input_text:
                    continue
                else:
                    input_text = text
                prediction_list = []
                prediction_ids = []
                if text:
                    prediction_list = [f"{item[1]} {baza.get_display_values(item[0])}"
                                       for item in choices if item[1].lower().__contains__(text)]  # text
                    prediction_ids = [item[0] for item in choices if item[1].lower().__contains__(text)]  # ids

                list_element.update(values=prediction_list)
                sel_item = 0
                list_element.update(set_to_index=sel_item)

            elif event == '-BOX-':
                self.edittswidow['-IN-'].update(value=values['-BOX-'])

            elif event in ("objects", "names", "models", "parts", "vendors", "serials"):
                choices = baza.get_index_names(event)
                choices.sort(key=myFunc)

        self.edittswidow.close()

    def word_output_page(self, headername):
        mswordlib = MSWord.Word()
        editlayout = [
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

        self.exportwordwindow = sg.Window(headername, editlayout, resizable=True, return_keyboard_events=True,
                                          element_justification="").Finalize()
        self.exportwordwindow.Maximize()
        list_element: sg.Listbox = self.exportwordwindow.Element('-BOX-')
        prediction_list, prediction_ids, input_text, sel_item = [], [], "", 0
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
            elif event == '-IN-':
                text = values['-IN-'].lower()
                if text == input_text:
                    continue
                else:
                    input_text = text
                prediction_list = []
                if text:
                    prediction_list = [item for item in choices if item.lower().__contains__(text)]  # text

                list_element.update(values=prediction_list)
                sel_item = 0
                list_element.update(set_to_index=sel_item)

            if event == '-OPEN-' and values["-IN-"]:
                if baza.search_if_exists("$.object", values['-IN-']):
                    objects = baza.search("$.object", values['-IN-'])
                    mswordlib.act_table(objects, f"АКТ {values['-IN-']}")
                    mswordlib.conclusion_table(objects, f"ЗАКЛЮЧЕНИЕ {values['-IN-']}")
                    mswordlib.methods_table(objects, f"МЕТОДЫ {values['-IN-']}")
                    mswordlib.ims_table(objects, f"СПИСОК ИМС {values['-IN-']}")

        self.exportwordwindow.close()


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

            elif event == sg.WIN_CLOSED:
                break

        pages.window.close()

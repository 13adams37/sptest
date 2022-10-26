import docx

nonBreakSpace = u'\xa0'


def row_count(obj):
    length = 0
    if type(obj) == list:
        for element in obj:
            length += 1
            if len(element[1]['table']):
                length += len(element[1]['table'])
                if len(element[1]['table']):
                    for i in element[1]['table']:
                        length += len(i['table'])
    else:
        length += 1
        if len(obj['table']):
            length += len(obj['table'])
            if len(obj['table']):
                for i in obj['table']:
                    length += len(i['table'])
    return length


def editcell(table, r, c, text):
    cell = table.cell(r, c)
    cell.text = str(text)


def prep(elmtor):
    elmt = elmtor.copy()
    if elmt['part'] not in ("", "б/н"):
        elmt['part'] = f"№{nonBreakSpace}{elmt['part']}"
    return f"{elmt['name']} {elmt['vendor']} {elmt['model']} {elmt['part']}"


class Word:
    def __init__(self):
        pass

    def act_table(self, elements, output_name):
        doc = docx.Document()

        print(row_count(elements))
        rows = row_count(elements)

        # добавляем таблицу
        table = doc.add_table(rows=rows, cols=10)
        # применяем стиль для таблицы
        table.style = 'Table Grid'

        row = -1
        while row != rows or row <= rows:
            items = []
            for item in elements:
                item = item[1]
                if type(item) == dict:
                    items.append(item)
                else:
                    items.append(elements)
                    break
            counter = 0
            for item in items:
                print(item)
                counter += 1
                row += 1
                editcell(table, row, 0, counter)
                editcell(table, row, 1, item['name'])
                editcell(table, row, 2, item['model'])
                editcell(table, row, 3, item['part'])
                editcell(table, row, 4, item['vendor'])
                editcell(table, row, 5, item['amount'])
                # editcell(table, row, 5, '1')  # test
                editcell(table, row, 6, item['serial1'])

                if item['uv']:
                    editcell(table, row, 7, "УФ")
                else:
                    editcell(table, row, 7, item['serial2'])

                editcell(table, row, 8, 'CC')
                editcell(table, row, 9, '2')

                if item['table']:
                    for item1 in item['table']:
                        print(item1)
                        row = row + 1
                        editcell(table, row, 1, item1['name'])
                        editcell(table, row, 2, item1['model'])
                        editcell(table, row, 3, item1['part'])
                        editcell(table, row, 4, item1['vendor'])
                        editcell(table, row, 5, item['amount'])
                        # editcell(table, row, 5, '1')  # test
                        editcell(table, row, 6, item1['serial1'])

                        if item1['uv']:
                            editcell(table, row, 7, "УФ")
                        else:
                            editcell(table, row, 7, item1['serial2'])

                        editcell(table, row, 8, 'CC')
                        editcell(table, row, 9, '2')

                        if item1['table']:
                            for item2 in item1['table']:
                                print(item2)
                                row = row + 1
                                editcell(table, row, 1, item2['name'])
                                editcell(table, row, 2, item2['model'])
                                editcell(table, row, 3, item2['part'])
                                editcell(table, row, 4, item2['vendor'])
                                # editcell(table, row, 5, '1')  # test
                                editcell(table, row, 5, item['amount'])
                                editcell(table, row, 6, item2['serial1'])

                                if item2['uv']:
                                    editcell(table, row, 7, "УФ")
                                else:
                                    editcell(table, row, 7, item2['serial2'])

                                editcell(table, row, 8, 'CC')
                                editcell(table, row, 9, '2')
            break
        doc.save(f'{output_name}.docx')

    def methods_table(self, elements, output_name):
        doc = docx.Document()

        print(row_count(elements))
        rows = row_count(elements)

        # добавляем таблицу
        table = doc.add_table(rows=rows, cols=4)
        # применяем стиль для таблицы
        table.style = 'Table Grid'

        row = -1
        while row != rows or row <= rows:
            items = []
            for item in elements:
                item = item[1]
                if type(item) == dict:
                    items.append(item)
                else:
                    items.append(elements)
                    break

            counter = 0
            for item in items:
                subcount = 0
                counter += 1
                row += 1
                editcell(table, row, 0, counter)
                editcell(table, row, 1, prep(item))

                if item['table']:
                    for item1 in item['table']:
                        subsubcount = 0
                        subcount += 1
                        row += 1
                        editcell(table, row, 0, f"{counter}.{subcount}")
                        editcell(table, row, 1, prep(item1))

                        if item1['table']:
                            for item2 in item1['table']:
                                subsubcount += 1
                                row += 1
                                editcell(table, row, 0, f"{counter}.{subcount}.{subsubcount}")
                                editcell(table, row, 1, prep(item2))
            break
        doc.save(f'{output_name}.docx')

    def conclusion_table(self, elements, output_name):
        doc = docx.Document()

        print(row_count(elements))
        rows = row_count(elements)

        # добавляем таблицу
        table = doc.add_table(rows=rows, cols=10)
        # применяем стиль для таблицы
        table.style = 'Table Grid'

        row = -1
        while row != rows or row <= rows:
            items = []
            for item in elements:
                item = item[1]
                if type(item) == dict:
                    items.append(item)
                else:
                    items.append(elements)
                    break

            counter = 0
            # serialscounter = 0
            for item in items:
                serialscounter = 0
                counter += 1
                row += 1
                editcell(table, row, 0, counter)
                editcell(table, row, 1, item['name'])
                editcell(table, row, 2, item['model'])
                editcell(table, row, 3, item['part'])
                editcell(table, row, 4, item['vendor'])
                editcell(table, row, 5, '1')  # test
                editcell(table, row, 6, item['serial1'])

                if item['serial2']:
                    serialscounter += int(item['serial2'])

                editcell(table, row, 8, 'CC')
                editcell(table, row, 9, '2')

                if item['table']:
                    for item1 in item['table']:
                        if item1['serial2']:
                            serialscounter += int(item1['serial2'])

                        if item1['table']:
                            for item2 in item1['table']:
                                if item2['serial2']:
                                    serialscounter += int(item2['serial2'])

                editcell(table, row, 7, serialscounter)
                row += 1
            break
        doc.save(f'{output_name}.docx')

    def ims_table(self, elements, output_name):
        doc = docx.Document()

        print(row_count(elements))
        rows = row_count(elements)

        # добавляем таблицу
        table = doc.add_table(rows=rows, cols=5)
        # применяем стиль для таблицы
        table.style = 'Table Grid'

        row = -1
        while row != rows or row <= rows:
            items = []
            for item in elements:
                item = item[1]
                if type(item) == dict:
                    items.append(item)
                else:
                    items.append(elements)
                    break

            counter = 0
            for item in items:
                row += 1
                counter += 1
                editcell(table, row, 0, counter)
                editcell(table, row, 1, prep(item))
                editcell(table, row, 3, item['rgg'])
                editcell(table, row, 4, item['rggpp'])

                if item['table']:
                    for item1 in item['table']:
                        row += 1
                        editcell(table, row, 1, prep(item1))
                        editcell(table, row, 3, item1['rgg'])
                        editcell(table, row, 4, item1['rggpp'])

                        if item1['table']:
                            for item2 in item1['table']:
                                row += 1
                                editcell(table, row, 1, prep(item2))
                                editcell(table, row, 3, item2['rgg'])
                                editcell(table, row, 4, item2['rggpp'])
            break
        doc.save(f'{output_name}.docx')


if __name__ == '__main__':
    headers = ["№ п/п", "Наименование ОП", "Модель (тип)", "Заводской номер", "Фирма производитель", "Кол-во", "СЗЗ-1",
               "СЗЗ-2", "СС", "КП"]
    mylist = ['multi', 'Системный блок', 'KCAS-13', '148001', 'POWERCOOL', '1337555', '', False, '', '', '', 'Комплект',
              [['multi', 'материнка', 'b450m-re', 'AKB450M000137', 'ASUS', '', '1', False, '', '', '',
                'Составная часть',
                [['multi', 'проц', 'i7-4700k', '00148', 'Intel', '', '', True, '', '', '', 'Элемент', []]]],
               ['multi', 'SSD', 'ARC-100', '', 'OCZ', '', '', False, '', '', '', 'Составная часть', []],
               ['multi', 'БП', 'R450M', '', 'AEROCOOL', '', '', False, '', '', '', 'Составная часть',
                [['multi', 'плата', '', '', '', '', '', False, '', '', '', 'Элемент', []]]],
               ['multi', 'вентилятор корпуса', 'SA-143', '', 'DEEPCOOL', '', '1', False, '', '', '', 'Элемент', []]]]
    mydict00 = {'object': 'multi', 'name': 'Системный блок', 'model': 'KCAS-13', 'part': '148001',
                'vendor': 'POWERCOOL',
                'serial1': '1337555', 'serial2': '', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '',
                'level': 'Комплект', 'table': [
            {'object': 'multi', 'name': 'материнка', 'model': 'b450m-re', 'part': 'AKB450M000137', 'vendor': 'ASUS',
             'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '',
             'level': 'Составная часть', 'table': [
                {'object': 'multi', 'name': 'проц', 'model': 'i7-4700k', 'part': '00148', 'vendor': 'Intel',
                 'serial1': '', 'serial2': '', 'uv': True, 'folder': '', 'rgg': '', 'rggpp': '', 'level': 'Элемент',
                 'table': []}]},
            {'object': 'multi', 'name': 'SSD', 'model': 'ARC-100', 'part': '', 'vendor': 'OCZ', 'serial1': '',
             'serial2': '', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '', 'level': 'Составная часть', 'table': []},
            {'object': 'multi', 'name': 'БП', 'model': 'R450M', 'part': '', 'vendor': 'AEROCOOL', 'serial1': '',
             'serial2': '', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '', 'level': 'Составная часть', 'table': [
                {'object': 'multi', 'name': 'плата', 'model': '', 'part': '', 'vendor': '', 'serial1': '',
                 'serial2': '', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '', 'level': 'Элемент', 'table': []}]},
            {'object': 'multi', 'name': 'вентилятор корпуса', 'model': 'SA-143', 'part': '', 'vendor': 'DEEPCOOL',
             'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '', 'level': 'Элемент',
             'table': []}]}
    mydict11 = {'object': 'ИК3 РТ', 'name': 'Системный блок', 'model': 'Kraftway idea KR54', 'part': '0011030581',
                'vendor': 'ЗАО "Крафтвей корпорейшн ПЛС"', 'serial1': '13105932', 'serial2': '', 'uv': False,
                'folder': '', 'rgg': '', 'rggpp': '00(1)', 'level': 'Комплект', 'table': [
            {'object': 'ИК3 РТ', 'name': 'Материнская плата', 'model': 'H410MS2V2', 'part': '21260072085', 'vendor': '',
             'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '',
             'level': 'Составная часть', 'table': [
                {'object': 'ИК3 РТ', 'name': 'ОЗУ', 'model': 'R744G2400U1SU0', 'part': '', 'vendor': 'AMD',
                 'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '00 (3)',
                 'level': 'Элемент', 'table': []},
                {'object': 'ИК3 РТ', 'name': 'ПАК "Соболь"', 'model': 'RU.40308570.501410.001', 'part': 'KVULGG2H',
                 'vendor': 'Код безопасности', 'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '',
                 'rggpp': '00 (2)', 'level': 'Элемент', 'table': []},
                {'object': 'ИК3 РТ', 'name': 'Процессор', 'model': 'G6405', 'part': 'X112L796 02101', 'vendor': 'Intel',
                 'serial1': '', 'serial2': '1', 'uv': True, 'folder': '', 'rgg': '', 'rggpp': '01', 'level': 'Элемент',
                 'table': []}]},
            {'object': 'ИК3 РТ', 'name': 'Вентилятор процессора', 'model': 'E97379-003', 'part': 'CNSH0485R5',
             'vendor': 'Videc', 'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '',
             'level': 'Элемент', 'table': []},
            {'object': 'ИК3 РТ', 'name': 'DVD Writer', 'model': 'SH-222', 'part': 'R8BZ6GFB523531', 'vendor': '',
             'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '',
             'level': 'Составная часть', 'table': [
                {'object': 'ИК3 РТ', 'name': 'Блок лазера', 'model': '94V-OH', 'part': 'б/н', 'vendor': '',
                 'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '03 (1)',
                 'level': 'Элемент', 'table': []},
                {'object': 'ИК3 РТ', 'name': 'Плата', 'model': 'BG41-00618A', 'part': 'б/н', 'vendor': '',
                 'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '03 (2)',
                 'level': 'Элемент', 'table': []},
                {'object': 'ИК3 РТ', 'name': 'Плата электродвигателя', 'model': 'BG41-00619A', 'part': 'б/н',
                 'vendor': '', 'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '03 (3)',
                 'level': 'Элемент', 'table': []}]},
            {'object': 'ИК3 РТ', 'name': 'Вентилятор корпуса', 'model': 'PLA12025S12L', 'part': 'б/н',
             'vendor': 'Gladiacal Tech', 'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '',
             'rggpp': '', 'level': 'Элемент', 'table': []},
            {'object': 'ИК3 РТ', 'name': 'Блок питания', 'model': 'UN450', 'part': 'б/н', 'vendor': 'ExeGate',
             'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '',
             'level': 'Составная часть', 'table': [
                {'object': 'ИК3 РТ', 'name': 'Плата БП', 'model': '', 'part': 'б/н', 'vendor': '', 'serial1': '',
                 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '02 (1)', 'level': 'Элемент',
                 'table': []},
                {'object': 'ИК3 РТ', 'name': 'Вентилятор БП', 'model': 'BDM12025S', 'part': 'б/н', 'vendor': '',
                 'serial1': '', 'serial2': '1', 'uv': False, 'folder': '', 'rgg': '', 'rggpp': '02 (2)',
                 'level': 'Элемент', 'table': []}]}]}
    # doc = docx.Document()
    mydictstack = []


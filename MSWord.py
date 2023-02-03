import re
from copy import deepcopy

import docx

nonBreakSpace = u'\xa0'


def row_count(obj):
    length = 0
    if type(obj) == list:
        for element in obj:
            length += 1
            if len(element['table']):
                length += len(element['table'])
                if len(element['table']):
                    for i in element['table']:
                        length += len(i['table'])
    return length


def empty_serial(serial):
    if not serial:
        return "–"
    else:
        return serial


def editcell(table, r, c, text):
    cell = table.cell(r, c)
    cell.text = str(text)


def prep(elmtor):
    elmt = elmtor.copy()
    if elmt['part'] not in ("", "б/н"):
        elmt['part'] = f"№{nonBreakSpace}{elmt['part']}"
    output = f"{elmt['name']} {elmt['vendor']} {elmt['model']} {elmt['part']}"
    return f"{re.sub(' +', ' ', output)}"


class Word:
    def __init__(self):
        self.serial1_count = 0
        self.serial2_count = 0

    def act_table(self, elements, output_name):
        doc = docx.Document()
        rows = row_count(elements)
        table = doc.add_table(rows=rows, cols=10)
        table.style = 'Table Grid'

        row = -1
        while row != rows or row <= rows:
            counter = 0
            for item in elements:
                counter += 1
                row += 1
                editcell(table, row, 0, counter)
                editcell(table, row, 1, item['name'])
                editcell(table, row, 2, item['model'])
                editcell(table, row, 3, item['part'])
                editcell(table, row, 4, item['vendor'])
                editcell(table, row, 5, item['amount'])
                editcell(table, row, 6, empty_serial(item['serial1']))

                if item['uv']:
                    editcell(table, row, 7, "УФ")
                else:
                    editcell(table, row, 7, empty_serial(item['serial2']))

                editcell(table, row, 8, 'CC')
                editcell(table, row, 9, '2')

                if item['table']:
                    for item1 in item['table']:
                        row = row + 1
                        editcell(table, row, 1, item1['name'])
                        editcell(table, row, 2, item1['model'])
                        editcell(table, row, 3, item1['part'])
                        editcell(table, row, 4, item1['vendor'])
                        editcell(table, row, 5, item1['amount'])
                        editcell(table, row, 6, empty_serial(item1['serial1']))

                        if item1['uv']:
                            editcell(table, row, 7, "УФ")
                        else:
                            editcell(table, row, 7, empty_serial(item1['serial2']))

                        editcell(table, row, 8, 'CC')
                        editcell(table, row, 9, '2')

                        if item1['table']:
                            for item2 in item1['table']:
                                row = row + 1
                                editcell(table, row, 1, item2['name'])
                                editcell(table, row, 2, item2['model'])
                                editcell(table, row, 3, item2['part'])
                                editcell(table, row, 4, item2['vendor'])
                                editcell(table, row, 5, item2['amount'])
                                editcell(table, row, 6, empty_serial(item2['serial1']))

                                if item2['uv']:
                                    editcell(table, row, 7, "УФ")
                                else:
                                    editcell(table, row, 7, empty_serial(item2['serial2']))

                                editcell(table, row, 8, 'CC')
                                editcell(table, row, 9, '2')
            break
        doc.save(f'{output_name}.docx')

    def methods_table(self, elements, output_name):
        doc = docx.Document()
        rows = row_count(elements)
        table = doc.add_table(rows=rows, cols=4)
        table.style = 'Table Grid'
        row = -1

        while row != rows or row <= rows:
            counter = 0
            for item in elements:
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
        rows = row_count(elements)
        table = doc.add_table(rows=rows, cols=10)
        table.style = 'Table Grid'
        row = -1
        self.serial1_count = 0
        self.serial2_count = 0

        while row != rows or row <= rows:
            counter = 0
            for item in elements:
                serialscounter = 0
                counter += 1
                row += 1
                object_row = deepcopy(row)
                editcell(table, row, 0, counter)
                editcell(table, row, 1, item['name'])
                editcell(table, row, 2, item['model'])
                editcell(table, row, 3, item['part'])
                editcell(table, row, 4, item['vendor'])
                editcell(table, row, 5, item['amount'])
                editcell(table, row, 6, empty_serial(item['serial1']))

                self.serial1_count += 1 if item['serial1'] else 0

                if item['serial2']:
                    serialscounter += int(item['serial2'])

                editcell(table, row, 8, 'CC')
                editcell(table, row, 9, '2')

                if item['table']:
                    subcounter = 0
                    for item1 in item['table']:
                        try:
                            if item1['selected']:
                                subcounter += 1
                                row += 1
                                level2serial = 0

                                editcell(table, row, 0, f"{counter}.{subcounter}")
                                editcell(table, row, 1, item1['name'])
                                editcell(table, row, 2, item1['model'])
                                editcell(table, row, 3, item1['part'])
                                editcell(table, row, 4, item1['vendor'])
                                editcell(table, row, 5, item1['amount'])
                                editcell(table, row, 6, empty_serial(item1['serial1']))
                                editcell(table, row, 8, 'CC')
                                editcell(table, row, 9, '2')

                                if item1['table']:
                                    for it2 in item1['table']:
                                        if it2['serial2'] and not it2['uv']:
                                            level2serial += int(it2['serial2'])

                                if item1['serial2'] and not item1['uv']:
                                    editcell(table, row, 7, int(item1['serial2'] + level2serial))
                                else:
                                    editcell(table, row, 7, "ERROR")

                                self.serial1_count += 1 if item1['serial1'] else 0
                                self.serial2_count += int(item1['serial2'] + level2serial)
                                continue  # ?????
                        except KeyError:
                            if item1['serial2']:
                                serialscounter += int(item1['serial2'])

                        if item1['table']:
                            subsubcounter = 0
                            for item2 in item1['table']:
                                try:
                                    if item2['selected']:
                                        subsubcounter += 1
                                        row += 1
                                        if subcounter > 0:
                                            editcell(table, row, 0, f"{counter}.{subcounter}.{subsubcounter}")
                                        else:
                                            editcell(table, row, 0, f"{counter}.{subsubcounter}")
                                        editcell(table, row, 1, item2['name'])
                                        editcell(table, row, 2, item2['model'])
                                        editcell(table, row, 3, item2['part'])
                                        editcell(table, row, 4, item2['vendor'])
                                        editcell(table, row, 5, item2['amount'])
                                        editcell(table, row, 6, empty_serial(item2['serial1']))
                                        editcell(table, row, 8, 'CC')
                                        editcell(table, row, 9, '2')

                                        if item2['serial2'] and not item2['uv']:
                                            editcell(table, row, 7, int(item2['serial2']))
                                        else:
                                            editcell(table, row, 7, "ERROR")

                                        self.serial1_count += 1 if item2['serial1'] else 0
                                        self.serial2_count += int(item2['serial2'])
                                except KeyError:
                                    if item2['serial2']:
                                        serialscounter += int(item2['serial2'])

                editcell(table, object_row, 7, serialscounter)
                self.serial2_count += serialscounter
            break
        doc.save(f'{output_name}.docx')

    def ims_table(self, elements, output_name):
        doc = docx.Document()
        rows = row_count(elements)
        table = doc.add_table(rows=rows, cols=5)
        table.style = 'Table Grid'
        row = -1

        while row != rows or row <= rows:
            counter = 0
            for item in elements:
                row += 1
                counter += 1
                subcount = 0
                editcell(table, row, 0, counter)
                editcell(table, row, 1, prep(item))
                editcell(table, row, 3, item['rgg'])
                editcell(table, row, 4, item['rggpp'])

                if item['table']:
                    for item1 in item['table']:
                        subsubcount = 0
                        row += 1
                        subcount += 1
                        editcell(table, row, 0, f"{counter}.{subcount}")
                        editcell(table, row, 1, prep(item1))
                        editcell(table, row, 3, item1['rgg'])
                        editcell(table, row, 4, item1['rggpp'])

                        if item1['table']:
                            for item2 in item1['table']:
                                row += 1
                                subsubcount += 1
                                editcell(table, row, 0, f"{counter}.{subcount}.{subsubcount}")
                                editcell(table, row, 1, prep(item2))
                                editcell(table, row, 3, item2['rgg'])
                                editcell(table, row, 4, item2['rggpp'])
            break
        doc.save(f'{output_name}.docx')

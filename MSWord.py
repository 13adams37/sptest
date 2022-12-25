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


def empty_serial(serial):
    if not serial:
        return "—"
    else:
        return serial


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
        rows = row_count(elements)
        table = doc.add_table(rows=rows, cols=10)
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
        rows = row_count(elements)
        table = doc.add_table(rows=rows, cols=10)
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
                serialscounter = 0
                counter += 1
                row += 1
                editcell(table, row, 0, counter)
                editcell(table, row, 1, item['name'])
                editcell(table, row, 2, item['model'])
                editcell(table, row, 3, item['part'])
                editcell(table, row, 4, item['vendor'])
                editcell(table, row, 5, item['amount'])
                editcell(table, row, 6, empty_serial(item['serial1']))

                if item['serial2']:
                    serialscounter += int(item['serial2'])

                editcell(table, row, 8, 'CC')
                editcell(table, row, 9, '2')

                if item['table']:
                    for item1 in item['table']:
                        if item1['serial2']:
                            serialscounter += int(item1['serial2']) * int(item1['amount'])

                        if item1['table']:
                            for item2 in item1['table']:
                                if item2['serial2']:
                                    serialscounter += int(item2['serial2']) * int(item2['amount'])

                editcell(table, row, 7, serialscounter)
            break
        doc.save(f'{output_name}.docx')

    def ims_table(self, elements, output_name):
        doc = docx.Document()
        rows = row_count(elements)
        table = doc.add_table(rows=rows, cols=5)
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

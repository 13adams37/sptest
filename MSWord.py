import re
from copy import deepcopy
import docx

import db

nonBreakSpace = u'\xa0'


def empty_serial(serial):
    if not serial or serial == "0":
        return "–"
    else:
        return serial


def prep(elmtor):
    elmt = elmtor.copy()
    if elmt['part'] not in ("", "б/н"):
        elmt['part'] = f"№{nonBreakSpace}{elmt['part']}"
    else:
        elmt['part'] = f"б/н"
    output = f"{elmt['name']} {elmt['vendor']} {elmt['model']} {elmt['part']}"
    return f"{re.sub(' +', ' ', output)}"


class Word:
    def __init__(self):
        self.serial1_count = 0
        self.serial2_count = 0

    def act_table(self, elements, output_name):
        def fill_new_row_act(main_object, cnt):
            cell = table.add_row().cells
            cell[0].text = str(cnt)
            cell[1].text = main_object['name']
            cell[2].text = main_object['model']
            cell[3].text = main_object['part'] if main_object['part'] else 'б/н'
            cell[4].text = main_object['vendor']
            cell[5].text = main_object['amount']
            cell[6].text = empty_serial(main_object['serial1'])
            cell[7].text = "УФ" if main_object['uv'] else empty_serial(main_object['serial2'])
            cell[8].text = 'CC'
            cell[9].text = '2'

        doc = docx.Document()
        table = doc.add_table(rows=0, cols=10)
        table.style = 'Table Grid'
        counter = 0

        for item in elements:
            counter += 1
            fill_new_row_act(item, counter)

            if item['table']:
                for item1 in item['table']:
                    fill_new_row_act(item1, "")

                    if item1['table']:
                        for item2 in item1['table']:
                            fill_new_row_act(item2, "")

        doc.save(f'{output_name}.docx')

    def conclusion_table(self, elements, output_name):
        def fill_conclusion_new_row(main_object, cnt):
            cell = table.add_row().cells
            cell[0].text = str(cnt)
            cell[1].text = main_object['name']
            cell[2].text = main_object['model']
            cell[3].text = main_object['part']
            cell[4].text = main_object['vendor']
            cell[5].text = main_object['amount']
            cell[6].text = empty_serial(main_object['serial1'])
            self.serial1_count += 1 if main_object['serial1'] else 0

            if item['uv']:
                cell[7].text = 'УФ'
            else:
                cell[7].text = empty_serial(main_object['serial2'])

            self.serial2_count += int(main_object['serial2']) if main_object['serial2'] else 0

        def fill_conclusion_by_row(main_object, cnt, row, this_serial_counter):
            cell = table.rows[row].cells
            cell[0].text = str(cnt)
            cell[1].text = main_object['name']
            cell[2].text = main_object['model']
            cell[3].text = main_object['part']
            cell[4].text = main_object['vendor']
            cell[5].text = main_object['amount']
            cell[6].text = empty_serial(main_object['serial1'])
            self.serial1_count += 1 if main_object['serial1'] else 0

            if item['uv'] and not this_serial_counter:
                cell[7].text = 'УФ'
            else:
                cell[7].text = empty_serial(this_serial_counter)

        doc = docx.Document()
        table = doc.add_table(rows=0, cols=8)
        table.style = 'Table Grid'
        self.serial1_count = 0
        self.serial2_count = 0
        current_row = -1

        for counter_l1, item in enumerate(elements, start=1):  # elements, start=?
            serial_counter = 0
            table.add_row()
            current_row += 1
            l1_row_to_fill = deepcopy(current_row)

            if item['table']:
                counter_l2 = 0
                for item1 in item['table']:
                    try:
                        if item1['selected']:
                            counter_l2 += 1
                            l2_serial = 0
                            table.add_row()
                            current_row += 1
                            l2_row_to_fill = deepcopy(current_row)

                            if item1['table']:
                                subcount_l2 = 0
                                for sel_item2 in item1['table']:
                                    try:
                                        if sel_item2['selected']:
                                            subcount_l2 += 1
                                            current_row += 1
                                            fill_conclusion_new_row(sel_item2,
                                                                    f"{counter_l1}.{counter_l2}.{subcount_l2}")
                                    except KeyError:
                                        if sel_item2['serial2'] and not sel_item2['uv']:
                                            l2_serial += int(sel_item2['serial2'])

                            l2_serial += int(item1['serial2']) if item1['serial2'] != "УФ" and item1['serial2'] else 0
                            fill_conclusion_by_row(item1, f"{counter_l1}.{counter_l2}", l2_row_to_fill, str(l2_serial))
                            self.serial2_count += l2_serial
                            continue

                    except KeyError:
                        if item1['serial2']:
                            serial_counter += int(item1['serial2'])

                    if item1['table']:
                        counter_l3 = 0
                        for item2 in item1['table']:
                            try:
                                if item2['selected']:
                                    counter_l3 += 1
                                    current_row += 1
                                    fill_conclusion_new_row(item2,
                                                            f"{counter_l1}.{counter_l2}.{counter_l3}" if counter_l2 > 0 else f"{counter_l1}.{counter_l3}")

                            except KeyError:
                                if item2['serial2']:
                                    serial_counter += int(item2['serial2'])

            serial_counter += int(item['serial2']) if item['serial2'] != "УФ" and item['serial2'] else 0
            fill_conclusion_by_row(item, counter_l1, l1_row_to_fill, str(serial_counter))
            self.serial2_count += serial_counter
        doc.save(f'{output_name}.docx')
        return self.serial1_count, self.serial2_count

    def methods_table(self, elements, output_name):
        def fill_new_row_methods(main_object, cnt, method, author):
            cell = table.add_row().cells
            cell[0].text = str(cnt)
            cell[1].text = prep(main_object)
            cell[2].text = str(method)
            cell[3].text = str(author)

        def get_method(name):
            for method_id in iter(db.methods_db):
                method_content = db.methods_db.get(method_id)
                if method_content['type'] == 'По содержанию':
                    # if method_content['name'].lower().__contains__(name):
                    if name.lower().__contains__(method_content['name'].lower()):
                        print(method_content['methods'], 'cont for', name)
                        return method_content['methods']
                else:
                    if method_content['name'].lower() == name:
                        print(method_content['methods'], '== for', name)
                        return method_content['methods']
            return ''

        doc = docx.Document()
        table = doc.add_table(rows=0, cols=4)
        table.style = 'Table Grid'
        print(elements)

        for counter_l1, item in enumerate(elements, start=1):
            try:
                author = item['author']
            except KeyError:
                author = ""

            fill_new_row_methods(item, f"{counter_l1}", get_method(item['name'].lower()), author)
            if item['table']:
                for counter_l2, item1 in enumerate(item['table'], start=1):
                    fill_new_row_methods(item1, f"{counter_l1}.{counter_l2}", get_method(item1['name'].lower()), author)

                    if item1['table']:
                        for counter_l3, item2 in enumerate(item1['table'], start=1):
                            fill_new_row_methods(item2, f"{counter_l1}.{counter_l2}.{counter_l3}", get_method(item2['name'].lower()), author)

        doc.save(f'{output_name}.docx')

    def ims_table(self, elements, output_name):
        def fill_new_row_ims(main_object, cnt):
            cell = table.add_row().cells
            cell[0].text = str(cnt)
            cell[1].text = prep(main_object)
            cell[3].text = main_object['rgg']
            cell[4].text = main_object['rggpp']

        doc = docx.Document()
        table = doc.add_table(rows=0, cols=5)
        table.style = 'Table Grid'

        for counter_l1, item in enumerate(elements, start=1):
            fill_new_row_ims(item, f"{counter_l1}")

            if item['table']:
                for counter_l2, item1 in enumerate(item['table'], start=1):
                    fill_new_row_ims(item1, f"{counter_l1}.{counter_l2}")

                    if item1['table']:
                        for counter_l3, item2 in enumerate(item1['table'], start=1):
                            fill_new_row_ims(item2, f"{counter_l1}.{counter_l2}.{counter_l3}")

        doc.save(f'{output_name}.docx')

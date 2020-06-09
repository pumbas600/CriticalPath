import csv
from _tkinter import TclError
import os.path as ospath
from enum import Enum

class Errors(Enum):
    SUCCESS = 'Successfully completed the action.'
    FILE_NOT_FOUND = "The file, {}, couldn't be found."
    FILE_MADE = "The file, {}, didn't exist and so it has been created."
    FILE_CURRENTLY_OPEN = 'The file, {}, cannot be accessed because it is currently open.'
    CLIPBOARD_EMPTY = 'Your clipboard is currently empty.'

    @staticmethod
    def is_error(error):
        return error is Errors and error != Errors.SUCCESS

class IOUtilities:

    @staticmethod
    def save_grid_list_to_clipboard(root, clipboard_list, item_to_list_converter,
                                    headers=None, print_clipboard=False):
        root.clipboard_clear()
        if headers is not None:
            root.clipboard_append('\t'.join(headers) + '\n')
        for item in clipboard_list:
            row = '\t'.join(item_to_list_converter(item))
            root.clipboard_append(row + '\n')

        if print_clipboard:
            print(root.clipboard_get())

        return Errors.SUCCESS

    @staticmethod
    def get_clipboard_as_dictionary_list(root, lower_headers=False):
        try:
            clipboard = root.clipboard_get()
            rows = clipboard.split('\n')

            headers = rows[0].split('\t')
            if lower_headers:
                headers = [h.lower() for h in headers]

            dictionary_list = []
            for row in rows[1:-1]:
                columns = row.split('\t')
                dict_data = dict(zip(headers, columns))
                dictionary_list.append(dict_data)

            return dictionary_list
        except TclError:
            return Errors.CLIPBOARD_EMPTY

    @staticmethod
    def get_csv_as_dictionary_list(path, not_found_callback=None, lower_headers=False):
        if path[-4:] != '.csv':
            path += '.csv'

        if not ospath.isfile(path):
            if not_found_callback is not None:
                return not_found_callback(path)
            else:
                return Errors.FILE_NOT_FOUND

        with open(path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            if lower_headers:
                reader.fieldnames = [h.lower().strip() for h in reader.fieldnames]
            return list(reader)

    @staticmethod
    def create_csv_file_callback(headers):
        def create_csv_file(path):
            with open(path, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                csvfile.close()
                return Errors.FILE_MADE
        return create_csv_file

    @staticmethod
    def write_csv_file_from_list(path, data_list, headers, item_to_list_converter):
        if path[-4:] != '.csv':
            path += '.csv'

        try:
            with open(path, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()

                for item in data_list:
                    row = dict(zip(headers, item_to_list_converter(item)))
                    writer.writerow(row)
        except PermissionError:
            return Errors.FILE_CURRENTLY_OPEN
        else:
            return Errors.SUCCESS


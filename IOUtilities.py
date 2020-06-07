import csv
from _tkinter import TclError
import os.path as ospath

class IOUtilities:
    SUCCESS = None
    FILE_NOT_FOUND = -1
    FILE_MADE = -2
    FILE_CURRENTLY_OPEN = -3
    CLIPBOARD_EMPTY = -4

    @staticmethod
    def is_error(result):
        return isinstance(result, int)

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

        return IOUtilities.SUCCESS

    @staticmethod
    def get_clipboard_as_dictionary_list(root):
        try:
            clipboard = root.clipboard_get()
            rows = clipboard.split('\n')

            headers = rows[0].split('\t')
            dictionary_list = []
            for row in rows[1:-1]:
                columns = row.split('\t')
                dict_data = dict(zip(headers, columns))
                dictionary_list.append(dict_data)

            return dictionary_list
        except TclError:
            return IOUtilities.CLIPBOARD_EMPTY

    @staticmethod
    def get_csv_as_dictionary_list(path, not_found_callback=None):
        if path[-4:] != '.csv':
            path += '.csv'

        if not ospath.isfile(path):
            if not_found_callback is not None:
                return not_found_callback(path)
            else:
                return IOUtilities.FILE_NOT_FOUND

        with open(path, 'r') as csvfile:
            return list(csv.DictReader(csvfile))

    @staticmethod
    def create_csv_file_callback(headers):
        def create_csv_file(path):
            with open(path, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                csvfile.close()
                return IOUtilities.FILE_MADE
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
            return IOUtilities.FILE_CURRENTLY_OPEN
        else:
            return IOUtilities.SUCCESS


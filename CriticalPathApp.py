from CriticalPath import *
from IOUtilities import *
from TKDesigner import TKDesigner, ResizingCanvas
from tkinter import *

class CriticalPathApp(TKDesigner):

    def __init__(self):
        super().__init__()

        self.filetype = '.csv'
        self.INPUT_DATA = 'data' + self.filetype
        self.OUTPUT_DATA = 'output' + self.filetype

        self._data = None
        self._data_headers = ['name', 'time', 'dependencies']

        self.item_to_list_converter = lambda n: [n.name, str(int_if_same(n.start_time)), str(int_if_same(n.time)),
                                                 str(int_if_same(n.get_end_time())), str(int_if_same(n.spare_time))]
        self.title('Critical Path Calculator')
        self.init_ui()

    def init_ui(self):
        self.display_get_input_data_ui()

    def display_get_input_data_ui(self):

        def on_got_input_data():
            self.clear_ui()
            self.display_input_data_ui()

        def on_paste_data():
            #TODO: Do further testing of partially incorrect clipboards
            result = IOUtilities.get_clipboard_as_dictionary_list(self, lower_headers=True)
            if Errors.is_error(result):
                self.create_temporary_popup(result.value)
            else:
                self._data = result
                if len(self._data) == 0:
                    self.create_temporary_popup(f"Your clipboard doesn't seem to be of a {self.filetype} file.")
                else:
                    on_got_input_data()

        def on_upload_data(event):
            path = event.widget.content.get()
            not_found_callback = IOUtilities.create_csv_file_callback(
                self._data_headers) if path == self.INPUT_DATA else None

            result = IOUtilities.get_csv_as_dictionary_list(path, not_found_callback=not_found_callback,
                                                            lower_headers=True)

            if Errors.is_error(result):
                self.create_temporary_popup(result.value.format(path))

            else:
                self._data = result
                if len(self._data) == 0:
                    self.create_temporary_popup(f'The file, {path}, seems to be empty.')
                else:
                    on_got_input_data()

        paste_button = self.create_button('Paste Data', command=on_paste_data, cooldown=1)
        upload_button, path_entry = self.create_button_entry_pair(
            button_settings=self.settings(text='Upload Data', bind=on_upload_data, cooldown=1),
            entry_settings=self.settings(text=self.INPUT_DATA))

        self.add_to_grid(paste_button, row=0, column=0, padding=5)
        self.add_to_grid(upload_button, row=0, column=1, padding=5)
        self.add_to_grid(path_entry, row=0, column=2, padding=5)
        self.set_column_weights(3)

    def display_input_data_ui(self):
        def on_parse_data():
            def validate_data():
                def check_headers():
                    input_headers = list(self._data[0].keys())
                    if len(input_headers) != len(self._data_headers):
                        self.create_temporary_popup(f"There doesn't seem to be the correct number of columns. Make sure "
                                                    f"you have the following columns: {', '.join(self._data_headers)}.")
                        return False
                    else:
                        for h in self._data_headers:
                            if h not in input_headers:
                                self.create_temporary_popup(f'You seem to be missing the column: {h}.')
                                return False
                    return True

                def check_dependencies_and_time():
                    tasks = []
                    for row in self._data:
                        dependencies = parse_dependencies(row['dependencies'])
                        if row['name'].upper() in dependencies:
                            self.create_temporary_popup(f'The task {row["name"]}, cannot be dependent on itself.')
                            return False
                        tasks.append(row['name'].upper())
                        if not all([d in tasks for d in dependencies]):
                            self.create_temporary_popup(f'Dependencies on a task, must come after that task in the '
                                                        f'dataset for the row {row["name"]}.')
                            return False
                        try:
                            float(row['time'])
                        except ValueError:
                            self.create_temporary_popup(f"The time for the task {row['name']}, doesn't seem "
                                                        f"to be a number.")
                            return False

                    return True

                if not all([check_headers(), check_dependencies_and_time()]):
                    self.clear_ui()
                    self.display_get_input_data_ui()

            validate_data()
            solve_data(self._data)
            self.clear_ui()
            self.display_output_data_ui()

        #Reset window size if it has been adjusted
        self.geometry('')
        #TODO: Check for invalid data formatting
        if self._data is None:
            self.create_temporary_popup("Something went wrong and the data hasn't been correctly loaded")
            return

        self.grid_from_list_of_dict(
            self._data,
            name=lambda n: n.capitalize(),
            dependencies=lambda x: ', '.join(d.upper() for d in x.split(','))
        ).pack(fill=BOTH)

        self.create_button('Parse Data', command=on_parse_data, padding=5).pack(fill=X)
        self.set_current_size_as_min()

    def display_output_data_ui(self):
        def on_save_data_to_clipboard():
            IOUtilities.save_grid_list_to_clipboard(
                self, clipboard_list=list(data.values()),
                item_to_list_converter=self.item_to_list_converter,
                headers=['Task', 'Start Time', 'Time Taken', 'End Time', 'Spare Time']
            )
            self.create_temporary_popup("Successfully saved the data to your clipboard!")

        def on_save_data_to_file():
            result = IOUtilities.write_csv_file_from_list(
                path=self.OUTPUT_DATA,
                data_list=list(data.values()),
                item_to_list_converter=self.item_to_list_converter,
                headers=['Task', 'Start Time', 'Time Taken', 'End Time', 'Spare Time']
            )

            #There was an error writing the data to the file
            if Errors.is_error(result):
                self.create_temporary_popup(result.value.format(self.OUTPUT_DATA))
            else:
                self.create_temporary_popup(f'Successfully saved the data to the file: {OUTPUT_DATA}.')

        def display_supervisor_ui():
            supervisors = determine_supervisors()
            supervisor_count = len(supervisors)
            self.create_label(f'Number of supervisors required: {supervisor_count}',
                              anchor=W, padx=5).pack(fill=X)

            line_width = 10
            vgap = 45
            padx = 10

            self.update()
            width = self.winfo_width()
            maximum_time = get_final_node().get_end_time()
            unit = (width - (2 * padx)) / maximum_time

            height = supervisor_count * (vgap + line_width)

            canvas = ResizingCanvas(self, width=width, height=height)
            canvas.pack(fill=X, expand=True)

            row_index = 0
            for supervisor in supervisors:
                row_index += 1
                prev_time = None
                for i in range(len(supervisor.working_times)):
                    working_time = supervisor.working_times[i]
                    fill = darker_pale_blue if i % 2 == 0 else mid_pale_blue

                    x1 = (working_time.start * unit) + padx
                    x2 = (working_time.end * unit) + padx
                    # Prevents double ups occurring when a task finishes and another starts at the same time
                    if prev_time is None or prev_time.end != working_time.start:
                        # Display start time
                        canvas.create_text(x1, (row_index + 0.3) * vgap,
                                           text=working_time.get_start())

                    # Create line representing task time.
                    canvas.create_line(x1, row_index * vgap, x2, row_index * vgap,
                                       width=line_width, fill=fill)

                    # Display end time
                    canvas.create_text(x2, (row_index + 0.3) * vgap,
                                       text=working_time.get_end())

                    # Display task name in the middle of the line
                    canvas.create_text(self.find_centre_of(x1, x2), (row_index - 0.3) * vgap,
                                       text=working_time.name.strip())

                    prev_time = working_time

        #Reset window size if it has been adjusted
        self.geometry('')

        data = get_parsed_data()
        self.grid_from_list(
            list(data.values()),
            item_to_list_converter=self.item_to_list_converter,
            headers=['Task', 'Start Time', 'Time Taken', 'End Time', 'Spare Time'],
        ).pack(fill=BOTH)

        self.create_single_row(
            (self.create_button,
             self.settings(text='Copy to Clipboard', command=on_save_data_to_clipboard, cooldown=1)),
            (self.create_button,
             self.settings(text='Save as File', command=on_save_data_to_file, cooldown=1))
        ).pack(fill=X)

        self.create_vertical_space(15)
        self.create_single_row(
            (self.create_label,
             self.settings(text='Critical Path: ', font=self.get_bold_font(self._label_font), anchor=E)),
            (self.create_label,
             self.settings(text=' → '.join([n.name for n in determine_critical_path()]), anchor=W)),
            (self.create_label,
             self.settings(text='Minimum Time: ', font=self.get_bold_font(self._label_font), anchor=E)),
            (self.create_label,
             self.settings(text=str(int_if_same(get_final_node().get_end_time())), anchor=W))
        ).pack(fill=X)

        self.create_header('Supervisor Distribution', padding=5).pack(fill=X)
        display_supervisor_ui()
        self.set_current_size_as_min()

def main():
    app = CriticalPathApp()
    app.mainloop()


if __name__ == '__main__':
    main()
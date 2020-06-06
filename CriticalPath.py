from _tkinter import TclError
import csv
from os import path as ospath
from tkinter import *

class Node:

    @staticmethod
    def get_empty():
        return Node('Empty', -1, None)

    def __init__(self, name, time, critical_parent):
        self.name = name
        self.time = time
        self.critical_parent = critical_parent
        self.critical_child = None
        self.start_time = critical_parent.get_end_time() if critical_parent is not None else 0
        self.is_critical = False
        self.spare_time = 0

    def get_end_time(self):
        return self.start_time + self.time

    def get_critical_parent(self):
        return self.critical_parent

    def set_is_critical(self):
        self.is_critical = True

    def set_critical_child(self, child):
        if self.critical_child is None or self.critical_child.start_time > child.start_time:
            self.critical_child = child

    def calculate_spare_time(self, total_time):
        child_start_time = self.critical_child.start_time if self.critical_child is not None else total_time

        self.spare_time = child_start_time - self.get_end_time()


class Supervisor:

    def __init__(self, time_range):
        self.working_times = [time_range]

    def add_work_time(self, time_range):
        self.working_times.append(time_range)
        self.sort_time_range_down()

    def sort_time_range_down(self):
        current_index = len(self.working_times) - 1
        while current_index > 0 and\
                self.working_times[current_index] < self.working_times[current_index - 1]:
            self.swap(current_index, current_index - 1)
            current_index -= 1

    def swap(self, a: int, b: int):
        self.working_times[a], self.working_times[b]\
            = self.working_times[b], self.working_times[a]

    def is_free_during(self, time_range):
        # Linear search FTW...
        for working_time in self.working_times:
            if working_time == time_range:
                return False
        return True

    def just_finished_at(self, time):
        finish_time = self.working_times[len(self.working_times) - 1].end if len(self.working_times) != 0 else 0
        return finish_time == time

class TimeRange:

    def __init__(self, start, end, name):
        self.start = start
        self.end = end
        self.name = name

    def get_start(self):
        return TimeRange.int_if_same(self.start)

    def get_end(self):
        return TimeRange.int_if_same(self.end)

    @staticmethod
    def int_if_same(num):
        return int(num) if int(num) == num else num

    def __lt__(self, other):
        return isinstance(other, TimeRange) and self.end < other.start

    def __gt__(self, other):
        return isinstance(other, TimeRange) and self.start > other.end

    def __eq__(self, other):
        return isinstance(other, TimeRange) and (other.start < self.end < other.end or
                                                 other.start < self.start < other.end or
                                                 (other.start >= self.start and other.end <= self.end))

    def __ne__(self, other):
        return not self.__eq__(other)


VERSION = 1.1
INPUT_DATA = 'data.csv'
OUTPUT_DATA = 'output.csv'

pale_blue = '#c4d9ed'
darker_pale_blue = '#aaceef'

def parse_dependencies(dependencies):
    if dependencies == '':
        return []
    return [d.strip().upper() for d in dependencies.split(',')]

def parse_data(clipboard_data=None, path_to_data=None):
    global parsed_data
    global final_node
    parsed_data = {}
    final_node = None

    def get_csv_data(path):
        if path is None:
            path = INPUT_DATA
        if not ospath.isfile(path):
            # Create the file if it doesn't exist.
            columns = ['name', 'time', 'dependencies']
            with open(INPUT_DATA, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()
                csvfile.close()
            print(f'The file {INPUT_DATA} did not exist and so has been created.')
            input('Press enter to close the console.')

        try:
            with open(INPUT_DATA, 'r') as csvfile:
                return list(csv.DictReader(csvfile))
        except FileNotFoundError:
            print(f"The file, {INPUT_DATA} doesn't exist, please create it and re-run the program.")
            input('Press enter to close the console.')

        return None

    def get_clipboard_data(clipboard):
        print(clipboard)
        rows = clipboard.split('\n')

        headers = rows[0].split('\t')
        dict_data_list = []
        for row in rows[1:-1]:
            columns = row.split('\t')
            dict_data = dict(zip(headers, columns))
            dict_data_list.append(dict_data)

        return dict_data_list

    data = get_csv_data(path_to_data) if clipboard_data is None else get_clipboard_data(clipboard_data)

    if data is not None:
        for row in data:
            try:
                name = row["name"].upper()

                try:
                    time = float(row["time"])
                except ValueError:
                    print(f'{row["time"]} should be a number.')

                parsed_dependencies = parse_dependencies(row["dependencies"])
                dependencies = [parsed_data[d] for d in parsed_dependencies]

                critical_node = None

                if len(dependencies) != 0:
                    critical_node = max(dependencies, key=lambda node: node.get_end_time())

                node = Node(name, time, critical_node)
                for n in dependencies:
                    # If the start time is sooner than node n's current critical child, then it
                    # updates it to this node.
                    n.set_critical_child(node)

                if final_node is None or final_node.get_end_time() < node.get_end_time():
                    final_node = node

                parsed_data[name] = node
            except KeyError:
                print(f"There was an error parsing {INPUT_DATA}. Make sure you have all the columns "
                      f"correctly named (name, time, dependencies) and check that {INPUT_DATA}'s formatting "
                      f"hasn't been corrupted. In that case, simple re-enter the data and check it's saved "
                      f"after closing it.")
                break

        determine_free_time()

def determine_critical_path():
    _final_node = get_final_node()
    critical_path = []

    current_node = _final_node

    while current_node is not None:
        critical_path.append(current_node)
        current_node.is_critical = True
        current_node = current_node.get_critical_parent()
    return critical_path[::-1]

def determine_supervisors():
    data = get_parsed_data()
    supervisors = []

    for name, node in data.items():
        time_range = TimeRange(node.start_time, node.get_end_time(), name)
        free_supervisor = determine_free_supervisor(supervisors, time_range)

        if free_supervisor is None:
            supervisors.append(Supervisor(time_range))
        else:
            free_supervisor.add_work_time(time_range)

    return supervisors

def determine_free_supervisor(supervisors, time_range):
    free_supervisor = None
    for supervisor in supervisors:
        #Prioritise supervisors that have just finished
        if supervisor.just_finished_at(time_range.start):
            return supervisor

        elif free_supervisor is None and supervisor.is_free_during(time_range):
            free_supervisor = supervisor
    return free_supervisor

def determine_free_time():
    _final_node = get_final_node()
    data = get_parsed_data()

    for name, node in data.items():
        node.calculate_spare_time(_final_node.get_end_time())

def write_parsed_data_to_csv():
    _final_node = get_final_node()
    data = get_parsed_data()
    if len(data.items()) == 0:
        print(f'{INPUT_DATA} is empty. Add data to it for the program to run.')
    else:
        try:
            with open(OUTPUT_DATA, 'w') as csvfile:
                columns = ["name", "start time", "time taken", "end time", "spare time", "is critical"]
                writer = csv.DictWriter(csvfile, fieldnames=columns)

                writer.writeheader()
                critical_path = determine_critical_path()

                for name, node in data.items():
                    row = {"name": name, "start time": node.start_time, "time taken": node.time,
                           "end time": node.get_end_time(), "spare time": node.spare_time, "is critical": node.is_critical}
                    writer.writerow(row)
                writer.writerow({"name": "Critical Path:", "start time": " -> ".join([n.name for n in critical_path]),
                                "spare time": "Total Time:", "is critical": _final_node.get_end_time()})
        except PermissionError:
            print(f"Couldn't save data because you had {OUTPUT_DATA} open.\n"
                  "Close the file and re-run the program.")
        else:
            print(f"Data successfully calculated and saved in the file: {OUTPUT_DATA}.  ")

def get_parsed_data():
    global parsed_data
    try:
        parsed_data is None
    # If parsed data is called before assignment
    except NameError:
        parsed_data = {}
    return parsed_data

def get_final_node():
    global final_node
    try:
        final_node is None
    # If final node is called before assignment
    except NameError:
        final_node = Node.get_empty()
    return final_node

def build_app():
    root = Tk()
    root.title('Critical Path Calculator')
    root.configure(background='white')
    frame = Frame(root)
    frame.configure(background='white')
    frame.pack(side=TOP, fill=X)

    def create_header(text, container=frame, **settings):
        header = create_label(text, container, **settings)
        #Add formatting to header
        return header

    def create_label(text, container=frame, **settings):
        settings.setdefault('bg', 'white')
        return Label(container, text=str(text), **settings)

    def create_button(text, container=frame, **settings):
        settings.setdefault('bg', 'white')
        return Button(container, text=text, **settings)

    def add_to_grid(widget, row, column, **settings):

        settings.setdefault('sticky', 'ew')
        settings.setdefault('ipadx', 10)
        settings.setdefault('ipady', 5)
        widget.grid(row=row, column=column, **settings)

    def clear_ui():
        for child in frame.winfo_children():
            child.destroy()

    def create_output_ui():
        data = get_parsed_data()

        def save_parsed_data_to_clipboard():
            clipboard = "name\tstart_time\ttime\tend_time\tspare_time"
            for _name, _node in data.items():
                _row = _node.name + "\t" + str(_node.start_time) + "\t" + str(_node.time) + "\t" +\
                      str(_node.get_end_time()) + "\t" + str(_node.spare_time)
                clipboard += "\n" + _row
            # Clear whats currently in the clipboard and replace it with the calculated data.
            root.clipboard_clear()
            root.clipboard_append(clipboard)
            print(root.clipboard_get())

        def create_row(node, row, **settings):
            add_to_grid(create_label(node.name,           **settings), row, 0)
            add_to_grid(create_label(node.start_time,     **settings), row, 1)
            add_to_grid(create_label(node.time,           **settings), row, 2)
            add_to_grid(create_label(node.get_end_time(), **settings), row, 3)
            add_to_grid(create_label(node.spare_time,     **settings), row, 4)

        def create_supervisor_ui():
            supervisors = determine_supervisors()

            width = frame.winfo_width()
            line_width = 10
            vgap = 50
            xpad = 10

            supervisor_count = len(supervisors)
            unit = width // get_final_node().get_end_time()

            #highlightthickness=0 removed weird border around the canvas
            canvas = Canvas(root, width=(unit * get_final_node().get_end_time()) + (2 * xpad),
                            bg='white', bd=0, highlightthickness=0)

            canvas.create_text(width // 2, vgap // 2,
                               text=f'Number of supervisors required: {supervisor_count}',
                               justify=CENTER)
            row_index = 1.5
            for supervisor in supervisors:
                prev_time = None
                for i in range(len(supervisor.working_times)):
                    working_time = supervisor.working_times[i]
                    fill = pale_blue if i % 2 == 0 else darker_pale_blue

                    #Prevents double ups occuring when a task finishes and another starts at the same time
                    if prev_time is None or prev_time.end != working_time.start:
                        #Display start time
                        canvas.create_text((working_time.start * unit) + xpad, (row_index + 0.3) * vgap,
                                           text=working_time.get_start(), justify=CENTER)

                    #Create line representing task time.
                    canvas.create_line((working_time.start * unit) + xpad, row_index * vgap,
                                       (working_time.end * unit) + xpad, row_index * vgap,
                                       width=line_width, fill=fill)

                    #Display end time
                    canvas.create_text((working_time.end * unit) + xpad, (row_index + 0.3) * vgap,
                                       text=working_time.get_end(), justify=CENTER)

                    #Display task name in the middle of the line
                    centre = ((working_time.start + working_time.end) * unit) / 2
                    canvas.create_text(centre + xpad, (row_index - 0.3) * vgap,
                                       text=working_time.name.strip(), justify=CENTER)

                    prev_time = working_time
                row_index += 1
            canvas.pack()

        def create_bottom_ui():
            bottom_frame = Frame(root)
            bottom_frame.pack()

            add_to_grid(create_label(
                'Critical Path: ' + " -> ".join([n.name for n in determine_critical_path()]),
                container=bottom_frame), row=0, column=0, columnspan=5)
            add_to_grid(create_label(
                'Minimum Time: ' + str(get_final_node().get_end_time()),
                container=bottom_frame), row=1, column=0, columnspan=5)
            create_supervisor_ui()


        row = 0
        add_to_grid(create_header('Task'), row, 0)
        add_to_grid(create_header('Start Time'), row, 1)
        add_to_grid(create_header('Time Taken'), row, 2)
        add_to_grid(create_header('End Time'), row, 3)
        add_to_grid(create_header('Spare Time'), row, 4)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
        frame.columnconfigure(3, weight=1)
        frame.columnconfigure(4, weight=1)

        row += 1

        for name, node in data.items():
            bg_colour = 'white' if row % 2 == 0 else pale_blue
            create_row(node, row, bg=bg_colour)
            row += 1

        middle_frame = Frame(root)
        middle_frame.configure(background='white')
        middle_frame.pack(fill=X)
        middle_frame.columnconfigure(0, weight=1)
        middle_frame.columnconfigure(1, weight=1)
        add_to_grid(create_button('Save as file', container=middle_frame, command=write_parsed_data_to_csv),
                    row=0, column=0)
        add_to_grid(create_button('Copy to clipboard', container=middle_frame, command=save_parsed_data_to_clipboard),
                    row=0, column=1)

        create_bottom_ui()
        root.minsize(root.winfo_width(), root.winfo_height())

    def create_input_ui():
        def paste_data():
            try:
                clipboard_data = root.clipboard_get()
                parse_data(clipboard_data=clipboard_data)
            except TclError:
                print("Your clipboard is empty")
            else:
                clear_ui()
                create_output_ui()

        def upload_data(event):
            path = event.widget.content.get()
            if path[-4:] != '.csv':
                path += '.csv'
            parse_data(path_to_data=path)
            clear_ui()
            create_output_ui()

        paste_data_button = create_button('Paste data', command=paste_data)
        upload_data_button = create_button('Upload data')
        upload_data_button.bind('<Button-1>', upload_data)

        content = StringVar()
        upload_data_file_input = Entry(frame, text=f'{INPUT_DATA}', textvariable=content)
        upload_data_button.content = content
        content.set(INPUT_DATA)
        add_to_grid(paste_data_button, 0, 0, padx=5, pady=5)
        add_to_grid(upload_data_button, 0, 1, padx=5, pady=5)
        add_to_grid(upload_data_file_input, 0, 2, padx=5, pady=5)

    create_input_ui()
    root.mainloop()

def main():
    print("Program started :)")
    build_app()

    input("Press enter to close the console.")


if __name__ == '__main__':
    main()

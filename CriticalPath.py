import csv
from os import path

class Node:

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
        #Use some form of binary search because times are sorted from lowest to highest
        pass


class TimeRange:

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __lt__(self, other):
        if isinstance(other, TimeRange):
            return self.end < other.start
        else:
            return False


INPUT_DATA = 'data.csv'
OUTPUT_DATA = 'output.csv'

def parse_dependencies(dependencies):
    if dependencies == '':
        return []
    return dependencies.split(',').trim().upper()

def parse_data():
    global parsed_data
    global final_node
    parsed_data = {}
    final_node = None

    if not path.isfile(INPUT_DATA):
        #Create the file if it doesn't exist.
        columns = ['name', 'time', 'dependencies']
        with open(INPUT_DATA, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            csvfile.close()
        print(f'The file {INPUT_DATA} did not exist and so has been created.')
        input('Press enter to close the console.')

    try:
        with open(INPUT_DATA, 'r') as csvfile:
            data = csv.DictReader(csvfile)
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
                    print(f"There was an error parsing {INPUT_DATA}. Make sure you have all the columns"
                          f" correctly named (name, time, dependencies) and check that {INPUT_DATA}'s formatting"
                          f"hasn't been corrupted. In that case, simple re-enter the data and check it's saved "
                          f"after closing it.")
                    break
    except FileNotFoundError:
        print(f"The file, {INPUT_DATA} doesn't exist, please create it and re-run the program.")
        input('Press enter to close the console.')

def determine_critical_path():
    global final_node
    critical_path = []

    current_node = final_node

    while current_node is not None:
        critical_path.append(current_node)
        current_node.is_critical = True
        current_node = current_node.get_critical_parent()
    return critical_path[::-1]


def determine_free_time():
    global parsed_data
    global final_node

    for name, node in parsed_data.items():
        node.calculate_spare_time(final_node.get_end_time())


def write_parsed_data_to_csv(data):
    global final_node
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
                                "spare time": "Total Time:", "is critical": final_node.get_end_time()})
        except PermissionError:
            print(f"Couldn't save data because you had {OUTPUT_DATA} open.\n"
                  "Close the file and re-run the program.")
        else:
            print(f"Data successfully calculated and saved in the file: {OUTPUT_DATA}.  ")

    input("Press enter to close the console.")

def main():
    global parsed_data

    print("Program started :)")

    parse_data()
    determine_free_time()
    write_parsed_data_to_csv(parsed_data)
    #for name, node in parsed_data.items():
    #    print(f'{name}: | start time: {node.start_time} | end time: {node.get_end_time()}'
    #          f' | spare time: {node.spare_time} | is critical: {node.is_critical}')

if __name__ == '__main__':
    main()

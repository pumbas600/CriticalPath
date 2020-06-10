def int_if_same(num):
    return int(num) if int(num) == num else round(num, 1)

class Node:

    @staticmethod
    def get_empty():
        return Node('Empty', -1, [], None)

    def __init__(self, name, time, dependencies, critical_parent):
        self.name = name
        self.time = time
        self.dependencies = dependencies
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
        return int_if_same(self.start)

    def get_end(self):
        return int_if_same(self.end)

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
mid_pale_blue = '#c0d6ea'
darker_pale_blue = '#aaceef'

def parse_dependencies(dependencies):
    if dependencies == '':
        return []
    return [d.strip().upper() for d in dependencies.split(',')]

def solve_data(data):
    global final_node
    global parsed_data
    final_node = None
    parsed_data = {}

    if data is not None:
        for row in data:
            try:
                name = row["name"].upper()

                time = 0
                try:
                    time = float(row["time"])
                except ValueError:
                    print(f'{row["time"]} should be a number.')

                parsed_dependencies = parse_dependencies(row["dependencies"])
                dependencies = [parsed_data[d] for d in parsed_dependencies]

                critical_node = None

                if len(dependencies) != 0:
                    critical_node = max(dependencies, key=lambda node: node.get_end_time())

                node = Node(name, time, dependencies, critical_node)
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


def main():
    pass

if __name__ == '__main__':
    main()

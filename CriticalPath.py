import pandas as pd
from node import Node

EXCEL_INPUT_DATA = 'data.xlsx'
EXCEL_OUTPUT_DATA = 'output.xlsx'

def open_data_file():
    data_frame = pd.read_excel(io=EXCEL_INPUT_DATA,
                               dtype={'name': str, 'time': float, 'dependencies': str})
    return data_frame


def parse_dependencies(dependencies):
    if type(dependencies) is float:
        return []
    return dependencies.split(',')

def parse_data(data_frame):
    global parsed_data
    global final_node
    parsed_data = {}
    final_node = None

    for index, series in data_frame.iterrows():
        name = series.get("name")
        time = series.get("time")

        parsed_dependencies = parse_dependencies(series.get("dependencies"))
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

    for name, node in parsed_data.items():
        node.calculate_spare_time()

def write_parsed_data_to_excel(data):
    df = pd.DataFrame(columns=["name", "start time", "end time", "spare time", "is critical"])
    for name, node in data.items():
        row = {"name": name, "start time": node.start_time, "end time": node.get_end_time(),
               "spare time": node.spare_time, "is critical": node.is_critical}
        df = df.append(row, ignore_index=True)

    #print(df)

    # Save the calculated data to the excel file
    with pd.ExcelWriter(EXCEL_OUTPUT_DATA) as writer:
        df.to_excel(writer)


def main():
    global parsed_data

    df = open_data_file()
    parse_data(df)
    critical_path = determine_critical_path()
    determine_free_time()

    print(", ".join([n.name for n in critical_path]))
    write_parsed_data_to_excel(parsed_data)
    #for name, node in parsed_data.items():
    #    print(f'{name}: | start time: {node.start_time} | end time: {node.get_end_time()}'
    #          f' | spare time: {node.spare_time} | is critical: {node.is_critical}')



if __name__ == '__main__':
    main()

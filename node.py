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
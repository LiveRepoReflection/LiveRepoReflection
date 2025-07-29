class Node:
    def __init__(self, employee_id, department, children):
        self.employee_id = employee_id
        self.department = department
        self.children = children

def find_meeting_scope(root, attendees):
    target_set = set(attendees)
    if not target_set:
        return None

    def helper(node):
        current_set = set()
        candidate = None
        if node.employee_id in target_set:
            current_set.add(node.employee_id)
        for child in node.children:
            child_set, child_candidate = helper(child)
            # If a candidate is already found in a descendant, propagate it up.
            if child_candidate is not None:
                candidate = child_candidate
            current_set |= child_set
        # If no candidate found in children and the current subtree covers all targets,
        # then the current node is the minimal meeting scope for the attendees in this subtree.
        if candidate is None and current_set == target_set:
            candidate = node
        return current_set, candidate

    _, result = helper(root)
    return result
class Node:
    def __init__(self, weight, order, symbol=None, parent=None, left=None, right=None):
        self.weight = weight
        self.order = order
        self.symbol = symbol  # None indicates an internal node or NYT node.
        self.parent = parent
        self.left = left
        self.right = right

    def is_leaf(self):
        return self.left is None and self.right is None


class AdaptiveHuffmanTree:
    def __init__(self):
        # Initialize the tree with a single NYT (Not Yet Transmitted) node.
        self.max_order = 512
        self.root = Node(0, self.max_order, None)
        self.NYT = self.root
        self.leaves = {}  # symbol -> Node mapping for quick lookup.
        self.nodes = [self.root]  # Maintain a list of all nodes for easy scanning.

    def get_code(self, node):
        code = ""
        current = node
        while current.parent:
            if current.parent.left == current:
                code = "0" + code
            else:
                code = "1" + code
            current = current.parent
        return code

    def find_node_by_weight(self, weight, order):
        # Find the node with the same weight that has the highest order (largest order value)
        # among those whose order is greater than the given order.
        candidate = None
        for node in self.nodes:
            if node.weight == weight and node.order > order:
                if candidate is None or node.order > candidate.order:
                    candidate = node
        return candidate

    def swap_nodes(self, node1, node2):
        # Swap positions of node1 and node2 in the tree, including updating parents and order.
        if node1.parent is None or node2.parent is None:
            return

        # Swap parent's child pointers.
        if node1.parent.left == node1:
            node1.parent.left = node2
        else:
            node1.parent.right = node2

        if node2.parent.left == node2:
            node2.parent.left = node1
        else:
            node2.parent.right = node1

        # Swap parent pointers.
        node1.parent, node2.parent = node2.parent, node1.parent

        # Swap the order numbers.
        node1.order, node2.order = node2.order, node1.order

    def update_tree(self, node):
        # Update the tree starting from the given node up to the root.
        while node:
            leader = self.find_node_by_weight(node.weight, node.order)
            if leader is not None and leader != node.parent and leader != node:
                self.swap_nodes(node, leader)
            node.weight += 1
            node = node.parent

    def insert(self, symbol):
        # Insert a new symbol into the tree by replacing the current NYT node.
        old_NYT = self.NYT
        # Create a new internal node to replace NYT.
        new_internal = Node(0, old_NYT.order, None, old_NYT.parent)
        # Create new leaf for the symbol.
        new_leaf = Node(1, old_NYT.order - 1, symbol, new_internal)
        # Create a new NYT node.
        new_NYT = Node(0, old_NYT.order - 2, None, new_internal)
        new_internal.left = new_NYT
        new_internal.right = new_leaf

        # Update the parent's pointer.
        if old_NYT.parent:
            if old_NYT.parent.left == old_NYT:
                old_NYT.parent.left = new_internal
            else:
                old_NYT.parent.right = new_internal
        else:
            self.root = new_internal

        # Remove the old NYT node and add the new nodes.
        self.nodes.remove(old_NYT)
        self.nodes.append(new_internal)
        self.nodes.append(new_leaf)
        self.nodes.append(new_NYT)

        # Store the new leaf for the symbol.
        self.leaves[symbol] = new_leaf

        # Update the NYT pointer.
        self.NYT = new_NYT

        # Update the tree weights starting from the new internal node.
        self.update_tree(new_internal)
        return new_leaf

    def get_symbol_node(self, symbol):
        return self.leaves.get(symbol, None)

    def traverse(self, bits):
        current = self.root
        consumed = 0
        for bit in bits:
            if bit == "0":
                current = current.left
            else:
                current = current.right
            consumed += 1
            if current.is_leaf():
                break
        return current, consumed


def encode(input_str):
    tree = AdaptiveHuffmanTree()
    output = ""
    for ch in input_str:
        node = tree.get_symbol_node(ch)
        if node is None:
            # If the symbol is new, output the code for the NYT node
            # followed by the fixed 8-bit ASCII representation of the symbol.
            code = tree.get_code(tree.NYT)
            fixed = format(ord(ch), "08b")
            output += code + fixed
            tree.insert(ch)
        else:
            # If the symbol is already in the tree, output its code.
            code = tree.get_code(node)
            output += code
            tree.update_tree(node)
    return output


def decode(bitstring):
    tree = AdaptiveHuffmanTree()
    output = ""
    i = 0
    while i < len(bitstring):
        current = tree.root
        if current.is_leaf():
            # Tree contains only NYT node, so read next 8 bits for the new symbol.
            if i + 8 > len(bitstring):
                break
            fixed = bitstring[i:i + 8]
            i += 8
            ch = chr(int(fixed, 2))
            output += ch
            tree.insert(ch)
        else:
            # Traverse the tree using the bitstring.
            while not current.is_leaf() and i < len(bitstring):
                bit = bitstring[i]
                i += 1
                if bit == "0":
                    current = current.left
                else:
                    current = current.right
            if current == tree.NYT:
                # If the NYT node is reached, the next 8 bits define a new symbol.
                if i + 8 > len(bitstring):
                    break
                fixed = bitstring[i:i + 8]
                i += 8
                ch = chr(int(fixed, 2))
                output += ch
                tree.insert(ch)
            else:
                # Existing symbol found.
                output += current.symbol
                tree.update_tree(current)
    return output
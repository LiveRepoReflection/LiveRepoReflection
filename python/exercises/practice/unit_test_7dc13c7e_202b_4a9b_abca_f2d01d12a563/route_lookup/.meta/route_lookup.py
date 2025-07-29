def ip_to_int(ip):
    parts = ip.split('.')
    return (int(parts[0]) << 24) | (int(parts[1]) << 16) | (int(parts[2]) << 8) | int(parts[3])

class TrieNode:
    __slots__ = 'children', 'next_hop'
    def __init__(self):
        self.children = [None, None]
        self.next_hop = None

class RouteTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, ip_int, prefix_length, next_hop):
        node = self.root
        for i in range(31, 31 - prefix_length, -1):
            bit = (ip_int >> i) & 1
            if node.children[bit] is None:
                node.children[bit] = TrieNode()
            node = node.children[bit]
        # Assign the next hop for this prefix
        node.next_hop = next_hop

    def search(self, ip_int):
        node = self.root
        best_match = None
        for i in range(31, -1, -1):
            if node.next_hop is not None:
                best_match = node.next_hop
            bit = (ip_int >> i) & 1
            if node.children[bit] is None:
                break
            node = node.children[bit]
        if node is not None and node.next_hop is not None:
            best_match = node.next_hop
        return best_match

def find_best_route(routing_table, destination_ip):
    """
    Given a routing_table (list of tuples: (prefix, next_hop)) and a destination_ip,
    returns the next_hop determined by longest prefix match.
    If no route matches, returns None.
    """
    trie = RouteTrie()
    # Build the trie from the routing table entries.
    for prefix, next_hop in routing_table:
        ip_part, length_str = prefix.split('/')
        prefix_length = int(length_str)
        ip_int = ip_to_int(ip_part)
        trie.insert(ip_int, prefix_length, next_hop)
    dest_int = ip_to_int(destination_ip)
    return trie.search(dest_int)

if __name__ == "__main__":
    # Simple manual test
    routing_table = [
        ("10.0.0.0/8", "192.168.1.1"),
        ("10.1.0.0/16", "192.168.2.1"),
        ("10.1.2.0/24", "192.168.3.1"),
        ("0.0.0.0/0", "192.168.0.1"),
    ]
    destination_ip = "10.1.2.3"
    print(find_best_route(routing_table, destination_ip))
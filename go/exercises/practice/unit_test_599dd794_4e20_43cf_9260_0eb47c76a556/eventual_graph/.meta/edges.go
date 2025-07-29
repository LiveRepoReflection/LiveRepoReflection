package eventual_graph

func InitializeGraph() (map[string]Node, map[string][]string) {
	graph := make(map[string]Node)
	edges := make(map[string][]string)
	return graph, edges
}

func AddNode(graph map[string]Node, id string, version int, data string) {
	graph[id] = Node{
		ID:      id,
		Version: version,
		Data:    data,
	}
}

func AddEdge(edges map[string][]string, from string, to string) {
	if _, exists := edges[from]; !exists {
		edges[from] = []string{}
	}
	edges[from] = append(edges[from], to)
}
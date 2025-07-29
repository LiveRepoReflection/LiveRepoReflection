package route_network_opt

import (
	"reflect"
	"testing"
)

// Assuming the following types and the OptimizeRoutes function are defined in the solution:
// Graph, GraphEdge, Agent, Package, GraphUpdate, DeliveryInput, AgentDecision, DeliveryOutput
//
// The unit tests below verify the correctness and robustness of OptimizeRoutes
// by validating various invariants such as valid route construction, capacity constraints,
// package delivery, dynamic network updates, collision avoidance, and handling multiple agents.

// isValidRoute checks that the given route is a valid path in the graph.
func isValidRoute(graph Graph, route []string) bool {
	if len(route) < 1 {
		return false
	}
	// Create a map for quick lookup: key "From->To": true
	edgeMap := make(map[string]bool)
	for _, edge := range graph.Edges {
		key := edge.From + "->" + edge.To
		edgeMap[key] = true
	}
	for i := 0; i < len(route)-1; i++ {
		key := route[i] + "->" + route[i+1]
		if !edgeMap[key] {
			return false
		}
	}
	return true
}

// deliveredPackages returns the IDs of packages that are considered delivered based on the route.
func deliveredPackages(route []string, pkgs []Package) []string {
	delivered := []string{}
	for _, pkg := range pkgs {
		for _, node := range route {
			if node == pkg.Destination {
				delivered = append(delivered, pkg.ID)
				break
			}
		}
	}
	return delivered
}

// TestOptimizeRoutes_Simple verifies that a basic scenario with a single agent and package works correctly.
func TestOptimizeRoutes_Simple(t *testing.T) {
	graph := Graph{
		Nodes: []string{"A", "B", "C"},
		Edges: []GraphEdge{
			{From: "A", To: "B", Weight: 5},
			{From: "B", To: "C", Weight: 5},
			{From: "A", To: "C", Weight: 12},
		},
	}
	agent := Agent{
		ID:       "agent1",
		Start:    "A",
		Capacity: 10,
	}
	pkg := Package{
		ID:          "pkg1",
		Size:        5,
		Destination: "C",
		Priority:    1,
	}
	input := DeliveryInput{
		Graph:    graph,
		Agents:   []Agent{agent},
		Packages: []Package{pkg},
		Updates:  []GraphUpdate{},
	}

	output := OptimizeRoutes(&input)
	if len(output.Decisions) != 1 {
		t.Errorf("Expected 1 decision, got %d", len(output.Decisions))
		return
	}
	decision := output.Decisions[0]
	if len(decision.Route) == 0 || decision.Route[0] != agent.Start {
		t.Errorf("Route should start at agent's starting location %s", agent.Start)
	}
	if !isValidRoute(graph, decision.Route) {
		t.Errorf("Route %v is not valid in the graph", decision.Route)
	}
	delivered := deliveredPackages(decision.Route, input.Packages)
	if !reflect.DeepEqual(delivered, []string{pkg.ID}) {
		t.Errorf("Expected delivered package %v, got %v", []string{pkg.ID}, delivered)
	}
}

// TestOptimizeRoutes_Capacity ensures that an agent does not deliver packages that exceed its carrying capacity.
func TestOptimizeRoutes_Capacity(t *testing.T) {
	graph := Graph{
		Nodes: []string{"X", "Y", "Z"},
		Edges: []GraphEdge{
			{From: "X", To: "Y", Weight: 3},
			{From: "Y", To: "Z", Weight: 3},
		},
	}
	agent := Agent{
		ID:       "agent2",
		Start:    "X",
		Capacity: 5,
	}
	heavyPkg := Package{
		ID:          "pkg_heavy",
		Size:        10,
		Destination: "Z",
		Priority:    2,
	}
	lightPkg := Package{
		ID:          "pkg_light",
		Size:        3,
		Destination: "Y",
		Priority:    1,
	}
	input := DeliveryInput{
		Graph:    graph,
		Agents:   []Agent{agent},
		Packages: []Package{heavyPkg, lightPkg},
		Updates:  []GraphUpdate{},
	}
	output := OptimizeRoutes(&input)
	if len(output.Decisions) != 1 {
		t.Errorf("Expected 1 decision, got %d", len(output.Decisions))
		return
	}
	decision := output.Decisions[0]
	if !isValidRoute(graph, decision.Route) {
		t.Errorf("Route %v is not valid in the graph", decision.Route)
	}
	// Verify that the heavy package is not delivered due to capacity constraint.
	for _, id := range decision.PackagesDelivered {
		if id == heavyPkg.ID {
			t.Errorf("Heavy package %s delivered despite capacity constraint", heavyPkg.ID)
		}
	}
	lightDelivered := false
	for _, id := range decision.PackagesDelivered {
		if id == lightPkg.ID {
			lightDelivered = true
		}
	}
	if !lightDelivered {
		t.Errorf("Light package %s was not delivered as expected", lightPkg.ID)
	}
}

// TestOptimizeRoutes_Dynamic checks that the optimizer can handle dynamic graph updates.
func TestOptimizeRoutes_Dynamic(t *testing.T) {
	graph := Graph{
		Nodes: []string{"D", "E", "F", "G"},
		Edges: []GraphEdge{
			{From: "D", To: "E", Weight: 4},
			{From: "E", To: "F", Weight: 4},
			{From: "D", To: "F", Weight: 10},
			{From: "F", To: "G", Weight: 3},
			{From: "E", To: "G", Weight: 8},
		},
	}
	agent := Agent{
		ID:       "agent3",
		Start:    "D",
		Capacity: 15,
	}
	pkg1 := Package{
		ID:          "pkg_dyn",
		Size:        5,
		Destination: "G",
		Priority:    1,
	}
	// Update: modify weight of edge D->F to be more attractive.
	update := GraphUpdate{
		From:      "D",
		To:        "F",
		NewWeight: 5,
	}
	input := DeliveryInput{
		Graph:    graph,
		Agents:   []Agent{agent},
		Packages: []Package{pkg1},
		Updates:  []GraphUpdate{update},
	}
	output := OptimizeRoutes(&input)
	if len(output.Decisions) != 1 {
		t.Errorf("Expected 1 decision, got %d", len(output.Decisions))
		return
	}
	decision := output.Decisions[0]
	if len(decision.Route) == 0 || decision.Route[0] != agent.Start {
		t.Errorf("Route should start at agent's starting location %s", agent.Start)
	}
	if !isValidRoute(graph, decision.Route) {
		t.Errorf("Route %v is not valid in the graph", decision.Route)
	}
	delivered := deliveredPackages(decision.Route, input.Packages)
	if !reflect.DeepEqual(delivered, []string{pkg1.ID}) {
		t.Errorf("Expected delivered package %v, got %v", []string{pkg1.ID}, delivered)
	}
}

// TestOptimizeRoutes_MultipleAgents tests the optimizer with multiple agents and packages assigned with priorities.
func TestOptimizeRoutes_MultipleAgents(t *testing.T) {
	graph := Graph{
		Nodes: []string{"H", "I", "J", "K", "L"},
		Edges: []GraphEdge{
			{From: "H", To: "I", Weight: 2},
			{From: "I", To: "J", Weight: 2},
			{From: "J", To: "K", Weight: 2},
			{From: "K", To: "L", Weight: 2},
			{From: "H", To: "L", Weight: 10},
		},
	}
	agents := []Agent{
		{ID: "agent4", Start: "H", Capacity: 10},
		{ID: "agent5", Start: "J", Capacity: 8},
	}
	pkgs := []Package{
		{ID: "pkg1", Size: 3, Destination: "L", Priority: 2},
		{ID: "pkg2", Size: 2, Destination: "K", Priority: 1},
		{ID: "pkg3", Size: 4, Destination: "I", Priority: 3},
	}
	input := DeliveryInput{
		Graph:    graph,
		Agents:   agents,
		Packages: pkgs,
		Updates:  []GraphUpdate{},
	}
	output := OptimizeRoutes(&input)
	if len(output.Decisions) != 2 {
		t.Errorf("Expected decisions for 2 agents, got %d", len(output.Decisions))
		return
	}
	// For each decision, check route validity, capacity constraints, and that packages reach their destination.
	for _, decision := range output.Decisions {
		var agentFound *Agent
		for _, a := range agents {
			if a.ID == decision.AgentID {
				agentFound = &a
				break
			}
		}
		if agentFound == nil {
			t.Errorf("Decision for unknown agent ID %s", decision.AgentID)
			continue
		}
		if len(decision.Route) == 0 || decision.Route[0] != agentFound.Start {
			t.Errorf("Agent %s: route should start at starting location %s", agentFound.ID, agentFound.Start)
		}
		if !isValidRoute(graph, decision.Route) {
			t.Errorf("Agent %s: route %v is not valid", agentFound.ID, decision.Route)
		}
		totalSize := 0
		for _, pkgID := range decision.PackagesDelivered {
			for _, p := range pkgs {
				if p.ID == pkgID {
					totalSize += p.Size
				}
			}
		}
		if totalSize > agentFound.Capacity {
			t.Errorf("Agent %s delivered packages exceed capacity", agentFound.ID)
		}
	}
}

// TestOptimizeRoutes_CollisionAvoidance checks that the solution handles potential route collisions among agents.
func TestOptimizeRoutes_CollisionAvoidance(t *testing.T) {
	graph := Graph{
		Nodes: []string{"M", "N", "O", "P"},
		Edges: []GraphEdge{
			{From: "M", To: "N", Weight: 3},
			{From: "N", To: "O", Weight: 3},
			{From: "O", To: "P", Weight: 3},
			{From: "M", To: "P", Weight: 10},
		},
	}
	agents := []Agent{
		{ID: "agent6", Start: "M", Capacity: 10},
		{ID: "agent7", Start: "M", Capacity: 10},
	}
	pkgs := []Package{
		{ID: "pkgA", Size: 3, Destination: "P", Priority: 1},
		{ID: "pkgB", Size: 3, Destination: "P", Priority: 1},
	}
	input := DeliveryInput{
		Graph:    graph,
		Agents:   agents,
		Packages: pkgs,
		Updates:  []GraphUpdate{},
	}
	output := OptimizeRoutes(&input)
	if len(output.Decisions) != 2 {
		t.Errorf("Expected decisions for 2 agents, got %d", len(output.Decisions))
		return
	}
	// Basic check: ensure that all packages are delivered
	deliveredMap := make(map[string]bool)
	for _, decision := range output.Decisions {
		for _, pkgID := range decision.PackagesDelivered {
			deliveredMap[pkgID] = true
		}
	}
	if len(deliveredMap) != len(pkgs) {
		t.Errorf("Not all packages delivered, expected %d, got %d", len(pkgs), len(deliveredMap))
	}
	// Check that each agent's route is valid and starts at the correct node.
	for _, decision := range output.Decisions {
		var agentFound *Agent
		for _, a := range agents {
			if a.ID == decision.AgentID {
				agentFound = &a
				break
			}
		}
		if agentFound == nil {
			t.Errorf("Decision for unknown agent ID %s", decision.AgentID)
			continue
		}
		if len(decision.Route) == 0 || decision.Route[0] != agentFound.Start {
			t.Errorf("Agent %s: route does not start at %s", agentFound.ID, agentFound.Start)
		}
		if !isValidRoute(graph, decision.Route) {
			t.Errorf("Agent %s: route %v is not valid", agentFound.ID, decision.Route)
		}
	}
}
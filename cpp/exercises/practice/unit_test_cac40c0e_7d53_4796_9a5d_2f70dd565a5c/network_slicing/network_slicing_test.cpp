#include "network_slicing.h"
#include "catch.hpp"
#include <vector>
#include <unordered_map>

using namespace std;

struct TestCase {
    string name;
    PhysicalNetwork physical;
    vector<NetworkSlice> slices;
    int expected_revenue;
};

// Helper function to create a physical network node
PhysicalNode createPhysicalNode(int cpu, int memory, int bandwidth) {
    PhysicalNode node;
    node.cpu = cpu;
    node.memory = memory;
    node.bandwidth = bandwidth;
    return node;
}

// Helper function to create a physical network edge
PhysicalEdge createPhysicalEdge(int bandwidth, int latency) {
    PhysicalEdge edge;
    edge.bandwidth = bandwidth;
    edge.latency = latency;
    return edge;
}

// Helper function to create a virtual node
VirtualNode createVirtualNode(int cpu, int memory, int bandwidth) {
    VirtualNode node;
    node.cpu = cpu;
    node.memory = memory;
    node.bandwidth = bandwidth;
    return node;
}

// Helper function to create a virtual edge
VirtualEdge createVirtualEdge(int bandwidth) {
    VirtualEdge edge;
    edge.bandwidth = bandwidth;
    return edge;
}

TEST_CASE("Empty physical network returns zero revenue") {
    PhysicalNetwork physical;
    vector<NetworkSlice> slices = {NetworkSlice()};
    
    auto result = network_slicing::optimize_network_slicing(physical, slices);
    
    REQUIRE(result.revenue == 0);
    REQUIRE(result.mappings.empty());
}

TEST_CASE("Empty slice list returns zero revenue") {
    PhysicalNetwork physical;
    physical.nodes = {createPhysicalNode(100, 100, 100)};
    vector<NetworkSlice> slices;
    
    auto result = network_slicing::optimize_network_slicing(physical, slices);
    
    REQUIRE(result.revenue == 0);
    REQUIRE(result.mappings.empty());
}

TEST_CASE("Single slice with single node") {
    PhysicalNetwork physical;
    physical.nodes = {createPhysicalNode(100, 100, 100)};
    
    NetworkSlice slice;
    slice.nodes = {createVirtualNode(50, 50, 50)};
    slice.revenue = 1000;
    vector<NetworkSlice> slices = {slice};
    
    auto result = network_slicing::optimize_network_slicing(physical, slices);
    
    REQUIRE(result.revenue == 1000);
    REQUIRE(result.mappings.size() == 1);
}

TEST_CASE("Slice with insufficient resources") {
    PhysicalNetwork physical;
    physical.nodes = {createPhysicalNode(40, 40, 40)};
    
    NetworkSlice slice;
    slice.nodes = {createVirtualNode(50, 50, 50)};
    slice.revenue = 1000;
    vector<NetworkSlice> slices = {slice};
    
    auto result = network_slicing::optimize_network_slicing(physical, slices);
    
    REQUIRE(result.revenue == 0);
    REQUIRE(result.mappings.empty());
}

TEST_CASE("Multiple slices with resource competition") {
    PhysicalNetwork physical;
    physical.nodes = {
        createPhysicalNode(100, 100, 100),
        createPhysicalNode(100, 100, 100)
    };
    physical.edges = {{0, 1, createPhysicalEdge(100, 1)}};
    
    NetworkSlice slice1;
    slice1.nodes = {
        createVirtualNode(60, 60, 60),
        createVirtualNode(60, 60, 60)
    };
    slice1.edges = {{0, 1, createVirtualEdge(70)}};
    slice1.revenue = 1000;
    
    NetworkSlice slice2;
    slice2.nodes = {
        createVirtualNode(50, 50, 50),
        createVirtualNode(50, 50, 50)
    };
    slice2.edges = {{0, 1, createVirtualEdge(60)}};
    slice2.revenue = 800;
    
    vector<NetworkSlice> slices = {slice1, slice2};
    
    auto result = network_slicing::optimize_network_slicing(physical, slices);
    
    REQUIRE(result.revenue > 0);
    REQUIRE(result.mappings.size() > 0);
}

TEST_CASE("Latency constraints") {
    PhysicalNetwork physical;
    physical.nodes = {
        createPhysicalNode(100, 100, 100),
        createPhysicalNode(100, 100, 100),
        createPhysicalNode(100, 100, 100)
    };
    physical.edges = {
        {0, 1, createPhysicalEdge(100, 5)},
        {1, 2, createPhysicalEdge(100, 5)}
    };
    
    NetworkSlice slice;
    slice.nodes = {
        createVirtualNode(50, 50, 50),
        createVirtualNode(50, 50, 50)
    };
    slice.edges = {{0, 1, createVirtualEdge(50)}};
    slice.latency_requirements = {{0, 1, 8}};
    slice.revenue = 1000;
    
    vector<NetworkSlice> slices = {slice};
    
    auto result = network_slicing::optimize_network_slicing(physical, slices);
    
    REQUIRE(result.revenue == 1000);
    REQUIRE(result.mappings.size() == 1);
}

TEST_CASE("Disconnected physical network") {
    PhysicalNetwork physical;
    physical.nodes = {
        createPhysicalNode(100, 100, 100),
        createPhysicalNode(100, 100, 100)
    };
    // No edges between nodes
    
    NetworkSlice slice;
    slice.nodes = {
        createVirtualNode(50, 50, 50),
        createVirtualNode(50, 50, 50)
    };
    slice.edges = {{0, 1, createVirtualEdge(50)}};
    slice.revenue = 1000;
    
    vector<NetworkSlice> slices = {slice};
    
    auto result = network_slicing::optimize_network_slicing(physical, slices);
    
    REQUIRE(result.revenue == 0);
    REQUIRE(result.mappings.empty());
}

TEST_CASE("Zero resource requirements") {
    PhysicalNetwork physical;
    physical.nodes = {createPhysicalNode(0, 0, 0)};
    
    NetworkSlice slice;
    slice.nodes = {createVirtualNode(0, 0, 0)};
    slice.revenue = 1000;
    vector<NetworkSlice> slices = {slice};
    
    auto result = network_slicing::optimize_network_slicing(physical, slices);
    
    REQUIRE(result.revenue == 1000);
    REQUIRE(result.mappings.size() == 1);
}

TEST_CASE("Complex network with multiple valid solutions") {
    PhysicalNetwork physical;
    // Create a grid of 3x3 nodes
    for (int i = 0; i < 9; i++) {
        physical.nodes.push_back(createPhysicalNode(100, 100, 100));
    }
    
    // Add edges in grid pattern
    for (int i = 0; i < 3; i++) {
        for (int j = 0; j < 3; j++) {
            if (j < 2) { // Horizontal edges
                physical.edges.push_back({i*3+j, i*3+j+1, createPhysicalEdge(100, 1)});
            }
            if (i < 2) { // Vertical edges
                physical.edges.push_back({i*3+j, (i+1)*3+j, createPhysicalEdge(100, 1)});
            }
        }
    }
    
    vector<NetworkSlice> slices;
    // Create three competing slices
    for (int i = 0; i < 3; i++) {
        NetworkSlice slice;
        slice.nodes = {
            createVirtualNode(40, 40, 40),
            createVirtualNode(40, 40, 40),
            createVirtualNode(40, 40, 40)
        };
        slice.edges = {
            {0, 1, createVirtualEdge(30)},
            {1, 2, createVirtualEdge(30)}
        };
        slice.latency_requirements = {
            {0, 2, 4}  // End-to-end latency requirement
        };
        slice.revenue = 1000 + i * 100;  // Different revenues
        slices.push_back(slice);
    }
    
    auto result = network_slicing::optimize_network_slicing(physical, slices);
    
    REQUIRE(result.revenue > 0);
    REQUIRE(result.mappings.size() > 0);
}
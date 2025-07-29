#include "catch.hpp"
#include "cloud_optimize.h"
#include <vector>
#include <tuple>

using namespace std;

TEST_CASE("Example test case") {
    int num_data_centers = 4;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10}, {1, 2, 15}, {2, 3, 20}, {0, 3, 25}
    };
    int source_data_center = 0;
    int destination_data_center = 3;
    int max_upgrades = 1;
    int upgrade_reduction = 5;
    vector<int> critical_vms = {1};
    vector<int> vm_data_center = {0, 1, 2};

    REQUIRE(cloud_optimize::min_latency(num_data_centers, edges, source_data_center, 
                                      destination_data_center, max_upgrades, 
                                      upgrade_reduction, critical_vms, vm_data_center) == 20);
}

TEST_CASE("No upgrades needed") {
    int num_data_centers = 3;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 5}, {1, 2, 5}, {0, 2, 10}
    };
    int source_data_center = 0;
    int destination_data_center = 2;
    int max_upgrades = 0;
    int upgrade_reduction = 5;
    vector<int> critical_vms = {};
    vector<int> vm_data_center = {};

    REQUIRE(cloud_optimize::min_latency(num_data_centers, edges, source_data_center, 
                                      destination_data_center, max_upgrades, 
                                      upgrade_reduction, critical_vms, vm_data_center) == 10);
}

TEST_CASE("Multiple upgrades on the same edge") {
    int num_data_centers = 2;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 20}
    };
    int source_data_center = 0;
    int destination_data_center = 1;
    int max_upgrades = 3;
    int upgrade_reduction = 5;
    vector<int> critical_vms = {};
    vector<int> vm_data_center = {};

    REQUIRE(cloud_optimize::min_latency(num_data_centers, edges, source_data_center, 
                                      destination_data_center, max_upgrades, 
                                      upgrade_reduction, critical_vms, vm_data_center) == 5);
}

TEST_CASE("Source and destination are the same") {
    int num_data_centers = 3;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10}, {1, 2, 10}, {0, 2, 20}
    };
    int source_data_center = 1;
    int destination_data_center = 1;
    int max_upgrades = 2;
    int upgrade_reduction = 5;
    vector<int> critical_vms = {};
    vector<int> vm_data_center = {};

    REQUIRE(cloud_optimize::min_latency(num_data_centers, edges, source_data_center, 
                                      destination_data_center, max_upgrades, 
                                      upgrade_reduction, critical_vms, vm_data_center) == 0);
}

TEST_CASE("Reducing edge weight to zero") {
    int num_data_centers = 3;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 5}, {1, 2, 10}, {0, 2, 20}
    };
    int source_data_center = 0;
    int destination_data_center = 2;
    int max_upgrades = 2;
    int upgrade_reduction = 10;
    vector<int> critical_vms = {};
    vector<int> vm_data_center = {};

    REQUIRE(cloud_optimize::min_latency(num_data_centers, edges, source_data_center, 
                                      destination_data_center, max_upgrades, 
                                      upgrade_reduction, critical_vms, vm_data_center) == 0);
}

TEST_CASE("Complex network with critical VMs") {
    int num_data_centers = 5;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10}, {1, 2, 20}, {2, 3, 15}, {3, 4, 10}, 
        {0, 4, 50}, {0, 2, 30}, {1, 3, 25}
    };
    int source_data_center = 0;
    int destination_data_center = 4;
    int max_upgrades = 2;
    int upgrade_reduction = 10;
    vector<int> critical_vms = {0, 2};
    vector<int> vm_data_center = {1, 0, 2, 3};

    REQUIRE(cloud_optimize::min_latency(num_data_centers, edges, source_data_center, 
                                      destination_data_center, max_upgrades, 
                                      upgrade_reduction, critical_vms, vm_data_center) == 30);
}

TEST_CASE("Large network with multiple critical VMs") {
    int num_data_centers = 6;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 10}, {1, 2, 20}, {2, 3, 15}, {3, 4, 10}, {4, 5, 25},
        {0, 5, 100}, {0, 2, 40}, {1, 4, 50}, {1, 3, 30}, {2, 5, 70}
    };
    int source_data_center = 0;
    int destination_data_center = 5;
    int max_upgrades = 3;
    int upgrade_reduction = 15;
    vector<int> critical_vms = {1, 3, 5};
    vector<int> vm_data_center = {0, 1, 2, 2, 3, 4};

    REQUIRE(cloud_optimize::min_latency(num_data_centers, edges, source_data_center, 
                                      destination_data_center, max_upgrades, 
                                      upgrade_reduction, critical_vms, vm_data_center) == 55);
}

TEST_CASE("Maximum allowed upgrades") {
    int num_data_centers = 4;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 100}, {1, 2, 100}, {2, 3, 100}
    };
    int source_data_center = 0;
    int destination_data_center = 3;
    int max_upgrades = 6;
    int upgrade_reduction = 50;
    vector<int> critical_vms = {};
    vector<int> vm_data_center = {};

    REQUIRE(cloud_optimize::min_latency(num_data_centers, edges, source_data_center, 
                                      destination_data_center, max_upgrades, 
                                      upgrade_reduction, critical_vms, vm_data_center) == 0);
}

TEST_CASE("No available upgrades") {
    int num_data_centers = 3;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 15}, {1, 2, 20}, {0, 2, 30}
    };
    int source_data_center = 0;
    int destination_data_center = 2;
    int max_upgrades = 0;
    int upgrade_reduction = 10;
    vector<int> critical_vms = {0};
    vector<int> vm_data_center = {1};

    REQUIRE(cloud_optimize::min_latency(num_data_centers, edges, source_data_center, 
                                      destination_data_center, max_upgrades, 
                                      upgrade_reduction, critical_vms, vm_data_center) == 30);
}

TEST_CASE("Critical VM paths vs direct paths") {
    int num_data_centers = 4;
    vector<tuple<int, int, int>> edges = {
        {0, 1, 5}, {1, 2, 5}, {2, 3, 5}, {0, 3, 20}
    };
    int source_data_center = 0;
    int destination_data_center = 3;
    int max_upgrades = 1;
    int upgrade_reduction = 10;
    vector<int> critical_vms = {0, 1};
    vector<int> vm_data_center = {1, 2};

    REQUIRE(cloud_optimize::min_latency(num_data_centers, edges, source_data_center, 
                                      destination_data_center, max_upgrades, 
                                      upgrade_reduction, critical_vms, vm_data_center) == 10);
}
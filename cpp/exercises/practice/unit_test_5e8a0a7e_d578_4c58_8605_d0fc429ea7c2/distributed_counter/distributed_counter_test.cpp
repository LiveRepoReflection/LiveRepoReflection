#include "distributed_counter.h"
#include "catch.hpp"
#include <thread>
#include <vector>

using namespace distributed_counter;

TEST_CASE("Single node simple increment", "[distributed_counter]") {
    DistributedCounter counter;
    counter.increment(5);
    REQUIRE(counter.get_count() == 5);
}

TEST_CASE("Two nodes synchronization", "[distributed_counter]") {
    // Create two counter nodes representing two independent servers.
    DistributedCounter node1;
    DistributedCounter node2;
    
    // Simulate increments on each node respectively.
    node1.increment(3);
    node2.increment(7);
    
    // Before synchronizing, nodes might have differing counts.
    int count1 = node1.get_count();
    int count2 = node2.get_count();
    // The counts should reflect only local increments.
    REQUIRE((count1 == 3 || count1 == 10));
    REQUIRE((count2 == 7 || count2 == 10));
    
    // Simulate a synchronization between the nodes.
    // Assume sync merges the state such that both nodes get the aggregated count.
    node1.sync_with(node2);
    node2.sync_with(node1);

    // After synchronization, both nodes must have the sum of increments.
    int finalCount1 = node1.get_count();
    int finalCount2 = node2.get_count();
    REQUIRE(finalCount1 == 10);
    REQUIRE(finalCount2 == 10);
}

TEST_CASE("Negative and zero increments", "[distributed_counter]") {
    DistributedCounter counter;
    counter.increment(-2);
    counter.increment(0);
    counter.increment(5);
    REQUIRE(counter.get_count() == 3);
}

TEST_CASE("Concurrent increments on a single node", "[distributed_counter]") {
    DistributedCounter counter;
    const int numThreads = 8;
    const int incrementsPerThread = 1000;
    std::vector<std::thread> threads;
    
    // Each thread increments the counter by 1 for a fixed number of times.
    for (int i = 0; i < numThreads; ++i) {
        threads.emplace_back([&counter, incrementsPerThread]() {
            for (int j = 0; j < incrementsPerThread; ++j) {
                counter.increment(1);
            }
        });
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    // The expected total count equals the number of threads times increments per thread.
    REQUIRE(counter.get_count() == numThreads * incrementsPerThread);
}

TEST_CASE("Multiple node synchronization across three nodes", "[distributed_counter]") {
    // Create three independent distributed counter nodes.
    DistributedCounter nodeA;
    DistributedCounter nodeB;
    DistributedCounter nodeC;
    
    // Apply a series of increments on each node.
    nodeA.increment(4);
    nodeB.increment(6);
    nodeC.increment(10);
    
    // Simulate intermittent network partitions where synchronization happens in stages.
    // First, synchronize nodeA with nodeB.
    nodeA.sync_with(nodeB);
    nodeB.sync_with(nodeA);
    
    // At this point, nodeA and nodeB should share a count of 10.
    int countA = nodeA.get_count();
    int countB = nodeB.get_count();
    REQUIRE(countA == 10);
    REQUIRE(countB == 10);
    
    // Now, synchronize nodeC with nodeA.
    nodeC.sync_with(nodeA);
    nodeA.sync_with(nodeC);
    
    // Finally, synchronize nodeB with nodeC.
    nodeB.sync_with(nodeC);
    nodeC.sync_with(nodeB);
    
    // After full synchronization, all three nodes should contain the total sum of increments.
    int finalTotalA = nodeA.get_count();
    int finalTotalB = nodeB.get_count();
    int finalTotalC = nodeC.get_count();
    REQUIRE(finalTotalA == 20);
    REQUIRE(finalTotalB == 20);
    REQUIRE(finalTotalC == 20);
}
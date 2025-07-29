#include "catch.hpp"
#include "tx_validation.h"
#include <sstream>
#include <string>

using namespace std;

namespace tx_validation {
    // Declaration of the solve function.
    // It reads from an input stream and writes the result to an output stream.
    void solve(istream &in, ostream &out);
}

TEST_CASE("Single transaction with one operation", "[tx_validation]") {
    // Cluster: 2 nodes, 2 data items, 1 transaction with a single READ
    string input = "2\n2\n1\n1\nREAD 0 x\n";
    stringstream in(input);
    stringstream out;
    
    tx_validation::solve(in, out);
    
    // Only one transaction commit is possible.
    string result = out.str();
    int maxCommit = stoi(result);
    REQUIRE(maxCommit == 1);
}

TEST_CASE("Two conflicting transactions", "[tx_validation]") {
    // Cluster: 1 node, 1 data item, 2 transactions that conflict on the same data item.
    // Transaction 1: READ 0 x, WRITE 0 x 10
    // Transaction 2: WRITE 0 x 20, READ 0 x
    string input = 
        "1\n"  // N: 1 node
        "1\n"  // M: 1 data item
        "2\n"  // T: 2 transactions
        "2\n"  // Transaction 1: 2 operations
        "READ 0 x\n"
        "WRITE 0 x 10\n"
        "2\n"  // Transaction 2: 2 operations
        "WRITE 0 x 20\n"
        "READ 0 x\n";
        
    stringstream in(input);
    stringstream out;
    tx_validation::solve(in, out);
    
    // They conflict so maximum serializable transactions is 1.
    string result = out.str();
    int maxCommit = stoi(result);
    REQUIRE(maxCommit == 1);
}

TEST_CASE("Two non-conflicting transactions", "[tx_validation]") {
    // Cluster: 2 nodes, 2 data items, 2 transactions that are independent.
    // Transaction 1: READ 0 x, WRITE 0 x 10
    // Transaction 2: READ 1 y, WRITE 1 y 20
    string input =
        "2\n" // N: 2 nodes
        "2\n" // M: 2 data items
        "2\n" // T: 2 transactions
        "2\n" // Transaction 1: 2 operations
        "READ 0 x\n"
        "WRITE 0 x 10\n"
        "2\n" // Transaction 2: 2 operations
        "READ 1 y\n"
        "WRITE 1 y 20\n";
    
    stringstream in(input);
    stringstream out;
    tx_validation::solve(in, out);
    
    // Both transactions can commit.
    string result = out.str();
    int maxCommit = stoi(result);
    REQUIRE(maxCommit == 2);
}

TEST_CASE("Three transactions with partial conflicts", "[tx_validation]") {
    // Cluster: 1 node, 2 data items, 3 transactions.
    // Transaction 1: READ 0 x, WRITE 0 x 10
    // Transaction 2: READ 0 y, WRITE 0 y 20
    // Transaction 3: WRITE 0 x 30
    // Transactions 1 and 3 conflict on data item x.
    // Serializability allows either {T1, T2} or {T2, T3} as a valid set.
    // Therefore maximum serializable transactions = 2.
    string input =
        "1\n" // N: 1 node
        "2\n" // M: 2 data items
        "3\n" // T: 3 transactions
        "2\n" // Transaction 1: 2 operations
        "READ 0 x\n"
        "WRITE 0 x 10\n"
        "2\n" // Transaction 2: 2 operations
        "READ 0 y\n"
        "WRITE 0 y 20\n"
        "1\n" // Transaction 3: 1 operation
        "WRITE 0 x 30\n";
    
    stringstream in(input);
    stringstream out;
    tx_validation::solve(in, out);
    
    string result = out.str();
    int maxCommit = stoi(result);
    REQUIRE(maxCommit == 2);
}

TEST_CASE("Complex conflict scenario", "[tx_validation]") {
    // Cluster: 1 node, 3 data items, 5 transactions.
    // Transaction 1: READ 0 a, WRITE 0 a 5
    // Transaction 2: WRITE 0 b 10
    // Transaction 3: READ 0 a, WRITE 0 c 15
    // Transaction 4: WRITE 0 c 20
    // Transaction 5: READ 0 b, WRITE 0 b 25
    //
    // Conflicts:
    // - T1 and T3 conflict on data item a.
    // - T3 and T4 conflict on data item c.
    // - T2 and T5 conflict on data item b.
    // A maximum serializable subset can include T1, T2, and T4.
    // Therefore the expected maximum number is 3.
    string input =
        "1\n"   // N: 1 node
        "3\n"   // M: 3 data items
        "5\n"   // T: 5 transactions
        "2\n"   // Transaction 1: 2 operations
        "READ 0 a\n"
        "WRITE 0 a 5\n"
        "1\n"   // Transaction 2: 1 operation
        "WRITE 0 b 10\n"
        "2\n"   // Transaction 3: 2 operations
        "READ 0 a\n"
        "WRITE 0 c 15\n"
        "1\n"   // Transaction 4: 1 operation
        "WRITE 0 c 20\n"
        "2\n"   // Transaction 5: 2 operations
        "READ 0 b\n"
        "WRITE 0 b 25\n";
    
    stringstream in(input);
    stringstream out;
    tx_validation::solve(in, out);
    
    string result = out.str();
    int maxCommit = stoi(result);
    REQUIRE(maxCommit == 3);
}
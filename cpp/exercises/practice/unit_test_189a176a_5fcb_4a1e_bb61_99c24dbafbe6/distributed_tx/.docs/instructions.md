Okay, here's a problem designed to be challenging, requiring sophisticated data structures, careful optimization, and consideration of real-world constraints.

## Question: Distributed Transaction Orchestration

**Description:**

You are tasked with designing and implementing a system for orchestrating distributed transactions across a network of microservices.  Each microservice manages its own independent data store (e.g., a database).  A transaction involves operations that *must* succeed or fail atomically across multiple microservices. To achieve this, you will implement a Two-Phase Commit (2PC) protocol with a central coordinator.

**System Architecture:**

*   **Microservices:** Represented by integer IDs (1, 2, 3, ...). Each microservice can perform a local "prepare" operation and a local "commit" or "rollback" operation.  The time each operation take (prepare, commit, rollback) is different for each service.
*   **Coordinator:** A central component (your program) responsible for initiating, coordinating, and finalizing transactions.
*   **Transaction:** Defined by a list of microservices involved and a unique transaction ID (a long integer). Each microservice must participate in at most one transaction at a time.

**Input:**

Your program will receive several types of commands via standard input:

1.  `ADD_SERVICE <service_id> <prepare_time> <commit_time> <rollback_time>`: Adds a new microservice to the system. `<service_id>` is a positive integer, `<prepare_time>`, `<commit_time>`, and `<rollback_time>` are positive integers representing the time, in milliseconds, taken for the respective operations.
2.  `BEGIN_TRANSACTION <transaction_id> <service_id_1> <service_id_2> ... <service_id_n>`:  Starts a new distributed transaction. `<transaction_id>` is a unique positive long integer. `<service_id_1>` to `<service_id_n>` are the IDs of the microservices involved in the transaction.  The order of service IDs matters.  If a service is already participating in another transaction, the command should be ignored.
3.  `COMMIT_TRANSACTION <transaction_id>`: Commits the specified transaction.
4.  `ROLLBACK_TRANSACTION <transaction_id>`: Rolls back the specified transaction.
5.  `GET_TRANSACTION_STATUS <transaction_id>`:  Queries the status of the specified transaction.

**Output:**

Your program should produce output to standard output for the following commands:

1.  `BEGIN_TRANSACTION`:  Output "OK" if the transaction is successfully initiated (all services were available). Output "ABORTED" if any of the services were unavailable (already participating in another transaction).
2.  `COMMIT_TRANSACTION`: Output the total time (in milliseconds) taken to commit the transaction across all involved microservices. Output "TRANSACTION_NOT_FOUND" if the transaction does not exist. If any service fails to commit, output "COMMIT_FAILED".
3.  `ROLLBACK_TRANSACTION`: Output the total time (in milliseconds) taken to rollback the transaction across all involved microservices. Output "TRANSACTION_NOT_FOUND" if the transaction does not exist. If any service fails to rollback, output "ROLLBACK_FAILED".
4.  `GET_TRANSACTION_STATUS`: Output one of the following:
    *   "IN_PROGRESS": The transaction is currently in progress (preparing, committing, or rolling back).
    *   "COMMITTED": The transaction has been successfully committed.
    *   "ROLLED_BACK": The transaction has been successfully rolled back.
    *   "NOT_FOUND": The transaction does not exist.
    *   "ABORTED": The transaction was aborted during the prepare phase (at least one service failed to prepare).

**Constraints:**

*   The number of microservices can be up to 10<sup>5</sup>.
*   The number of transactions can be up to 10<sup>5</sup>.
*   The number of microservices involved in a single transaction can be up to 100.
*   `service_id` and `transaction_id` are positive integers and can be up to 2<sup>63</sup> - 1.
*   `<prepare_time>`, `<commit_time>`, and `<rollback_time>` are positive integers and can be up to 10<sup>3</sup>.
*   The time taken for network communication between the coordinator and microservices is negligible and can be ignored.
*   All operations within a single microservice are sequential. A microservice cannot start a new prepare, commit, or rollback operation while another is in progress.
*   The time spent in coordinator operations is negligible compared to the microservice operation times.

**Optimization Requirements:**

*   Your solution must be efficient enough to handle the specified input sizes and constraints. Inefficient algorithms or data structures will likely result in Time Limit Exceeded (TLE) errors.
*   Consider using appropriate data structures to store and retrieve microservice and transaction information quickly.
*   Think about how to efficiently manage concurrency and avoid race conditions when multiple transactions are being processed.

**Example:**

```
ADD_SERVICE 1 10 20 30
ADD_SERVICE 2 15 25 35
BEGIN_TRANSACTION 12345 1 2
GET_TRANSACTION_STATUS 12345
COMMIT_TRANSACTION 12345
GET_TRANSACTION_STATUS 12345
```

**Expected Output (example):**

```
OK
IN_PROGRESS
45
COMMITTED
```

**Grading:**

Your solution will be evaluated based on correctness, efficiency, and code quality.  Test cases will include a variety of scenarios, including:

*   Simple transactions that commit successfully.
*   Transactions that are aborted due to service unavailability.
*   Transactions that are rolled back.
*   Large-scale transactions with many microservices.
*   Concurrent transactions.
*   Edge cases and error handling.
```cpp
#include <iostream>
#include <vector>
#include <unordered_map>
#include <string>
#include <sstream>
#include <algorithm>

using namespace std;

struct Microservice {
    long long prepare_time;
    long long commit_time;
    long long rollback_time;
    bool in_transaction;
};

struct Transaction {
    vector<long long> service_ids;
    string status;
};

int main() {
    unordered_map<long long, Microservice> services;
    unordered_map<long long, Transaction> transactions;

    string line;
    while (getline(cin, line)) {
        stringstream ss(line);
        string command;
        ss >> command;

        if (command == "ADD_SERVICE") {
            long long service_id, prepare_time, commit_time, rollback_time;
            ss >> service_id >> prepare_time >> commit_time >> rollback_time;
            services[service_id] = {prepare_time, commit_time, rollback_time, false};
        } else if (command == "BEGIN_TRANSACTION") {
            long long transaction_id;
            ss >> transaction_id;

            vector<long long> service_ids;
            long long service_id;
            bool aborted = false;
            while (ss >> service_id) {
                if (services.find(service_id) != services.end() && !services[service_id].in_transaction) {
                    service_ids.push_back(service_id);
                } else {
                    aborted = true;
                    break;
                }
            }

            if (aborted) {
                cout << "ABORTED" << endl;
            } else {
                for (long long id : service_ids) {
                    services[id].in_transaction = true;
                }
                transactions[transaction_id] = {service_ids, "IN_PROGRESS"};
                cout << "OK" << endl;
            }
        } else if (command == "COMMIT_TRANSACTION") {
            long long transaction_id;
            ss >> transaction_id;

            if (transactions.find(transaction_id) == transactions.end()) {
                cout << "TRANSACTION_NOT_FOUND" << endl;
            } else {
                long long total_time = 0;
                bool commit_failed = false;
                for (long long id : transactions[transaction_id].service_ids) {
                    if (services.find(id) != services.end()) {
                        total_time += services[id].commit_time;
                    } else {
                        commit_failed = true;
                        break;
                    }
                }

                if (commit_failed) {
                    cout << "COMMIT_FAILED" << endl;
                } else {
                    cout << total_time << endl;
                    transactions[transaction_id].status = "COMMITTED";
                    for (long long id : transactions[transaction_id].service_ids) {
                        services[id].in_transaction = false;
                    }
                }
            }
        } else if (command == "ROLLBACK_TRANSACTION") {
            long long transaction_id;
            ss >> transaction_id;

            if (transactions.find(transaction_id) == transactions.end()) {
                cout << "TRANSACTION_NOT_FOUND" << endl;
            } else {
                long long total_time = 0;
                bool rollback_failed = false;
                for (long long id : transactions[transaction_id].service_ids) {
                    if (services.find(id) != services.end()) {
                        total_time += services[id].rollback_time;
                    } else {
                        rollback_failed = true;
                        break;
                    }
                }

                if (rollback_failed) {
                    cout << "ROLLBACK_FAILED" << endl;
                } else {
                    cout << total_time << endl;
                    transactions[transaction_id].status = "ROLLED_BACK";
                    for (long long id : transactions[transaction_id].service_ids) {
                        services[id].in_transaction = false;
                    }
                }
            }
        } else if (command == "GET_TRANSACTION_STATUS") {
            long long transaction_id;
            ss >> transaction_id;

            if (transactions.find(transaction_id) == transactions.end()) {
                cout << "NOT_FOUND" << endl;
            } else {
                cout << transactions[transaction_id].status << endl;
            }
        }
    }

    return 0;
}
```
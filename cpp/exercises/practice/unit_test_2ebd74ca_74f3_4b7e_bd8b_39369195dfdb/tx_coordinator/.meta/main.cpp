#include "tx_coordinator.h"
#include <iostream>
#include <string>

int main() {
    TransactionCoordinator coordinator;
    std::string line;
    
    std::cout << "Transaction Coordinator started. Enter commands or 'exit' to quit.\n";
    
    while (true) {
        std::cout << "> ";
        std::getline(std::cin, line);
        
        if (line == "exit") {
            break;
        }
        
        std::string result = coordinator.executeCommand(line);
        std::cout << result << std::endl;
    }
    
    return 0;
}
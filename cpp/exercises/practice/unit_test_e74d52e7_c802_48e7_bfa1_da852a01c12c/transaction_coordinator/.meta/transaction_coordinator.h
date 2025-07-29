#ifndef TRANSACTION_COORDINATOR_H
#define TRANSACTION_COORDINATOR_H

#include <istream>
#include <ostream>

namespace transaction_coordinator {

void process_transactions(std::istream& in, std::ostream& out);

}

#endif
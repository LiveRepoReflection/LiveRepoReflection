#include "distributed_tx.h"
#include <chrono>
#include <thread>

namespace distributed_tx {

Coordinator::Coordinator(int timeout_ms)
    : timeout_ms_(timeout_ms), globalDecision_("") {}

void Coordinator::addParticipant(Participant* participant) {
    participants_.push_back(participant);
    ackMap_[participant] = false;
    participant->setCoordinator(this);
}

void Coordinator::acknowledge(Participant* participant) {
    ackMap_[participant] = true;
}

bool Coordinator::allAcksReceived() const {
    for (const auto& entry : ackMap_) {
        if (!entry.second) {
            return false;
        }
    }
    return true;
}

std::string Coordinator::getGlobalDecision() const {
    return globalDecision_;
}

void Coordinator::initiateTransaction() {
    bool allCommit = true;
    // Collect votes from all participants.
    for (Participant* p : participants_) {
        std::string vote = p->prepareTransaction();
        if (vote != "COMMIT") {
            allCommit = false;
        }
    }
    // Determine global decision.
    globalDecision_ = allCommit ? "GLOBAL_COMMIT" : "GLOBAL_ABORT";
    // Send the global decision to all participants.
    for (Participant* p : participants_) {
        p->finalizeTransaction(globalDecision_);
    }
}

Participant::Participant(const std::string& id, bool voteCommit, bool simulateTimeout)
    : id_(id),
      voteCommit_(voteCommit),
      simulateTimeout_(simulateTimeout),
      crashed_(false),
      log_(""),
      pendingGlobalDecision_(""),
      coordinator_(nullptr) {}

void Participant::setCoordinator(Coordinator* coordinator) {
    coordinator_ = coordinator;
}

std::string Participant::prepareTransaction() {
    if (crashed_) {
        return "NO_RESPONSE";
    }
    log_ = "prepared";
    if (simulateTimeout_) {
        return "TIMEOUT";
    }
    return voteCommit_ ? "COMMIT" : "ABORT";
}

void Participant::finalizeTransaction(const std::string& decision) {
    if (crashed_) {
        pendingGlobalDecision_ = decision;
        return;
    }
    if (decision == "GLOBAL_COMMIT") {
        log_ = "committed";
    } else {
        log_ = "aborted";
    }
    if (coordinator_) {
        coordinator_->acknowledge(this);
    }
}

void Participant::simulateCrash() {
    crashed_ = true;
    // When crashed, participant does not process finalize messages.
}

void Participant::recover() {
    crashed_ = false;
    if (!pendingGlobalDecision_.empty()) {
        finalizeTransaction(pendingGlobalDecision_);
        pendingGlobalDecision_.clear();
    }
}

std::string Participant::getLog() const {
    return log_;
}

}  // namespace distributed_tx
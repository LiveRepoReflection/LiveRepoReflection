#ifndef DISTRIBUTED_TX_H
#define DISTRIBUTED_TX_H

#include <string>
#include <vector>
#include <map>

namespace distributed_tx {

class Participant;
class Coordinator;

class Coordinator {
public:
    Coordinator(int timeout_ms);
    void addParticipant(Participant* participant);
    void initiateTransaction();
    void acknowledge(Participant* participant);
    bool allAcksReceived() const;
    std::string getGlobalDecision() const;

private:
    int timeout_ms_;
    std::vector<Participant*> participants_;
    std::map<Participant*, bool> ackMap_;
    std::string globalDecision_;
};

class Participant {
public:
    Participant(const std::string& id, bool voteCommit, bool simulateTimeout);
    void setCoordinator(Coordinator* coordinator);
    std::string prepareTransaction();
    void finalizeTransaction(const std::string& decision);
    void simulateCrash();
    void recover();
    std::string getLog() const;

private:
    std::string id_;
    bool voteCommit_;
    bool simulateTimeout_;
    bool crashed_;
    std::string log_;
    std::string pendingGlobalDecision_;
    Coordinator* coordinator_;
};

}  // namespace distributed_tx

#endif
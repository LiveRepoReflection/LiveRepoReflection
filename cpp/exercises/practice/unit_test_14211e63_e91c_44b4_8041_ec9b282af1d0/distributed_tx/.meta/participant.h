#ifndef PARTICIPANT_H
#define PARTICIPANT_H

#include "distributed_tx.h"
#include <string>

class Participant : public IParticipant {
public:
    explicit Participant(std::string id);
    
    PrepareResult prepare() override;
    bool commit() override;
    bool rollback() override;
    
    const std::string& getId() const;

private:
    std::string id_;
    bool prepared_;
    bool committed_;
    std::mutex mutex_;
};

#endif
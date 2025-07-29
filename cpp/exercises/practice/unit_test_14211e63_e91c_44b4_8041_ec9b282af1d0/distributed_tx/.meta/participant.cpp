#include "participant.h"

Participant::Participant(std::string id)
    : id_(std::move(id)), prepared_(false), committed_(false) {}

PrepareResult Participant::prepare() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    try {
        // Simulate some work
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        prepared_ = true;
        return PrepareResult::READY;
    } catch (...) {
        prepared_ = false;
        return PrepareResult::ABORT;
    }
}

bool Participant::commit() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    if (!prepared_) {
        return false;
    }
    
    try {
        // Simulate some work
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        committed_ = true;
        return true;
    } catch (...) {
        return false;
    }
}

bool Participant::rollback() {
    std::lock_guard<std::mutex> lock(mutex_);
    
    try {
        // Simulate some work
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        prepared_ = false;
        committed_ = false;
        return true;
    } catch (...) {
        return false;
    }
}

const std::string& Participant::getId() const {
    return id_;
}
#ifndef SERVICE_H
#define SERVICE_H

class Service {
public:
    virtual bool Prepare() = 0;
    virtual bool Commit() = 0;
    virtual bool Rollback() = 0;
    virtual int GetId() = 0;
    virtual ~Service() = default;
};

#endif
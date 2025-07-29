# Transaction Validation

This module validates distributed transaction logs according to the two-phase commit (2PC) protocol.

## Overview

The validation ensures transaction logs adhere to these rules:

1. Services must receive a PREPARE message before voting
2. Services can vote only once per transaction
3. Commit/abort decisions must follow all votes
4. Commit requires all services to vote commit; abort requires at least one abort vote
5. Services can only complete a transaction after a commit/abort decision
6. Services can only complete a transaction once

## Usage

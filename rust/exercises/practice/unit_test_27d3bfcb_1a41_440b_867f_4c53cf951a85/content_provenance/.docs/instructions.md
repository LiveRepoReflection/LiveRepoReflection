## Project Name

`Decentralized Social Network: Content Provenance and Tamper Detection`

## Question Description

You are tasked with building a core component for a decentralized social network. This network aims to provide users with verifiable content provenance and tamper detection, addressing concerns about misinformation and content manipulation. The network leverages a distributed ledger to store content hashes and authorship information, ensuring transparency and immutability.

Each user in the network can post content. Each content is uniquely identified by a content ID (`u64`). When a user posts content, the following information is recorded on the distributed ledger:

1.  **Content ID (`u64`):** A unique identifier for the content.
2.  **Author ID (`u64`):** The ID of the user who posted the content.
3.  **Content Hash (`String`):** A cryptographic hash (SHA-256) of the content itself.
4.  **Timestamp (`u64`):** A Unix timestamp representing when the content was posted.
5. **Signatures (`Vec<(u64, String)>`):** A list of endorsements (signatures) from other users in the network, with each tuple representing the user id (`u64`) of the endorser and the signature (`String`).

Your task is to implement the core functionality to verify the integrity and provenance of content within this decentralized social network. Specifically, you need to implement the following functions:

1.  **`store_content(content_id: u64, author_id: u64, content: String, timestamp: u64) -> bool`:** This function simulates storing new content on the distributed ledger. It calculates the SHA-256 hash of the provided `content` string and stores the `content_id`, `author_id`, calculated `content_hash`, and `timestamp`. This function should return `true` if storing is successful. You should also handle the case when a content id already exists.

2.  **`verify_content(content_id: u64, content: String) -> bool`:** Given a `content_id` and the actual `content` string, this function verifies if the content matches the hash stored on the distributed ledger. It calculates the SHA-256 hash of the provided `content` and compares it with the stored hash for the given `content_id`. Return `true` if the content is verified (hashes match), and `false` otherwise.

3.  **`get_author(content_id: u64) -> Option<u64>`:** Given a `content_id`, return the `author_id` of the content. If the `content_id` does not exist, return `None`.

4.  **`endorse_content(content_id: u64, endorser_id: u64, signature: String) -> bool`:** Allows a user (`endorser_id`) to endorse a piece of content (`content_id`) by providing a digital signature. The signature is simply a string. The function should store the endorser's ID and signature alongside the content's metadata. Multiple endorsements for the same content should be allowed. Return true if endorsement is successful.

5.  **`get_endorsements(content_id: u64) -> Option<Vec<(u64, String)>>`:** Given a `content_id`, return a vector of tuples, where each tuple contains the `endorser_id` and the corresponding `signature` for that endorsement. Return `None` if the `content_id` does not exist or has no endorsements.

**Constraints:**

*   The content must be considered immutable once stored.
*   Implement efficient lookups and storage for a large number of content entries (think millions).
*   The solution should be thread-safe. Multiple users can simultaneously post and verify content.
*   Calculating SHA-256 hashes should be performant.
*   Assume that the content string can be arbitrarily large (up to several MB).
*   The timestamp represents the number of seconds since the Unix epoch. It is only for data storage and will not affect the program logic.

**Optimization Requirements:**

*   Minimize memory usage.
*   Optimize for read operations (verifying content, getting author, getting endorsements). Read operations are expected to be more frequent than write operations (storing and endorsing).
*   Consider using appropriate data structures for efficient storage and retrieval of content and related metadata.

**Real-World Practical Scenarios:**

*   Detecting deepfakes and manipulated media by verifying content hashes against a trusted ledger.
*   Tracking the origin and modifications of documents in a collaborative environment.
*   Ensuring the integrity of software updates and preventing malware distribution.

**System Design Aspects:**

*   Consider how your implementation can scale to handle a large volume of content and users.
*   Think about potential bottlenecks and how to mitigate them.
*   How would you handle content deletion requests (if any)? (This is out of scope for this question, but consider the implications).

**Algorithmic Efficiency Requirements:**

*   `store_content`: Should have an average time complexity close to O(1).
*   `verify_content`: Should have an average time complexity close to O(1).
*   `get_author`: Should have an average time complexity close to O(1).
*   `endorse_content`: Should have an average time complexity close to O(1).
*   `get_endorsements`: Should have an average time complexity close to O(1).

This problem challenges you to design and implement a core component of a decentralized social network that prioritizes content integrity and provenance using Rust's powerful features and memory safety guarantees. Good luck!

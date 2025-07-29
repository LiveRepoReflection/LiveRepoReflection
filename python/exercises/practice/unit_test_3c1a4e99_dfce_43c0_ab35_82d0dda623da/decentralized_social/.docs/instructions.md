## Project Name

```
Decentralized-Social-Network
```

## Question Description

You are tasked with designing and implementing core functionalities for a decentralized social network (DSN). Unlike centralized platforms, this DSN operates on a peer-to-peer network, and data is distributed across multiple nodes. This problem focuses on implementing the user profile management and post distribution aspects of the DSN.

**Core Requirements:**

1.  **User Profile Management:**

    *   Each user has a unique ID (a string).
    *   Each user has a profile containing:
        *   A username (string).
        *   A display name (string).
        *   A bio (string).
        *   A list of follower user IDs.
        *   A list of following user IDs.
    *   Implement functions to:
        *   Create a new user profile.
        *   Update an existing user profile.
        *   Retrieve a user profile given their ID.
        *   Follow another user (add to both follower and following lists).
        *   Unfollow another user (remove from both follower and following lists).

2.  **Post Distribution:**

    *   Each post has a unique ID (string).
    *   Each post contains:
        *   The author's user ID (string).
        *   The post content (string).
        *   A timestamp (integer representing seconds since epoch).
    *   Implement functions to:
        *   Create a new post.
        *   Retrieve a post given its ID.
        *   Distribute a post to followers:
            *   Given a user ID, retrieve a list of their follower user IDs.
            *   Simulate pushing the new post ID to each follower's "inbox" (a list of post IDs). The inbox size is limited. If the inbox is full, the oldest post ID should be removed.

**Constraints and Considerations:**

*   **Data Storage:** Assume that the data (user profiles, posts, and inboxes) is stored in a distributed hash table (DHT). However, for this problem, you can simulate the DHT using a dictionary in Python. You don't need to implement a full DHT.
*   **Scalability:** While you don't need to implement true distributed functionality, design your data structures and algorithms with scalability in mind. Consider how your design would perform with millions of users and posts.
*   **Concurrency:** Assume that multiple users can interact with the DSN simultaneously. While you don't need to implement actual threading or locking, consider potential race conditions and how you would address them in a real-world implementation.
*   **Inbox Size:** Each user's inbox can hold a maximum of `N` post IDs. Older post IDs are evicted when the inbox is full. `N` should be definable when initializing your DSN system.
*   **Time Complexity:**  Optimize for retrieving user profiles and distributing posts to followers.  Assume read operations happen much more frequently than write operations (creating/updating profiles, creating posts).
*   **Error Handling:** Implement appropriate error handling, such as raising exceptions when a user ID or post ID does not exist.

**Specific Requirements:**

*   Implement the following classes and functions:
    *   `DSN(inbox_size)`:  The main class representing the decentralized social network. The `inbox_size` parameter defines the maximum size of user inboxes.

        *   `create_user(user_id, username, display_name, bio)`: Creates a new user profile. Raises an exception if the user ID already exists.
        *   `update_user(user_id, username=None, display_name=None, bio=None)`: Updates an existing user profile. Raises an exception if the user ID does not exist.
        *   `get_user(user_id)`: Retrieves a user profile. Raises an exception if the user ID does not exist.
        *   `follow_user(follower_id, followee_id)`:  Makes the `follower_id` follow the `followee_id`. Raises exceptions if either user ID does not exist.
        *   `unfollow_user(follower_id, followee_id)`:  Makes the `follower_id` unfollow the `followee_id`. Raises exceptions if either user ID does not exist.
        *   `create_post(post_id, author_id, content, timestamp)`: Creates a new post. Raises an exception if the post ID already exists or the author user ID does not exist.
        *   `get_post(post_id)`: Retrieves a post. Raises an exception if the post ID does not exist.
        *   `distribute_post(post_id)`: Distributes a post to all followers of the author.  The post ID is added to each follower's inbox.
        *   `get_inbox(user_id)`: Retrieves the user's inbox (list of post IDs). Raises an exception if the user ID does not exist.
*   Your implementation must use dictionaries to simulate the DHT for storing user profiles, posts, and inboxes.
*   Ensure that the `follow_user` and `unfollow_user` functions update both the follower's `following` list and the followee's `followers` list.
*   Implement inbox eviction using a suitable data structure (e.g., a deque) to maintain the correct order and ensure efficient removal of the oldest post.

This problem requires a good understanding of data structures, algorithm design, and system design considerations. The challenge lies in creating a scalable and efficient implementation within the given constraints.

from collections import deque

class DSN:
    def __init__(self, inbox_size):
        self.inbox_size = inbox_size
        self.users = {}  # key: user_id, value: user profile dict
        self.posts = {}  # key: post_id, value: post dict
        self.inboxes = {}  # key: user_id, value: deque of post_ids

    def create_user(self, user_id, username, display_name, bio):
        if user_id in self.users:
            raise Exception("User already exists")
        self.users[user_id] = {
            "username": username,
            "display_name": display_name,
            "bio": bio,
            "followers": [],
            "following": []
        }
        self.inboxes[user_id] = deque(maxlen=self.inbox_size)

    def update_user(self, user_id, username=None, display_name=None, bio=None):
        if user_id not in self.users:
            raise Exception("User does not exist")
        if username is not None:
            self.users[user_id]["username"] = username
        if display_name is not None:
            self.users[user_id]["display_name"] = display_name
        if bio is not None:
            self.users[user_id]["bio"] = bio

    def get_user(self, user_id):
        if user_id not in self.users:
            raise Exception("User does not exist")
        return self.users[user_id]

    def follow_user(self, follower_id, followee_id):
        if follower_id not in self.users:
            raise Exception("Follower user does not exist")
        if followee_id not in self.users:
            raise Exception("Followee user does not exist")
        # Update follower's following list if not already following
        if followee_id not in self.users[follower_id]["following"]:
            self.users[follower_id]["following"].append(followee_id)
        # Update followee's followers list if not already a follower
        if follower_id not in self.users[followee_id]["followers"]:
            self.users[followee_id]["followers"].append(follower_id)

    def unfollow_user(self, follower_id, followee_id):
        if follower_id not in self.users:
            raise Exception("Follower user does not exist")
        if followee_id not in self.users:
            raise Exception("Followee user does not exist")
        if followee_id in self.users[follower_id]["following"]:
            self.users[follower_id]["following"].remove(followee_id)
        if follower_id in self.users[followee_id]["followers"]:
            self.users[followee_id]["followers"].remove(follower_id)

    def create_post(self, post_id, author_id, content, timestamp):
        if post_id in self.posts:
            raise Exception("Post already exists")
        if author_id not in self.users:
            raise Exception("Author does not exist")
        self.posts[post_id] = {
            "author_id": author_id,
            "content": content,
            "timestamp": timestamp
        }

    def get_post(self, post_id):
        if post_id not in self.posts:
            raise Exception("Post does not exist")
        return self.posts[post_id]

    def distribute_post(self, post_id):
        if post_id not in self.posts:
            raise Exception("Post does not exist")
        author_id = self.posts[post_id]["author_id"]
        if author_id not in self.users:
            raise Exception("Author does not exist")
        followers = self.users[author_id]["followers"]
        for follower_id in followers:
            if follower_id in self.inboxes:
                self.inboxes[follower_id].append(post_id)
            else:
                # In a real-world scenario, all users should have an inbox
                self.inboxes[follower_id] = deque([post_id], maxlen=self.inbox_size)

    def get_inbox(self, user_id):
        if user_id not in self.users:
            raise Exception("User does not exist")
        return list(self.inboxes[user_id])
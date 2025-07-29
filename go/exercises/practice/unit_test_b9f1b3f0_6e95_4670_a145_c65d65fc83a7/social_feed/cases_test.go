package socialfeed

// TestCase represents a test case for the social feed system
type TestCase struct {
	description string
	operations  []Operation
	expected    []Post
}

// Operation represents different operations that can be performed on the social feed
type Operation struct {
	opType    string      // "addUser", "addFollower", "createPost", "getFeed"
	userID    int64       
	targetID  int64       // for follow operations
	content   string      // for post operations
	timestamp int64       // for post operations
	likes     int64       // for post operations
}

// Post represents a post in the social feed
type Post struct {
	UserID    int64
	Content   string
	Timestamp int64
	Likes     int64
}

var testCases = []TestCase{
	{
		description: "Basic feed generation test",
		operations: []Operation{
			{opType: "addUser", userID: 1},
			{opType: "addUser", userID: 2},
			{opType: "addUser", userID: 3},
			{opType: "addFollower", userID: 1, targetID: 2},
			{opType: "addFollower", userID: 1, targetID: 3},
			{opType: "createPost", userID: 2, content: "Hello from user 2", timestamp: 1000, likes: 5},
			{opType: "createPost", userID: 3, content: "Hello from user 3", timestamp: 2000, likes: 3},
		},
		expected: []Post{
			{UserID: 3, Content: "Hello from user 3", Timestamp: 2000, Likes: 3},
			{UserID: 2, Content: "Hello from user 2", Timestamp: 1000, Likes: 5},
		},
	},
	{
		description: "Empty feed test",
		operations: []Operation{
			{opType: "addUser", userID: 1},
			{opType: "addUser", userID: 2},
		},
		expected: []Post{},
	},
	{
		description: "Complex feed with multiple posts and followers",
		operations: []Operation{
			{opType: "addUser", userID: 1},
			{opType: "addUser", userID: 2},
			{opType: "addUser", userID: 3},
			{opType: "addUser", userID: 4},
			{opType: "addFollower", userID: 1, targetID: 2},
			{opType: "addFollower", userID: 1, targetID: 3},
			{opType: "addFollower", userID: 1, targetID: 4},
			{opType: "createPost", userID: 2, content: "First post", timestamp: 1000, likes: 10},
			{opType: "createPost", userID: 3, content: "Second post", timestamp: 2000, likes: 5},
			{opType: "createPost", userID: 4, content: "Third post", timestamp: 3000, likes: 15},
			{opType: "createPost", userID: 2, content: "Fourth post", timestamp: 4000, likes: 7},
		},
		expected: []Post{
			{UserID: 2, Content: "Fourth post", Timestamp: 4000, Likes: 7},
			{UserID: 4, Content: "Third post", Timestamp: 3000, Likes: 15},
			{UserID: 3, Content: "Second post", Timestamp: 2000, Likes: 5},
			{UserID: 2, Content: "First post", Timestamp: 1000, Likes: 10},
		},
	},
}
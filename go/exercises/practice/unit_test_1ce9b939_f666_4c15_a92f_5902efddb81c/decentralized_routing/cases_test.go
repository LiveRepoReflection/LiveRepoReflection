package decentralized_routing

type routeTest struct {
	description    string
	originServer  string
	userID        string
	message       string
	networkState  NetworkState
	expectedPaths map[string][]string // serverID -> expected path
}

var routeTests = []routeTest{
	{
		description: "single follower on same server",
		originServer: "s1",
		userID: "u1",
		message: "hello",
		networkState: NetworkState{
			Servers: map[string]Server{
				"s1": {
					Connections: []string{},
					Users: map[string]User{
						"u1": {Followers: []Follower{{ID: "u2", Server: "s1"}}},
						"u2": {},
					},
				},
			},
		},
		expectedPaths: map[string][]string{
			"s1": {"s1"},
		},
	},
	{
		description: "multiple followers across servers",
		originServer: "s1",
		userID: "u1",
		message: "test",
		networkState: NetworkState{
			Servers: map[string]Server{
				"s1": {
					Connections: []string{"s2"},
					Users: map[string]User{
						"u1": {Followers: []Follower{
							{ID: "u2", Server: "s2"},
							{ID: "u3", Server: "s1"},
						}},
					},
				},
				"s2": {
					Connections: []string{"s1", "s3"},
					Users: map[string]User{
						"u2": {},
					},
				},
				"s3": {
					Connections: []string{"s2"},
					Users: map[string]User{
						"u4": {},
					},
				},
			},
		},
		expectedPaths: map[string][]string{
			"s1": {"s1"},
			"s2": {"s1", "s2"},
		},
	},
	{
		description: "network partition",
		originServer: "s1",
		userID: "u1",
		message: "partition",
		networkState: NetworkState{
			Servers: map[string]Server{
				"s1": {
					Connections: []string{"s2"},
					Users: map[string]User{
						"u1": {Followers: []Follower{
							{ID: "u2", Server: "s2"},
							{ID: "u3", Server: "s3"},
						}},
					},
				},
				"s2": {
					Connections: []string{"s1"},
					Users: map[string]User{
						"u2": {},
					},
				},
				"s3": {
					Connections: []string{"s4"},
					Users: map[string]User{
						"u3": {},
					},
				},
				"s4": {
					Connections: []string{"s3"},
					Users: map[string]User{
						"u4": {},
					},
				},
			},
		},
		expectedPaths: map[string][]string{
			"s2": {"s1", "s2"},
		},
	},
	{
		description: "circular connections",
		originServer: "s1",
		userID: "u1",
		message: "circle",
		networkState: NetworkState{
			Servers: map[string]Server{
				"s1": {
					Connections: []string{"s2"},
					Users: map[string]User{
						"u1": {Followers: []Follower{
							{ID: "u2", Server: "s3"},
						}},
					},
				},
				"s2": {
					Connections: []string{"s3", "s1"},
					Users: map[string]User{
						"u3": {},
					},
				},
				"s3": {
					Connections: []string{"s1", "s2"},
					Users: map[string]User{
						"u2": {},
					},
				},
			},
		},
		expectedPaths: map[string][]string{
			"s3": {"s1", "s2", "s3"},
		},
	},
}
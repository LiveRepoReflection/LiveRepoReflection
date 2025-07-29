package geo_kv

type Config struct {
	DataCenters       []DataCenterConfig
	ReplicationFactor int
	ConsistencyLevel  ConsistencyLevel
}

type DataCenterConfig struct {
	ID    string
	Nodes []string
}

type ConsistencyLevel string

const (
	ConsistencyLevelQuorum   ConsistencyLevel = "quorum"
	ConsistencyLevelStrong  ConsistencyLevel = "strong"
	ConsistencyLevelEventual ConsistencyLevel = "eventual"
)
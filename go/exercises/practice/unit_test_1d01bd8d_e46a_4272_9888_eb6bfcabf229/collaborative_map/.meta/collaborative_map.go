package collaborative_map

import (
	"sync"
)

type Claim struct {
	Row       int
	Col       int
	Value     string
	Timestamp int64
	UserID    string
}

type cellState struct {
	value     string
	timestamp int64
	userID    string
}

type MapService struct {
	size  int
	grid  [][]*cellState
	mutex sync.RWMutex
}

func NewMapService(size int) *MapService {
	grid := make([][]*cellState, size)
	for i := range grid {
		grid[i] = make([]*cellState, size)
	}
	return &MapService{
		size: size,
		grid: grid,
	}
}

func (m *MapService) SubmitClaim(claim Claim) {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	if claim.Row < 0 || claim.Row >= m.size || claim.Col < 0 || claim.Col >= m.size {
		return
	}

	current := m.grid[claim.Row][claim.Col]
	if current == nil ||
		claim.Timestamp > current.timestamp ||
		(claim.Timestamp == current.timestamp && claim.UserID < current.userID) {
		m.grid[claim.Row][claim.Col] = &cellState{
			value:     claim.Value,
			timestamp: claim.Timestamp,
			userID:    claim.UserID,
		}
	}
}

func (m *MapService) GetValue(row, col int) string {
	m.mutex.RLock()
	defer m.mutex.RUnlock()

	if row < 0 || row >= m.size || col < 0 || col >= m.size {
		return ""
	}

	if m.grid[row][col] == nil {
		return ""
	}
	return m.grid[row][col].value
}

func (m *MapService) Size() int {
	return m.size
}
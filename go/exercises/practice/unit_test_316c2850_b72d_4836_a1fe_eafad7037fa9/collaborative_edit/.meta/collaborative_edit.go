package collaborative_edit

type Operation struct {
	AuthorID      string
	Timestamp     int64
	SectionID     string
	OperationType string
	Content       string
	Version       int64
}

type sectionState struct {
	content string
	version int64
}

func ApplyOperations(documentState map[string]string, operations []Operation) map[string]string {
	// Create a version tracking map
	sectionVersions := make(map[string]*sectionState)

	// Initialize version tracking for existing sections
	for sectionID, content := range documentState {
		sectionVersions[sectionID] = &sectionState{
			content: content,
			version: 0,
		}
	}

	// Process each operation in order
	for _, op := range operations {
		// Get or create section state
		section, exists := sectionVersions[op.SectionID]
		if !exists {
			section = &sectionState{
				content: "",
				version: 0,
			}
			sectionVersions[op.SectionID] = section
		}

		// Version check
		if op.Version != section.version {
			continue // Skip operation if version doesn't match
		}

		// Apply the operation based on type
		switch op.OperationType {
		case "insert":
			section.content += op.Content

		case "delete":
			if op.Content == "" {
				section.content = ""
			} else {
				section.content = op.Content
			}

		case "replace":
			section.content = op.Content
		}

		// Increment version after successful operation
		section.version++
	}

	// Update document state with final contents
	result := make(map[string]string)
	for sectionID, state := range sectionVersions {
		result[sectionID] = state.content
	}

	return result
}
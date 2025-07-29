package network

// getInputSwitchForServer returns the input switch ID for a given server
func getInputSwitchForServer(n, r, serverID int) int {
	serversPerInputSwitch := n / r
	return serverID / serversPerInputSwitch
}

// getOutputSwitchForServer returns the output switch ID for a given server
func getOutputSwitchForServer(n, k, serverID int) int {
	serversPerOutputSwitch := n / k
	return serverID / serversPerOutputSwitch
}

// isValidPath checks if a path exists from src to dest considering faulty links
func isValidPath(n, r, m, k, src, dest int, faults []FaultyLink) bool {
	if src == dest {
		return true
	}

	// Determine input and output switches for src and dest
	inputSwitch := getInputSwitchForServer(n, r, src)
	outputSwitch := getOutputSwitchForServer(n, k, dest)

	// Check if src is connected to its input switch
	srcToInputFaulty := false
	for _, fault := range faults {
		if fault.Type == "output" && fault.ID1 == inputSwitch && fault.ID2 == src {
			srcToInputFaulty = true
			break
		}
	}
	if srcToInputFaulty {
		return false
	}

	// Check if dest is connected to its output switch
	destToOutputFaulty := false
	for _, fault := range faults {
		if fault.Type == "output" && fault.ID1 == outputSwitch && fault.ID2 == dest {
			destToOutputFaulty = true
			break
		}
	}
	if destToOutputFaulty {
		return false
	}

	// Check if at least one path exists from input switch to output switch via middle switches
	for middleSwitchID := 0; middleSwitchID < m; middleSwitchID++ {
		// Check if input switch is connected to this middle switch
		inputToMiddleFaulty := false
		for _, fault := range faults {
			if fault.Type == "input" && fault.ID1 == inputSwitch && fault.ID2 == middleSwitchID {
				inputToMiddleFaulty = true
				break
			}
		}
		if inputToMiddleFaulty {
			continue
		}

		// Check if middle switch is connected to output switch
		middleToOutputFaulty := false
		for _, fault := range faults {
			if fault.Type == "middle" && fault.ID1 == middleSwitchID && fault.ID2 == outputSwitch {
				middleToOutputFaulty = true
				break
			}
		}
		if middleToOutputFaulty {
			continue
		}

		// We found a valid path through this middle switch
		return true
	}

	// No valid path found
	return false
}

// MinimumHops finds the minimum number of hops required to transmit data
// from src to dest through the Clos network.
// Returns -1 if no path is available.
func MinimumHops(n, r, m, k, src, dest int, faults []FaultyLink) int {
	// Validate input parameters
	if n <= 0 || r <= 0 || m <= 0 || k <= 0 || n%r != 0 || n%k != 0 {
		return -1
	}

	// Validate server IDs
	if src < 0 || src >= n || dest < 0 || dest >= n {
		return -1
	}

	// If source and destination are the same, no hops needed
	if src == dest {
		return 0
	}

	// Initialize faults slice if nil
	if faults == nil {
		faults = []FaultyLink{}
	}

	// Check if a valid path exists
	if !isValidPath(n, r, m, k, src, dest, faults) {
		return -1
	}

	// Calculate minimum hops
	// 1. Server src -> Input Switch: 1 hop
	// 2. Input Switch -> Middle Switch: 1 hop
	// 3. Middle Switch -> Output Switch: 1 hop
	// 4. Output Switch -> Server dest: 1 hop
	// Total: 4 hops, which is the minimum for any non-identical src and dest
	return 4
}
package task_assign

import "math"

func MinCostAssignment(N int, M int, engineerSkills []int, taskSkills []int, cost [][]int) int {
    if N < M {
        return -1
    }

    // Precompute valid assignments
    valid := make([][]bool, N)
    for i := range valid {
        valid[i] = make([]bool, M)
        for j := range valid[i] {
            valid[i][j] = (engineerSkills[i] & taskSkills[j]) == taskSkills[j]
        }
    }

    minCost := math.MaxInt32
    assigned := make([]int, M)
    for i := range assigned {
        assigned[i] = -1
    }

    var backtrack func(int, int)
    backtrack = func(engineerIdx int, currentCost int) {
        if currentCost >= minCost {
            return
        }

        if engineerIdx == N {
            complete := true
            for _, t := range assigned {
                if t == -1 {
                    complete = false
                    break
                }
            }
            if complete && currentCost < minCost {
                minCost = currentCost
            }
            return
        }

        // Option 1: Don't assign this engineer to any task
        backtrack(engineerIdx+1, currentCost)

        // Option 2: Assign to each valid task that's not already assigned
        for taskIdx := 0; taskIdx < M; taskIdx++ {
            if assigned[taskIdx] == -1 && valid[engineerIdx][taskIdx] {
                assigned[taskIdx] = engineerIdx
                backtrack(engineerIdx+1, currentCost+cost[engineerIdx][taskIdx])
                assigned[taskIdx] = -1
            }
        }
    }

    backtrack(0, 0)

    if minCost == math.MaxInt32 {
        return -1
    }
    return minCost
}
pub type ProcessId = usize;

pub struct MemoryManager {
    pub capacity: usize,
    pub allocations: Vec<Option<ProcessId>>,
}

impl MemoryManager {
    pub fn defragment(&mut self) {
        // If the allocations vector is empty, there's nothing to defragment
        if self.allocations.is_empty() {
            return;
        }
        
        // Algorithm: partition array in-place (similar to Lomuto's partition scheme)
        // but maintaining stability by using swap_remove rather than swap
        
        // Start with write_index at 0
        let mut write_index = 0;
        
        // First pass: move all Some values to the beginning
        for read_index in 0..self.allocations.len() {
            if self.allocations[read_index].is_some() {
                // If current position has a process, and it's not already
                // at the correct position, move it
                if read_index != write_index {
                    // Use swap to maintain stability of elements
                    self.allocations.swap(read_index, write_index);
                }
                write_index += 1;
            }
        }
        
        // At this point, all Some values are contiguous at the beginning,
        // and all None values are at the end
    }
}
use mem_defrag::{ProcessId, MemoryManager};

#[test]
fn empty_memory() {
    let mut memory_manager = MemoryManager {
        capacity: 10,
        allocations: vec![],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![]);
}

#[test]
fn full_memory() {
    let mut memory_manager = MemoryManager {
        capacity: 5,
        allocations: vec![Some(1), Some(2), Some(3), Some(4), Some(5)],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(2), Some(3), Some(4), Some(5)]);
}

#[test]
fn empty_allocations() {
    let mut memory_manager = MemoryManager {
        capacity: 5,
        allocations: vec![None, None, None, None, None],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![None, None, None, None, None]);
}

#[test]
fn already_defragmented() {
    let mut memory_manager = MemoryManager {
        capacity: 10,
        allocations: vec![Some(1), Some(2), Some(3), None, None, None, None, None],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(2), Some(3), None, None, None, None, None]);
}

#[test]
fn simple_defragmentation() {
    let mut memory_manager = MemoryManager {
        capacity: 10,
        allocations: vec![Some(1), None, Some(2), None, Some(3), None, Some(4), None, Some(5), None],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(2), Some(3), Some(4), Some(5), None, None, None, None, None]);
}

#[test]
fn defragmentation_with_same_process_ids() {
    let mut memory_manager = MemoryManager {
        capacity: 10,
        allocations: vec![Some(1), None, Some(1), None, Some(2), None, Some(2), None, Some(1), None],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(1), Some(2), Some(2), Some(1), None, None, None, None, None]);
}

#[test]
fn defragmentation_with_leading_none() {
    let mut memory_manager = MemoryManager {
        capacity: 10,
        allocations: vec![None, None, Some(1), None, Some(2), None, Some(3), None],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(2), Some(3), None, None, None, None, None]);
}

#[test]
fn defragmentation_with_trailing_some() {
    let mut memory_manager = MemoryManager {
        capacity: 10,
        allocations: vec![None, Some(1), None, Some(2), None, Some(3)],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(2), Some(3), None, None, None]);
}

#[test]
fn alternating_pattern() {
    let mut memory_manager = MemoryManager {
        capacity: 10,
        allocations: vec![Some(1), None, Some(2), None, Some(3), None, Some(4), None],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(2), Some(3), Some(4), None, None, None, None]);
}

#[test]
fn large_sequential_blocks() {
    let mut memory_manager = MemoryManager {
        capacity: 20,
        allocations: vec![Some(1), Some(2), Some(3), None, None, None, Some(4), Some(5), Some(6), None, None, None],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(2), Some(3), Some(4), Some(5), Some(6), None, None, None, None, None, None]);
}

#[test]
fn single_allocated_block() {
    let mut memory_manager = MemoryManager {
        capacity: 10,
        allocations: vec![None, None, None, Some(42), None, None],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(42), None, None, None, None, None]);
}

#[test]
fn single_free_block() {
    let mut memory_manager = MemoryManager {
        capacity: 10,
        allocations: vec![Some(1), Some(2), None, Some(3), Some(4)],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(2), Some(3), Some(4), None]);
}

#[test]
fn large_test_case() {
    let mut allocations = Vec::with_capacity(1000);
    for i in 0..1000 {
        if i % 2 == 0 {
            allocations.push(Some(i / 2));
        } else {
            allocations.push(None);
        }
    }

    let mut memory_manager = MemoryManager {
        capacity: 2000,
        allocations: allocations,
    };

    let expected: Vec<Option<ProcessId>> = (0..500).map(Some)
                                                 .chain((0..500).map(|_| None))
                                                 .collect();

    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, expected);
}

#[test]
fn test_stability() {
    // This test ensures that the relative order of allocated blocks is preserved
    let mut memory_manager = MemoryManager {
        capacity: 15,
        allocations: vec![
            Some(3), None, Some(1), None, Some(4), None, 
            Some(1), None, Some(5), None, Some(9), None,
        ],
    };
    memory_manager.defragment();
    assert_eq!(
        memory_manager.allocations, 
        vec![
            Some(3), Some(1), Some(4), Some(1), Some(5), Some(9),
            None, None, None, None, None, None,
        ]
    );
}

#[test]
fn test_edge_cases() {
    // Capacity greater than allocations length
    let mut memory_manager = MemoryManager {
        capacity: 100,
        allocations: vec![Some(1), None, Some(2)],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(2), None]);

    // Allocations at the ends
    let mut memory_manager = MemoryManager {
        capacity: 10,
        allocations: vec![Some(1), None, None, None, None, None, None, None, None, Some(2)],
    };
    memory_manager.defragment();
    assert_eq!(memory_manager.allocations, vec![Some(1), Some(2), None, None, None, None, None, None, None, None]);
}
use crdt_editor::{CrdtEditor, Operation};
use std::sync::Arc;
use std::thread;

#[test]
fn test_single_insert() {
    let mut editor = CrdtEditor::new();
    let op = Operation::Insert {
        after: None,
        guid: "a1".to_string(),
        character: 'H',
    };
    editor.apply(op);
    assert_eq!(editor.to_string(), "H");
}

#[test]
fn test_multiple_sequential_inserts() {
    let mut editor = CrdtEditor::new();
    editor.apply(Operation::Insert {
        after: None,
        guid: "a1".to_string(),
        character: 'H',
    });
    editor.apply(Operation::Insert {
        after: Some("a1".to_string()),
        guid: "a2".to_string(),
        character: 'i',
    });
    assert_eq!(editor.to_string(), "Hi");
}

#[test]
fn test_concurrent_inserts_same_position() {
    let editor = Arc::new(std::sync::Mutex::new(CrdtEditor::new()));
    let editor1 = editor.clone();
    let editor2 = editor.clone();

    let thread1 = thread::spawn(move || {
        let op = Operation::Insert {
            after: None,
            guid: "a1".to_string(),
            character: 'A',
        };
        editor1.lock().unwrap().apply(op);
    });

    let thread2 = thread::spawn(move || {
        let op = Operation::Insert {
            after: None,
            guid: "a2".to_string(),
            character: 'B',
        };
        editor2.lock().unwrap().apply(op);
    });

    thread1.join().unwrap();
    thread2.join().unwrap();

    let result = editor.lock().unwrap().to_string();
    assert!(result == "AB" || result == "BA");
}

#[test]
fn test_insert_and_delete() {
    let mut editor = CrdtEditor::new();
    editor.apply(Operation::Insert {
        after: None,
        guid: "a1".to_string(),
        character: 'H',
    });
    editor.apply(Operation::Insert {
        after: Some("a1".to_string()),
        guid: "a2".to_string(),
        character: 'i',
    });
    editor.apply(Operation::Delete {
        guid: "a1".to_string(),
    });
    assert_eq!(editor.to_string(), "i");
}

#[test]
fn test_concurrent_delete_win() {
    let editor = Arc::new(std::sync::Mutex::new(CrdtEditor::new()));
    let editor1 = editor.clone();
    let editor2 = editor.clone();

    // Initial setup
    editor.lock().unwrap().apply(Operation::Insert {
        after: None,
        guid: "a1".to_string(),
        character: 'X',
    });

    let thread1 = thread::spawn(move || {
        editor1.lock().unwrap().apply(Operation::Delete {
            guid: "a1".to_string(),
        });
    });

    let thread2 = thread::spawn(move || {
        editor2.lock().unwrap().apply(Operation::Insert {
            after: Some("a1".to_string()),
            guid: "a2".to_string(),
            character: 'Y',
        });
    });

    thread1.join().unwrap();
    thread2.join().unwrap();

    let result = editor.lock().unwrap().to_string();
    assert!(result.is_empty() || result == "Y");
}

#[test]
fn test_complex_operations() {
    let mut editor = CrdtEditor::new();
    editor.apply(Operation::Insert {
        after: None,
        guid: "a1".to_string(),
        character: 'R',
    });
    editor.apply(Operation::Insert {
        after: Some("a1".to_string()),
        guid: "a2".to_string(),
        character: 'u',
    });
    editor.apply(Operation::Insert {
        after: Some("a2".to_string()),
        guid: "a3".to_string(),
        character: 's',
    });
    editor.apply(Operation::Insert {
        after: Some("a3".to_string()),
        guid: "a4".to_string(),
        character: 't',
    });
    editor.apply(Operation::Delete {
        guid: "a2".to_string(),
    });
    editor.apply(Operation::Insert {
        after: Some("a1".to_string()),
        guid: "a5".to_string(),
        character: 'a',
    });
    assert_eq!(editor.to_string(), "Rast");
}

#[test]
fn test_empty_document() {
    let editor = CrdtEditor::new();
    assert_eq!(editor.to_string(), "");
}

#[test]
fn test_invalid_operations() {
    let mut editor = CrdtEditor::new();
    editor.apply(Operation::Insert {
        after: None,
        guid: "a1".to_string(),
        character: 'X',
    });

    // Insert after non-existent GUID
    editor.apply(Operation::Insert {
        after: Some("nonexistent".to_string()),
        guid: "a2".to_string(),
        character: 'Y',
    });
    assert_eq!(editor.to_string(), "X");

    // Delete non-existent GUID
    editor.apply(Operation::Delete {
        guid: "nonexistent".to_string(),
    });
    assert_eq!(editor.to_string(), "X");
}

#[test]
fn test_guid_uniqueness() {
    let mut editor = CrdtEditor::new();
    editor.apply(Operation::Insert {
        after: None,
        guid: "a1".to_string(),
        character: 'A',
    });
    
    // Duplicate GUID insert should be ignored
    editor.apply(Operation::Insert {
        after: None,
        guid: "a1".to_string(),
        character: 'B',
    });
    assert_eq!(editor.to_string(), "A");
}
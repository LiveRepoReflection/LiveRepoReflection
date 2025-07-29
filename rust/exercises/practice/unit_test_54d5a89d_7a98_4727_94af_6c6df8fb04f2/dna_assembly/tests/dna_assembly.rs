use dna_assembly::assemble;

fn reverse_complement(seq: &str) -> String {
    seq.chars()
        .rev()
        .map(|c| match c {
            'A' => 'T',
            'T' => 'A',
            'C' => 'G',
            'G' => 'C',
            _ => c,
        })
        .collect()
}

fn fragment_in_assembly(assembly: &str, fragment: &str) -> bool {
    let rc = reverse_complement(fragment);
    assembly.contains(fragment) || assembly.contains(&rc)
}

#[test]
fn test_empty_input() {
    let fragments: Vec<String> = Vec::new();
    let assembled = assemble(&fragments);
    // For an empty input, we expect an empty assembled sequence.
    assert_eq!(assembled, "");
}

#[test]
fn test_single_fragment() {
    let fragments = vec!["ACGT".to_string()];
    let assembled = assemble(&fragments);
    // The result should contain either the fragment itself or its reverse complement.
    assert!(assembled.contains("ACGT") || assembled.contains("TGCA"));
    // As the fragment length is 4, the assembled result should have length at least 4.
    assert!(assembled.len() >= 4);
}

#[test]
fn test_basic_assembly() {
    let fragments = vec![
        "ACG".to_string(),
        "CGA".to_string(),
        "GAC".to_string(),
    ];
    let assembled = assemble(&fragments);
    // Check that every fragment or its reverse complement is a substring of the assembled sequence.
    for frag in &fragments {
        assert!(
            fragment_in_assembly(&assembled, frag),
            "Fragment {} not found in assembly",
            frag
        );
    }
}

#[test]
fn test_overlapping_fragments() {
    let fragments = vec![
        "AGT".to_string(),
        "GTC".to_string(),
        "TCA".to_string(),
        "CAT".to_string(),
    ];
    let assembled = assemble(&fragments);
    for frag in &fragments {
        assert!(
            fragment_in_assembly(&assembled, frag),
            "Fragment {} not found in assembly",
            frag
        );
    }
    // Verify that the assembled sequence is shorter than the simple concatenation of fragments.
    let total_length: usize = fragments.iter().map(|s| s.len()).sum();
    assert!(
        assembled.len() < total_length,
        "Assembled result is not optimized in length"
    );
}

#[test]
fn test_reverse_complement_integration() {
    // Provide fragments where one fragment is the reverse complement of another.
    let fragments = vec![
        "ATCG".to_string(),
        "CGAT".to_string(), // Reverse complement of "ATCG"
        "TCGA".to_string(), // Reverse complement of "AGCT"
    ];
    let assembled = assemble(&fragments);
    for frag in &fragments {
        assert!(
            fragment_in_assembly(&assembled, frag),
            "Fragment {} (or its reverse complement) not found in assembly",
            frag
        );
    }
}

#[test]
fn test_complex_case() {
    // A more complex set of fragments that require careful overlapping.
    let fragments = vec![
        "AGCTAGC".to_string(),
        "TCGATCG".to_string(),
        "CGATCGA".to_string(),
        "GATCGAT".to_string(),
        "ATCGATC".to_string(),
    ];
    let assembled = assemble(&fragments);
    for frag in &fragments {
        assert!(
            fragment_in_assembly(&assembled, frag),
            "Fragment {} (or its reverse complement) not found in assembly",
            frag
        );
    }
    let total_length: usize = fragments.iter().map(|s| s.len()).sum();
    assert!(
        assembled.len() < total_length,
        "Assembled result is not optimized in length"
    );
}
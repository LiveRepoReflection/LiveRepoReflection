pub fn assemble(fragments: &[String]) -> String {
    // Remove fragments that are substrings of others.
    let mut frags = remove_substrings(fragments);
    if frags.is_empty() {
        return "".to_string();
    }
    // Continue merging until only one superstring remains.
    while frags.len() > 1 {
        let (i, j, overlap, merged) = find_best_merge(&frags);
        if overlap == 0 {
            // No overlap found, so simply concatenate the last two fragments.
            let last = frags.pop().unwrap();
            let second_last = frags.pop().unwrap();
            frags.push(second_last + &last);
        } else {
            // Remove the merged fragments. Remove the index with the higher value first.
            if i > j {
                frags.remove(i);
                frags.remove(j);
            } else {
                frags.remove(j);
                frags.remove(i);
            }
            frags.push(merged);
        }
        frags = remove_substrings(&frags);
    }
    frags.pop().unwrap()
}

fn remove_substrings(strings: &[String]) -> Vec<String> {
    let mut result = Vec::new();
    'outer: for s in strings {
        for t in strings {
            if s != t && t.contains(s) {
                continue 'outer;
            }
        }
        result.push(s.clone());
    }
    result
}

fn find_best_merge(strings: &[String]) -> (usize, usize, usize, String) {
    let mut best_overlap = 0;
    let mut best_merged = String::new();
    let mut best_i = 0;
    let mut best_j = 0;
    let n = strings.len();
    for i in 0..n {
        for j in 0..n {
            if i == j {
                continue;
            }
            let s1 = &strings[i];
            let s2 = &strings[j];
            // Try merging with s2 in its original orientation.
            let overlap_orig = calc_overlap(s1, s2);
            if overlap_orig > best_overlap {
                best_overlap = overlap_orig;
                best_merged = s1.clone() + &s2[overlap_orig..];
                best_i = i;
                best_j = j;
            }
            // Try merging with s2 in its reverse complement orientation.
            let s2_rc = reverse_complement(s2);
            let overlap_rc = calc_overlap(s1, &s2_rc);
            if overlap_rc > best_overlap {
                best_overlap = overlap_rc;
                best_merged = s1.clone() + &s2_rc[overlap_rc..];
                best_i = i;
                best_j = j;
            }
        }
    }
    (best_i, best_j, best_overlap, best_merged)
}

fn calc_overlap(a: &str, b: &str) -> usize {
    let max_overlap = std::cmp::min(a.len(), b.len());
    for k in (1..=max_overlap).rev() {
        if a.ends_with(&b[..k]) {
            return k;
        }
    }
    0
}

fn reverse_complement(s: &str) -> String {
    s.chars()
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
import unittest
from dna_align import max_alignment_score

class TestDNAAlignment(unittest.TestCase):
    def test_both_empty(self):
        # Both sequences empty
        sequence1 = ""
        sequence2 = ""
        expected = 0
        self.assertEqual(max_alignment_score(sequence1, sequence2), expected)

    def test_one_empty(self):
        # One sequence empty, the other non-empty
        sequence1 = "ACGT"
        sequence2 = ""
        # Each gap introduces a -2 penalty, so expected score is len("ACGT") * -2 = -8
        expected = -8
        self.assertEqual(max_alignment_score(sequence1, sequence2), expected)

    def test_single_character_match(self):
        # Single character and they match
        sequence1 = "A"
        sequence2 = "A"
        expected = 2  # match gives +2
        self.assertEqual(max_alignment_score(sequence1, sequence2), expected)

    def test_single_character_mismatch(self):
        # Single character and they mismatch
        sequence1 = "A"
        sequence2 = "G"
        expected = -1  # mismatch gives -1 (better than introducing gaps which have -2 penalty)
        self.assertEqual(max_alignment_score(sequence1, sequence2), expected)

    def test_all_match(self):
        # Multiple characters, all match
        sequence1 = "AGTAC"
        sequence2 = "AGTAC"
        # 5 matches: 5 * 2 = 10
        expected = 10
        self.assertEqual(max_alignment_score(sequence1, sequence2), expected)

    def test_simple_mismatch(self):
        # Mixed match and mismatch: "ACGT" vs "ACCT"
        sequence1 = "ACGT"
        sequence2 = "ACCT"
        # Alignment without gaps: A-A=2, C-C=2, G-C=-1, T-T=2 => total = 5
        expected = 5
        self.assertEqual(max_alignment_score(sequence1, sequence2), expected)

    def test_complex_alignment(self):
        # A known challenging alignment
        sequence1 = "GATTACA"
        sequence2 = "GCATGCU"
        # The optimal alignment score for these sequences computes to 2.
        expected = 2
        self.assertEqual(max_alignment_score(sequence1, sequence2), expected)

    def test_alternative_alignment(self):
        # Test with sequences where inserting gaps optimizes the score.
        # For instance, aligning "AGTC" with "ATC" might benefit from a gap.
        sequence1 = "AGTC"
        sequence2 = "ATC"
        # One optimal alignment:
        # A G T C
        # A - T C
        # Score: A-A: 2, G-gap: -2, T-T: 2, C-C: 2 => total = 4
        expected = 4
        self.assertEqual(max_alignment_score(sequence1, sequence2), expected)

    def test_symmetry(self):
        # Test symmetry of the alignment function: score(a,b) == score(b,a)
        sequence1 = "ACGTCG"
        sequence2 = "ACTCG"
        score1 = max_alignment_score(sequence1, sequence2)
        score2 = max_alignment_score(sequence2, sequence1)
        self.assertEqual(score1, score2)

if __name__ == "__main__":
    unittest.main()
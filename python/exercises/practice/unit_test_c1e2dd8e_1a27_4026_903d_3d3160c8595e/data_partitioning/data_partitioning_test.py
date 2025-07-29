import unittest
from data_partitioning import minimum_partitions

class TestMinimumPartitions(unittest.TestCase):
    def test_no_partition(self):
        # Scenario: no required partition because all data is already in compliant data centers.
        data_centers = ["USA", "Germany", "China"]
        data_types = ["Financial", "Personal"]
        residency_requirements = [("Financial", "USA")]
        connectivity = [("USA", "Germany"), ("Germany", "China"), ("USA", "China")]
        storage_mapping = [
            ("USA", "Financial"),
            ("Germany", "Personal"),
            ("China", "Personal")
        ]
        expected = 0
        result = minimum_partitions(data_centers, data_types, residency_requirements, connectivity, storage_mapping)
        self.assertEqual(result, expected)

    def test_one_partition(self):
        # Example scenario provided in the problem description.
        data_centers = ["USA", "Germany", "China"]
        data_types = ["Financial", "Personal"]
        residency_requirements = [("Personal", "Germany")]
        connectivity = [("USA", "Germany"), ("Germany", "China")]
        storage_mapping = [
            ("USA", "Personal"),
            ("China", "Financial")
        ]
        expected = 1
        result = minimum_partitions(data_centers, data_types, residency_requirements, connectivity, storage_mapping)
        self.assertEqual(result, expected)

    def test_multiple_partitions(self):
        # Complex scenario with multiple violations requiring multiple partitions.
        data_centers = ["A", "B", "C", "D"]
        data_types = ["X", "Y"]
        residency_requirements = [("X", "A"), ("Y", "D")]
        connectivity = [
            ("A", "B"),
            ("B", "C"),
            ("C", "D"),
            ("A", "C"),
            ("B", "D")
        ]
        storage_mapping = [
            ("A", "X"),   # A is compliant for X.
            ("B", "X"),   # Violates requirement for X (should be in A).
            ("B", "Y"),   # Violates requirement for Y (should be in D).
            ("C", "Y"),   # Violates requirement for Y.
            ("D", "Y")    # D is compliant for Y.
        ]
        # Expected partitions: 
        # Edge ("A","B") must be cut because B holds 'X' while requirement ("X","A") is violated.
        # Edge ("B","D") must be cut because B holds 'Y' while requirement ("Y","D") is violated.
        # Edge ("C","D") must be cut because C holds 'Y' while requirement ("Y","D") is violated.
        expected = 3
        result = minimum_partitions(data_centers, data_types, residency_requirements, connectivity, storage_mapping)
        self.assertEqual(result, expected)

    def test_no_connections(self):
        # When there are no connections, even if non-compliant data exists, no partitioning is needed.
        data_centers = ["A", "B"]
        data_types = ["X"]
        residency_requirements = [("X", "A")]
        connectivity = []
        storage_mapping = [
            ("B", "X")  # B holds X but it's isolated with no connecting edge to A.
        ]
        expected = 0
        result = minimum_partitions(data_centers, data_types, residency_requirements, connectivity, storage_mapping)
        self.assertEqual(result, expected)

    def test_complex_case(self):
        # A more complex test with a heterogeneous network and multiple requirements.
        data_centers = ["USA", "Canada", "Mexico", "Germany"]
        data_types = ["Tax", "Health"]
        residency_requirements = [("Tax", "USA"), ("Health", "Canada")]
        connectivity = [
            ("USA", "Canada"),
            ("Canada", "Mexico"),
            ("Mexico", "USA"),
            ("USA", "Germany"),
            ("Canada", "Germany")
        ]
        storage_mapping = [
            ("USA", "Tax"),      # USA is compliant for Tax.
            ("Canada", "Tax"),   # Violates ("Tax", "USA"); connection with USA will force cut.
            ("Canada", "Health"),# Canada is compliant for Health.
            ("Mexico", "Health"),# Violates ("Health", "Canada"); if directly connected to Canada.
            ("Germany", "Health")# Violates ("Health", "Canada"); if directly connected to Canada.
        ]
        # Expected partitions:
        # Edge ("USA", "Canada") must be cut due to Canada holding 'Tax' while requirement is ("Tax", "USA").
        # Edge ("Canada", "Mexico") must be cut since Mexico holding 'Health' must not be coupled with Canada's Health.
        # Edge ("Canada", "Germany") must be cut for the same reason with Germany.
        expected = 3
        result = minimum_partitions(data_centers, data_types, residency_requirements, connectivity, storage_mapping)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()
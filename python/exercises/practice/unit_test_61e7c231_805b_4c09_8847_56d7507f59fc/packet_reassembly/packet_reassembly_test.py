import unittest
from packet_reassembly import reassemble_file

class PacketReassemblyTest(unittest.TestCase):
    def test_successful_reassembly(self):
        packets = [
            {'packet_id': 123, 'total_packets': 5, 'packet_index': 2, 'data': 'segment2'},
            {'packet_id': 123, 'total_packets': 5, 'packet_index': 0, 'data': 'segment0'},
            {'packet_id': 123, 'total_packets': 5, 'packet_index': 1, 'data': 'segment1'},
            {'packet_id': 123, 'total_packets': 5, 'packet_index': 4, 'data': 'segment4'},
            {'packet_id': 123, 'total_packets': 5, 'packet_index': 3, 'data': 'segment3'},
        ]
        expected = "segment0segment1segment2segment3segment4"
        self.assertEqual(reassemble_file(packets), expected)

    def test_missing_packets(self):
        packets = [
            {'packet_id': 123, 'total_packets': 5, 'packet_index': 2, 'data': 'segment2'},
            {'packet_id': 123, 'total_packets': 5, 'packet_index': 0, 'data': 'segment0'},
            {'packet_id': 123, 'total_packets': 5, 'packet_index': 4, 'data': 'segment4'},
        ]
        self.assertIsNone(reassemble_file(packets))

    def test_inconsistent_total_packets(self):
        packets = [
            {'packet_id': 456, 'total_packets': 3, 'packet_index': 0, 'data': 'A'},
            {'packet_id': 456, 'total_packets': 4, 'packet_index': 1, 'data': 'B'},
        ]
        with self.assertRaises(ValueError):
            reassemble_file(packets)

    def test_invalid_packet_index(self):
        packets = [
            {'packet_id': 789, 'total_packets': 3, 'packet_index': 5, 'data': 'X'},
            {'packet_id': 789, 'total_packets': 3, 'packet_index': 1, 'data': 'Y'},
        ]
        with self.assertRaises(ValueError):
            reassemble_file(packets)

    def test_empty_input(self):
        self.assertIsNone(reassemble_file([]))

    def test_single_packet_file(self):
        packets = [
            {'packet_id': 999, 'total_packets': 1, 'packet_index': 0, 'data': 'complete'}
        ]
        self.assertEqual(reassemble_file(packets), "complete")

    def test_duplicate_packet_index(self):
        packets = [
            {'packet_id': 111, 'total_packets': 3, 'packet_index': 0, 'data': 'first'},
            {'packet_id': 111, 'total_packets': 3, 'packet_index': 0, 'data': 'duplicate'},
        ]
        with self.assertRaises(ValueError):
            reassemble_file(packets)

    def test_large_file_reassembly(self):
        # Generate 1000 packets
        packets = [
            {'packet_id': 222, 'total_packets': 1000, 'packet_index': i, 'data': f'data{i}'}
            for i in range(1000)
        ]
        # Shuffle to test out-of-order handling
        import random
        random.shuffle(packets)
        expected = ''.join(f'data{i}' for i in range(1000))
        self.assertEqual(reassemble_file(packets), expected)

    def test_different_packet_ids(self):
        packets = [
            {'packet_id': 333, 'total_packets': 2, 'packet_index': 0, 'data': 'A'},
            {'packet_id': 444, 'total_packets': 2, 'packet_index': 1, 'data': 'B'},
        ]
        self.assertIsNone(reassemble_file(packets))

    def test_negative_packet_index(self):
        packets = [
            {'packet_id': 555, 'total_packets': 2, 'packet_index': -1, 'data': 'neg'},
            {'packet_id': 555, 'total_packets': 2, 'packet_index': 0, 'data': 'pos'},
        ]
        with self.assertRaises(ValueError):
            reassemble_file(packets)

    def test_zero_total_packets(self):
        packets = [
            {'packet_id': 666, 'total_packets': 0, 'packet_index': 0, 'data': 'zero'},
        ]
        with self.assertRaises(ValueError):
            reassemble_file(packets)

    def test_missing_dictionary_keys(self):
        packets = [
            {'packet_id': 777, 'total_packets': 1},  # Missing 'data' and 'packet_index'
        ]
        with self.assertRaises(KeyError):
            reassemble_file(packets)

    def test_empty_data_packets(self):
        packets = [
            {'packet_id': 888, 'total_packets': 2, 'packet_index': 0, 'data': ''},
            {'packet_id': 888, 'total_packets': 2, 'packet_index': 1, 'data': ''},
        ]
        self.assertEqual(reassemble_file(packets), '')

if __name__ == '__main__':
    unittest.main()
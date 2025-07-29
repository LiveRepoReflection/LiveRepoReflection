import unittest
from transaction_analyzer import analyze_transaction_logs

class TransactionAnalyzerTest(unittest.TestCase):
    def test_simple_committed_transaction(self):
        logs = [
            "1,tx1,PREPARE,1678886400,",
            "1,tx1,VOTE_COMMIT,1678886401,",
            "2,tx1,PREPARE,1678886402,",
            "2,tx1,VOTE_COMMIT,1678886403,",
            "1,tx1,COMMIT,1678886404,",
            "2,tx1,COMMIT,1678886405,"
        ]
        expected = {"tx1": "COMMITTED"}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_simple_rolled_back_transaction(self):
        logs = [
            "1,tx2,PREPARE,1678886406,",
            "2,tx2,PREPARE,1678886407,",
            "1,tx2,VOTE_ROLLBACK,1678886408,",
            "2,tx2,VOTE_ROLLBACK,1678886409,",
            "1,tx2,ROLLBACK,1678886410,",
            "2,tx2,ROLLBACK,1678886411,"
        ]
        expected = {"tx2": "ROLLED_BACK"}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_indeterminate_transaction(self):
        logs = [
            "1,tx3,PREPARE,1678886412,",
            "2,tx3,PREPARE,1678886413,",
            "1,tx3,VOTE_COMMIT,1678886414,"
        ]
        expected = {"tx3": "INDETERMINATE"}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_mixed_transactions(self):
        logs = [
            "1,tx1,PREPARE,1678886400,",
            "1,tx1,VOTE_COMMIT,1678886401,",
            "2,tx1,PREPARE,1678886402,",
            "2,tx1,VOTE_COMMIT,1678886403,",
            "1,tx1,COMMIT,1678886404,",
            "2,tx1,COMMIT,1678886405,",
            "1,tx2,PREPARE,1678886406,",
            "2,tx2,PREPARE,1678886407,",
            "1,tx2,VOTE_ROLLBACK,1678886408,",
            "2,tx2,VOTE_ROLLBACK,1678886409,",
            "1,tx2,ROLLBACK,1678886410,",
            "2,tx2,ROLLBACK,1678886411,",
            "1,tx3,PREPARE,1678886412,",
            "2,tx3,PREPARE,1678886413,",
            "1,tx3,VOTE_COMMIT,1678886414,"
        ]
        expected = {
            "tx1": "COMMITTED",
            "tx2": "ROLLED_BACK",
            "tx3": "INDETERMINATE"
        }
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_partial_commit(self):
        logs = [
            "1,tx4,PREPARE,1678886500,",
            "2,tx4,PREPARE,1678886501,",
            "3,tx4,PREPARE,1678886502,",
            "1,tx4,VOTE_COMMIT,1678886503,",
            "2,tx4,VOTE_COMMIT,1678886504,",
            "3,tx4,VOTE_COMMIT,1678886505,",
            "1,tx4,COMMIT,1678886506,",
            "2,tx4,COMMIT,1678886507,"
            # Missing COMMIT for node 3
        ]
        expected = {"tx4": "INDETERMINATE"}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_mixed_votes(self):
        logs = [
            "1,tx5,PREPARE,1678886600,",
            "2,tx5,PREPARE,1678886601,",
            "1,tx5,VOTE_COMMIT,1678886602,",
            "2,tx5,VOTE_ROLLBACK,1678886603,",
            "1,tx5,ROLLBACK,1678886604,",
            "2,tx5,ROLLBACK,1678886605,"
        ]
        expected = {"tx5": "ROLLED_BACK"}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_only_prepare_logs(self):
        logs = [
            "1,tx6,PREPARE,1678886700,",
            "2,tx6,PREPARE,1678886701,"
        ]
        expected = {"tx6": "INDETERMINATE"}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_prepare_and_vote_only(self):
        logs = [
            "1,tx7,PREPARE,1678886800,",
            "2,tx7,PREPARE,1678886801,",
            "1,tx7,VOTE_COMMIT,1678886802,",
            "2,tx7,VOTE_COMMIT,1678886803,"
        ]
        expected = {"tx7": "INDETERMINATE"}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_some_commits_some_rollbacks(self):
        logs = [
            "1,tx8,PREPARE,1678886900,",
            "2,tx8,PREPARE,1678886901,",
            "1,tx8,VOTE_COMMIT,1678886902,",
            "2,tx8,VOTE_COMMIT,1678886903,",
            "1,tx8,COMMIT,1678886904,",
            "2,tx8,ROLLBACK,1678886905,"  # Conflicting state
        ]
        expected = {"tx8": "INDETERMINATE"}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_out_of_order_timestamps(self):
        logs = [
            "1,tx9,COMMIT,1678887000,",
            "1,tx9,VOTE_COMMIT,1678886999,",
            "1,tx9,PREPARE,1678886998,",
            "2,tx9,COMMIT,1678887001,",
            "2,tx9,VOTE_COMMIT,1678886997,",
            "2,tx9,PREPARE,1678886996,"
        ]
        expected = {"tx9": "COMMITTED"}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_large_number_of_nodes(self):
        logs = []
        # Create a committed transaction with 100 nodes
        for i in range(1, 101):
            logs.extend([
                f"{i},tx10,PREPARE,{1678888000+i},",
                f"{i},tx10,VOTE_COMMIT,{1678888100+i},",
                f"{i},tx10,COMMIT,{1678888200+i},"
            ])
        expected = {"tx10": "COMMITTED"}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_large_number_of_transactions(self):
        logs = []
        # Create 1000 committed transactions
        for i in range(1, 1001):
            tx_id = f"tx{1000+i}"
            logs.extend([
                f"1,{tx_id},PREPARE,{1678890000+i},",
                f"1,{tx_id},VOTE_COMMIT,{1678890000+i+1},",
                f"1,{tx_id},COMMIT,{1678890000+i+2},"
            ])
        
        # Expected output
        expected = {}
        for i in range(1, 1001):
            expected[f"tx{1000+i}"] = "COMMITTED"
        
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_empty_logs(self):
        logs = []
        expected = {}
        self.assertEqual(analyze_transaction_logs(logs), expected)

    def test_invalid_log_format(self):
        logs = [
            "1,tx11,PREPARE,1678889000,",
            "invalid_log_format",  # Invalid format
            "2,tx11,VOTE_COMMIT,1678889001,",
            "1,tx11,COMMIT,1678889002,",
            "2,tx11,COMMIT,1678889003,"
        ]
        # The function should handle the invalid log and still process the valid ones
        with self.assertRaises(ValueError):
            analyze_transaction_logs(logs)

    def test_unknown_log_type(self):
        logs = [
            "1,tx12,PREPARE,1678889100,",
            "1,tx12,UNKNOWN_TYPE,1678889101,",  # Unknown log type
            "1,tx12,VOTE_COMMIT,1678889102,",
            "1,tx12,COMMIT,1678889103,"
        ]
        # The function should handle the unknown log type
        with self.assertRaises(ValueError):
            analyze_transaction_logs(logs)

if __name__ == "__main__":
    unittest.main()
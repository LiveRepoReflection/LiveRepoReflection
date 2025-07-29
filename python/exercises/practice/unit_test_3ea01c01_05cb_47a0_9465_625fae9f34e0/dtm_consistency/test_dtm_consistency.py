import unittest
import os
import threading
import tempfile
import shutil
from dtm_consistency import DTM

class TestDTMConsistency(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.test_dir, "dtm.log")
        self.dtm = DTM(self.log_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_begin_transaction(self):
        self.dtm.begin_transaction(1)
        self.assertEqual(self.dtm.get_transaction_state(1), "ACTIVE")

    def test_duplicate_transaction(self):
        self.dtm.begin_transaction(1)
        with self.assertRaises(ValueError):
            self.dtm.begin_transaction(1)

    def test_prepare(self):
        self.dtm.begin_transaction(1)
        self.dtm.prepare(1, 101)
        self.assertEqual(self.dtm.get_transaction_state(1), "PREPARED")

    def test_commit_success(self):
        self.dtm.begin_transaction(1)
        self.dtm.prepare(1, 101)
        self.dtm.commit(1)
        self.assertEqual(self.dtm.get_transaction_state(1), "COMMITTED")

    def test_commit_failure(self):
        self.dtm.begin_transaction(1)
        with self.assertRaises(ValueError):
            self.dtm.commit(1)

    def test_rollback(self):
        self.dtm.begin_transaction(1)
        self.dtm.prepare(1, 101)
        self.dtm.rollback(1)
        self.assertEqual(self.dtm.get_transaction_state(1), "ROLLED_BACK")

    def test_nonexistent_transaction(self):
        self.assertEqual(self.dtm.get_transaction_state(999), "NON_EXISTENT")

    def test_concurrent_prepares(self):
        self.dtm.begin_transaction(1)
        
        def prepare_service(service_id):
            self.dtm.prepare(1, service_id)

        threads = []
        for i in range(101, 111):
            t = threading.Thread(target=prepare_service, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        self.assertEqual(self.dtm.get_transaction_state(1), "PREPARED")

    def test_log_file_created(self):
        self.dtm.begin_transaction(1)
        self.assertTrue(os.path.exists(self.log_file))

    def test_log_file_content(self):
        self.dtm.begin_transaction(1)
        self.dtm.prepare(1, 101)
        self.dtm.commit(1)
        
        with open(self.log_file, 'r') as f:
            content = f.read()
            self.assertIn("BEGIN 1", content)
            self.assertIn("PREPARE 1 101", content)
            self.assertIn("COMMIT 1", content)

if __name__ == '__main__':
    unittest.main()
import unittest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from synthesizer import *
import hashlib

class TestDividebyzero(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = './tmpdir_dividebyzero'
        return super().setUp()
    def tearDown(self) -> None:
        if self._outcome.errors[-1][1] is None and len(self._outcome.result.failures) ==0:
            if os.path.exists(self.tmp_dir):
                shutil.rmtree(self.tmp_dir)
        return super().tearDown()
    
    def test_1(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/dividebyzero/test1.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/dividebyzero/test1_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        ALL_TARGET_UB = [TargetUB.DivideZero]
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, given_ALL_TARGET_UB=ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_2(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/dividebyzero/test2.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/dividebyzero/test2_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        ALL_TARGET_UB = [TargetUB.DivideZero]
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, given_ALL_TARGET_UB=ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_3(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/dividebyzero/test3.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/dividebyzero/test3_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        ALL_TARGET_UB = [TargetUB.DivideZero]
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, given_ALL_TARGET_UB=ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
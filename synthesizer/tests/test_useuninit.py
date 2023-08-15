import unittest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from synthesizer import *
import config
import hashlib

class TestUseuninit(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = './tmpdir_useuninit'
        return super().setUp()
    def tearDown(self) -> None:
        if self._outcome.errors[-1][1] is None and len(self._outcome.result.failures) ==0:
            if os.path.exists(self.tmp_dir):
                shutil.rmtree(self.tmp_dir)
        return super().tearDown()

    def check_sanitizer(self, mut_src) -> bool:
        ret = os.system(f"clang -w -O0 -fsanitize=memory {mut_src} -o check.out")
        if ret != 0:
            return False
        ret = os.system("./check.out >/dev/null 2>&1")
        if ret == 0:
            return False
        os.remove("./check.out")
        return True
    
    def test_1(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/useuninit/test1.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/useuninit/test1_oracle1.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/useuninit/test1_oracle2.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/useuninit/test1_oracle3.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/useuninit/test1_oracle4.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        ALL_TARGET_UB = [TargetUB.UseUninit]
        set_mut_md5 = []
        for _ in range(10): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'UNINIT\_\w+', b'UNINIT_var', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_2(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/useuninit/test2.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/useuninit/test2_oracle1.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/useuninit/test2_oracle2.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/useuninit/test2_oracle3.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        ALL_TARGET_UB = [TargetUB.UseUninit]
        set_mut_md5 = []
        for _ in range(10): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'UNINIT\_\w+', b'UNINIT_var', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)

    
if __name__ == '__main__':
    unittest.main()
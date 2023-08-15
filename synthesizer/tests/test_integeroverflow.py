import unittest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from synthesizer import *
import hashlib

class TestIntegeroverflow(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = './tmpdir_integeroverflow'
        return super().setUp()
    def tearDown(self) -> None:
        if self._outcome.errors[-1][1] is None and len(self._outcome.result.failures) ==0:
            if os.path.exists(self.tmp_dir):
                shutil.rmtree(self.tmp_dir)
        return super().tearDown()
    
    def check_sanitizer(self, mut_src) -> bool:
        ret = os.system(f"gcc -w -O0 -fsanitize=undefined -fno-sanitize-recover=all {mut_src} -o check.out")
        if ret != 0:
            return False
        ret = os.system("./check.out >/dev/null 2>&1")
        if ret == 0:
            return False
        os.remove("./check.out")
        return True
    
    def test_1(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test1.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test1_oracle1.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test1_oracle2.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.Zero
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(re.escape(b'#include <stdint.h>'), b'', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_2(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test2.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test2_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.Value
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'a = safe_add_func_int32_t_s_s\(a, [-|\d]+\);//UBFUZZ ', b'a = safe_add_func_int32_t_s_s(a, 100);//UBFUZZ ', mut)
                mut = re.sub(re.escape(b'#include <stdint.h>'), b'', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_3(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test3.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test3_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.MaxMin
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(re.escape(b'#include <stdint.h>'), b'', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_4(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test4.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test4_oracle1.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test4_oracle2.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.Value
        set_mut_md5 = []
        for _ in range(10): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(re.escape(b'#include <stdint.h>'), b'', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_5(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test5.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test5_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.Value
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(re.escape(b'#include <stdint.h>'), b'', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_6(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test6.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test6_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.Value
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(re.escape(b'#include <stdint.h>'), b'', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_7(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test7.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test7_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.Value
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(re.escape(b'#include <stdint.h>'), b'', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_8(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test8.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test8_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.Value
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(re.escape(b'#include <stdint.h>'), b'', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_9(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test9.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test9_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.Value
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(re.escape(b'#include <stdint.h>'), b'', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_10(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test10.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test10_oracle1.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test10_oracle2.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test10_oracle3.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test10_oracle4.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.Value
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(re.escape(b'#include <stdint.h>'), b'', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_11(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/integeroverflow/test11.c'))
        oracle_files = [
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.IntegerOverflow]
        CONFIG_IntegerOverflow = MutIntegerOverflow.Value
        set_mut_md5 = []
        for _ in range(5): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow)
            mutated_files = syner.synthesizer(src_code_file)
            self.assertTrue(len(mutated_files)==0)

    
if __name__ == '__main__':
    unittest.main()
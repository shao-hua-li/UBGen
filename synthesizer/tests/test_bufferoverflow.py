import unittest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from synthesizer import *
import hashlib

class TestBufferoverflow(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = './tmpdir_bufferoverflow'
        self.failed = True
        return super().setUp()
    def tearDown(self) -> None:
        if self._outcome.errors[-1][1] is None and len(self._outcome.result.failures) ==0:
            if os.path.exists(self.tmp_dir):
                shutil.rmtree(self.tmp_dir)
        return super().tearDown()

    def check_sanitizer(self, mut_src) -> bool:
        ret = os.system(f"gcc -w -O0 -fsanitize=address {mut_src} -o check.out")
        if ret != 0:
            return False
        ret = os.system("./check.out >/dev/null 2>&1")
        if ret == 0:
            return False
        os.remove("./check.out")
        return True

    def test_1(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test1.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test1_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'[\+|\-|\d]+\/\*UBFUZZ\*\/', b'+2/*UBFUZZ*/', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_2(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test2.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test2_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'[\+|\-|\d]+\/\*UBFUZZ\*\/', b'+2/*UBFUZZ*/', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    
    def test_3(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test3.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test3_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'[\+|\-|\d]+\/\*UBFUZZ\*\/', b'+2/*UBFUZZ*/', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        self.assertTrue(False)
    
    def test_4(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test4.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test4_oracle1.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test4_oracle2.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test4_oracle3.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'[\+|\d]+\/\*UBFUZZ\*\/', b'+2/*UBFUZZ*/', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        for oracle_i in range(len(oracle_files)):
            if oracle_md5[oracle_i] not in set_mut_md5:
                print("{} not found!".format(oracle_files[oracle_i].split('/')[-1]))
        self.assertTrue(False)
    
    def test_5(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test5.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test5_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        set_mut_md5 = []
        for _ in range(100): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'[\+|\-|\d]+\/\*UBFUZZ\*\/', b'+2/*UBFUZZ*/', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        print(oracle_md5)
        print(list(set(set_mut_md5)))
        self.assertTrue(False)
    
    def test_6(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test6.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test6_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'[\+|\-|\d]+\/\*UBFUZZ\*\/', b'+2/*UBFUZZ*/', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        for oracle_i in range(len(oracle_files)):
            if oracle_md5[oracle_i] not in set_mut_md5:
                print("{} not found!".format(oracle_files[oracle_i].split('/')[-1]))
        self.assertTrue(False)

    def test_7(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test7.c'))
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        for _ in range(1): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            self.assertTrue(len(mutated_files)==0)

    def test_8(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test8.c'))
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        for _ in range(1): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            self.assertTrue(len(mutated_files)==0)
    
    def test_9(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test9.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test9_oracle1.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'[\+|\-|\d]+\/\*UBFUZZ\*\/', b'+2/*UBFUZZ*/', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        for oracle_i in range(len(oracle_files)):
            if oracle_md5[oracle_i] not in set_mut_md5:
                print("{} not found!".format(oracle_files[oracle_i].split('/')[-1]))
        self.assertTrue(False)
    
    def test_10(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test10.c'))
        oracle_files = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test10_oracle1.c')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test10_oracle2.c')),
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        set_mut_md5 = []
        for _ in range(20): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            for mut_src in mutated_files:
                self.assertTrue(self.check_sanitizer(mut_src))
                with open(mut_src, 'rb') as f:
                    mut = f.read().replace(b'\n', b'')
                mut = re.sub(b'[\+|\-|\d]+\/\*UBFUZZ\*\/', b'+2/*UBFUZZ*/', mut)
                mut_md5 = hashlib.md5(mut).hexdigest()
                self.assertTrue(mut_md5 in oracle_md5)
                set_mut_md5.append(mut_md5)
                if len(set(set_mut_md5)) == len(set(oracle_md5)):
                    self.assertTrue(True)
                    return
        for oracle_i in range(len(oracle_files)):
            if oracle_md5[oracle_i] not in set_mut_md5:
                print("{} not found!".format(oracle_files[oracle_i].split('/')[-1]))
        self.assertTrue(False)
    
    def test_11(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test11.c'))
        oracle_files = [
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        for _ in range(3): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            self.assertTrue(len(mutated_files)==0)
    
    def test_12(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test12.c'))
        oracle_files = [
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        for _ in range(3): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            self.assertTrue(len(mutated_files)==0)
    
    def test_13(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/bufferoverflow/test13.c'))
        oracle_files = [
        ]
        oracle_md5 = []
        for oracle_f in oracle_files:
            with open(oracle_f, 'rb') as f:
                oracle = f.read().replace(b'\n', b'')
            oracle_md5.append(hashlib.md5(oracle).hexdigest())
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
        ALL_TARGET_UB = [TargetUB.BufferOverflow]
        for _ in range(3): # due to randomness of synthesizer
            syner = Synthesizer(100, self.tmp_dir, TOOL_STACKTOHEAP, ALL_TARGET_UB)
            mutated_files = syner.synthesizer(src_code_file)
            self.assertTrue(len(mutated_files)==0)

if __name__ == '__main__':
    unittest.main()
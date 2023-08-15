import unittest
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../auto_reduce/diopter')))
from diopter.compiler import SourceProgram, CompilationSetting, CompilerExe, OptLevel, Language
from diopter.sanitizer import Sanitizer
from diopter.reducer import Reducer, ReductionCallback
from diopter.preprocessor import preprocess_csmith_program
from ccbuilder import CompilerProject
from shutil import which, copy
import subprocess as sp
from tempfile import NamedTemporaryFile

def run_cmd(cmd, time_out=10):
    if type(cmd) is not list:
        cmd = cmd.split(' ')
    ret, out = 0, ''
    try:
        process = sp.run(cmd, timeout=time_out, capture_output=True)
        ret = process.returncode
        out = process.stdout.decode('utf-8')
    except Exception as e:
        print(e)
        ret = 1
    return ret, out

class TestAll(unittest.TestCase):

    def setUp(self) -> None:
        self.gcc = CompilerExe(CompilerProject.GCC, which("gcc-12"), "origin/main")
        self.clang = CompilerExe(CompilerProject.LLVM, which("clang-14"), "origin/main")
        self.cc_flag = ("-fsanitize=address,undefined","-fno-sanitize-recover=all")
        self.sanitization = Sanitizer(gcc=self.gcc, clang=self.clang, check_warnings_and_sanitizer_opt_level=OptLevel.O3)

        self.csmith_include = os.environ['CSMITH_HOME']
        self.tool_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../build/bin'))
        with NamedTemporaryFile(suffix=".c") as ntf:
            ntf.close()
        self.tmpfile = ntf.name
        return super().setUp()

    def tearDown(self) -> None:
        os.remove(self.tmpfile)
        return super().tearDown()
    
    def construct_program(self, src_code_file):
        with open(src_code_file) as f:
            src_code_lines = f.readlines()
        src_code = []
        for line in src_code_lines:
            if line.strip() != '':
                src_code.append(line)
        src_code = '\n'.join(src_code)
        return SourceProgram(
                code=src_code,
                language=Language.C,
                available_macros=(),
                defined_macros=(),
                include_paths=(f"{self.csmith_include}/include",),
                system_include_paths=(),
                flags=(),
            )
    
    def tool_addbraces(self, src_code_file):
        cmd = f'{self.tool_path}/tool-addbraces {src_code_file} -- -w -I{self.csmith_include}/include'
        ret, out = run_cmd(cmd)
        if ret != 0:
            return 'Error in tool-addbraces.'
        return True
    
    def tool_addarrayindex(self, src_code_file):
        cmd = f'{self.tool_path}/tool-addarrayindex {src_code_file} -- -w -I{self.csmith_include}/include'
        ret, out = run_cmd(cmd)
        if ret != 0:
            return 'Error in tool-addarrayindex.'
        return True
    
    def tool_instrumenter(self, src_code_file):
        cmd = f'{self.tool_path}/tool-instrumenter {src_code_file} -- -w -I{self.csmith_include}/include'
        ret, out = run_cmd(cmd)
        if ret != 0:
            return 'Error in tool-instrumenter.'
        return True
    
    def tool_stacktoheap(self, src_code_file, mut_prob=50):
        cmd = f'{self.tool_path}/tool-stacktoheap {src_code_file} --mutate-prob {mut_prob} -- -w -I{self.csmith_include}/include'
        ret, out = run_cmd(cmd)
        if ret != 0:
            return 'Error in tool-stacktoheap.'
        return True

    def test_0(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/test0.c'))
        copy(src_code_file, self.tmpfile)
        self.assertTrue(self.tool_addbraces(self.tmpfile))
        self.assertTrue(self.tool_addarrayindex(self.tmpfile))
        self.assertTrue(self.tool_instrumenter(self.tmpfile))
        self.assertTrue(self.tool_stacktoheap(self.tmpfile))

        program = self.construct_program(self.tmpfile)
        preprocessed = preprocess_csmith_program(program, self.gcc)
        self.assertTrue(preprocessed)

        program = preprocessed
        sanitization_ret = self.sanitization.check_for_compiler_warnings(program)
        self.assertTrue(sanitization_ret)
    
    def test_many(self):
        for _ in range(10):
            run_cmd(f'{self.csmith_include}/bin/csmith --output {self.tmpfile}')
            self.assertTrue(self.tool_addbraces(self.tmpfile))
            self.assertTrue(self.tool_addarrayindex(self.tmpfile))
            self.assertTrue(self.tool_instrumenter(self.tmpfile))
            self.assertTrue(self.tool_stacktoheap(self.tmpfile))

            program = self.construct_program(self.tmpfile)
            preprocessed = preprocess_csmith_program(program, self.gcc)
            self.assertTrue(preprocessed)

            program = preprocessed
            sanitization_ret = self.sanitization.check_for_compiler_warnings(program)
            self.assertTrue(sanitization_ret)
    
    def test_stacktoheap_0(self):
        src_code_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testcases/test0.c'))
        copy(src_code_file, self.tmpfile)
        self.assertTrue(self.tool_stacktoheap(self.tmpfile, mut_prob=0))

        program = self.construct_program(self.tmpfile)
        preprocessed = preprocess_csmith_program(program, self.gcc)
        self.assertTrue(preprocessed)

        program = preprocessed
        sanitization_ret = self.sanitization.check_for_compiler_warnings(program)
        self.assertTrue(sanitization_ret)

if __name__ == '__main__':
    unittest.main()
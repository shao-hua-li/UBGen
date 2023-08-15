from synthesizer import *
from pathlib import Path
import subprocess as sp
import shutil, os, re
from config import *
from glob import glob

syner = Synthesizer(
    prob=100,
    tmp_dir='./test'
)

def run_sanitizer(src):
    try:
        process = sp.run(f'{CC} {COMPILE_ARGS} -w -O0 {src} -fsanitize=address -o test.out'.split(' '), capture_output=True, timeout=5)
    except:
        return -1
    if process.returncode != 0:
        print(process.stderr)
        return -1
        # exit(1)
    try:
        process = sp.run('./test.out', capture_output=True, timeout=2)
    except:
        os.remove('test.out')
        return -1
    if 'null' in process.stdout.decode('utf-8'):
        print(src)
        assert False
    os.remove('test.out')
    return process.returncode

def test_many():

    fail_syner = 0
    fail_instr = 0
    for test_i in range(100):
        test = './test/test.c'
        test_syn = './test/test_syn.c'
        while True:
            try:
                process = sp.run(f'csmith > {test}', shell=True, capture_output=True, timeout=5)
            except:
                continue
            if process.returncode == 0:
                break

        # mutate
        try:
            mutated_files = syner.synthesizer(test)
        except InstrumentError as e:
            shutil.copy(test, test.replace('.c', f'_fail_instr_{fail_instr}.c'))
            fail_instr += 1
            print(f'Test {test_i} failed due to InstrumentError: {e}.')
            continue
        except Exception as e:
            shutil.copy(test, test.replace('.c', f'_fail_syner_{fail_syner}.c'))
            fail_syner+=1
            print(f'Test {test_i} failed. Fail syner on {str(test)}', e)
            continue

        for mutated_f in mutated_files:
            ret = run_sanitizer(mutated_f)
            os.remove(mutated_f)

        print(f"Test {test_i} succeed! Generated {len(mutated_files)} mutated files.")

def test_one(test):
    mutated_files = syner.synthesizer(test, 5)
    for mutated_f in mutated_files:
            ret = run_sanitizer(mutated_f)
            if ret == -1:
                exit(1)
    print(f'Test {test} succeed!')


if __name__=='__main__':
    test_one('./test0.c')
    # test_many()

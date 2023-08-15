#!/usr/bin/env python3
import argparse, os, requests, zipfile, shutil
from pathlib import Path
from synthesizer.synthesizer import Synthesizer
from synthesizer.config import *
from tempfile import NamedTemporaryFile, TemporaryDirectory, TemporaryFile

def run_cmd(cmd, timeout, out_file):
    ret = os.system(f"ASAN_OPTIONS=detect_leaks=0,detect_stack_use_after_return=1 timeout {timeout} {cmd} > {out_file} 2>&1");
    return ret >> 8

def string_to_targetub(ub_str: str) -> TargetUB:
    match ub_str:
        case "buffer-overflow" | "0" | "(0)":
            return TargetUB.BufferOverflow
        case "division-by-zero" | "1" | "(1)":
            return TargetUB.DivideZero
        case "null-pointer-dereference" | "2" | "(2)":
            return TargetUB.NullPtrDeref
        case "use-after-free" | "3" | "(3)":
            return TargetUB.UseAfterFree
        case "use-after-scope" | "4" | "(4)":
            return TargetUB.UseAfterScope
        case "double-free" | "5" | "(5)":
            return TargetUB.DoubleFree
        case "integer-overflow" | "6" | "(6)":
            return TargetUB.IntegerOverflow
        case "out-of-bound" | "7" | "(7)":
            return TargetUB.OutBound
        case "use-of-uninit" | "8" | "(8)":
            return TargetUB.UseUninit
        case _:
            return TargetUB.ERROR

def install_csmith():
    csmith_home = Path(__file__).parent / "csmith_install"
    with NamedTemporaryFile(suffix=".zip", mode="rb", delete=True) as f, TemporaryDirectory() as csmith_src:
        csmith_src_zip = f.name
        response = requests.get("https://github.com/csmith-project/csmith/archive/refs/tags/csmith-2.3.0.zip")
        if response.status_code == 200:
            with open(csmith_src_zip, "wb") as f:
                f.write(response.content)
        with zipfile.ZipFile(csmith_src_zip, "r") as zip_ref:
            zip_ref.extractall(csmith_src)
        os.system(f'cd {csmith_src}/csmith-csmith-2.3.0/ && cmake -DCMAKE_INSTALL_PREFIX={csmith_home} . && make && make install')

def check_available_csmith(csmith_home:str="csmith") -> bool:
    if csmith_home == "csmith":
        csmith_home = Path(__file__).parent / "csmith_install"
        if not csmith_home.exists():
            install_csmith()
    with NamedTemporaryFile(suffix=".c", mode="rb", delete=True) as tmp_src:
        ret = os.system(f"{csmith_home}/bin/csmith > {tmp_src.name}")
        if ret != 0:
            return False
        ret = os.system(f"{CC} {COMPILE_ARGS} {tmp_src.name} -o /dev/null -w")
        if ret != 0:
            return False
        return True

def generate_csmith_src() -> str:
    src = NamedTemporaryFile(suffix=".c", mode="w", delete=False)
    src.close()
    src = src.name
    csmith_exe = 'null'
    while 1:
        if Path(csmith_exe).exists():
            os.remove(csmith_exe)
        with NamedTemporaryFile(suffix="_csmith.exe", mode="w", delete=False) as f:
            f.close()
            csmith_exe = f.name
            cmd = f"{CSMITH_HOME}/bin/csmith {CSMITH_USER_OPTIONS} --output {src}"
            ret = run_cmd(cmd, CSMITH_TIMEOUT, "/dev/null")
            if ret != 0:
                continue
            if os.path.getsize(src) >= MIN_PROGRAM_SIZE:
                cmd = f"{CC} {COMPILE_ARGS} {CSMITH_CHECK_OPTIONS} {src} -o {csmith_exe}"
                ret = run_cmd(cmd, COMPILER_TIMEOUT, "/dev/null")
                if ret != 0:
                    continue
                ret = run_cmd(csmith_exe, PROG_TIMEOUT, "/dev/null")
                if ret != 0:
                    continue
                break
            else:
                continue
    if Path(csmith_exe).exists():
        os.remove(csmith_exe)
    return src
    

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Sythesize programs with undefined behaviors.")
    parser.add_argument("--ub", required=True, help=\
                        "The type of undefined behavior to synthesize. Supported types are: \
                            (0) buffer-overflow , \
                            (1) division-by-zero, \
                            (2) null-pointer-dereference, \
                            (3) use-after-free, \
                            (4) use-after-scope, \
                            (5) double-free, \
                            (6) integer-overflow, \
                            (7) out-of-bound, \
                            (8) use-of-uninit \
                        ")
    parser.add_argument("--out", type=Path, required=True, help="The output directory to store the synthesized programs.")
    parser.add_argument("--csmith-home", type=str, default="csmith", help="The path to the csmith home.")

    args = parser.parse_args()

    target_ub = string_to_targetub(args.ub)
    if target_ub == TargetUB.ERROR:
        print(f"Invalid undefined behavior type: {args.ub}")
        exit(1)
    if has_overlap([TargetUB.DoubleFree, TargetUB.MemoryLeak], ALL_TARGET_UB):
        TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100' # free statements will only be inserted with p=100

    
    if not check_available_csmith(args.csmith_home):
        print(f"Cannot find csmith binary at {args.csmith}. Please use --csmith to specify the path to the csmith binary.")
        exit(1)

    args.out.mkdir(parents=True, exist_ok=True)

    while True:
        with TemporaryDirectory() as tmp_dir:
            SYNER = Synthesizer(prob=100, tmp_dir=tmp_dir, given_ALL_TARGET_UB=[target_ub])
            src = generate_csmith_src()
            try:
                mutated_files = SYNER.synthesizer(src, MUTATE_NUM)
            except:
                os.remove(src)
                continue
            os.remove(src)
            if len(mutated_files) == 0:
                continue
            for mutated_file in mutated_files:
                shutil.copy(mutated_file, args.out)
                os.remove(mutated_file)
        break



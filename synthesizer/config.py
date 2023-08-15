from enum import Enum, auto
import os

CC = "clang-13"

# csmith config
CSMITH_HOME = os.environ['CSMITH_HOME']
CSMITH_HEADER = f"-I{CSMITH_HOME}/include"
MIN_PROGRAM_SIZE = 8000 # programs shorter than this many bytes are too boring to test
CSMITH_TIMEOUT = 10
CSMITH_USER_OPTIONS = "--no-packed-struct --ccomp --no-volatiles --no-volatile-pointers"
CSMITH_CHECK_OPTIONS = "-fsanitize=address,undefined -fno-sanitize-recover=all"

COMPILE_ARGS = f" -I{CSMITH_HOME}/include "
COMPCERT = "ccomp -interp -fstruct-passing "

# mutated configurations for each seed
MUTATE_TIMEOUT = 3
MUTATE_NUM = 2

# program config
COMPILER_TIMEOUT = 10
PROG_TIMEOUT = 2

# Synthesizer config
class TargetUB(Enum):
    BufferOverflow  = auto()
    UseAfterScope   = auto()
    UseAfterFree    = auto()
    DoubleFree      = auto()
    NullPtrDeref    = auto()
    IntegerOverflow = auto()
    DivideZero      = auto()
    OutBound        = auto()
    UseUninit       = auto()
    MemoryLeak      = auto()
    ERROR           = auto()

    def __eq__(self, other: object) -> bool:
        return self.value == other.value

def has_overlap(l1, l2) -> bool:
    for item1 in l1:
        for item2 in l2:
            if item1 == item2:
                return True
    return False

# IntegerOverflow mutation type
class MutIntegerOverflow(Enum):
    Random  = auto() # randomly select a mutation
    Zero    = auto() # assign zero
    Value   = auto() # assign a random value within range
    MaxMin  = auto() # assign either max or min value

Synthesizer_tmp_dir = './mutate'
DYNAMIC_ANALYZER = os.path.join(os.path.dirname(__file__), "../dynamic_analyzer/build/bin")
TOOL_ADDBRACES = f'{DYNAMIC_ANALYZER}/tool-addbraces'
TOOL_ADDARRAYINDEX = f'{DYNAMIC_ANALYZER}/tool-addarrayindex'
TOOL_ADDINTEGER = f'{DYNAMIC_ANALYZER}/tool-addinteger'
TOOL_INSTRUMENTER = f'{DYNAMIC_ANALYZER}/tool-instrumenter'
TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 0'
ALL_TARGET_UB = [TargetUB.MemoryLeak]

CONFIG_IntegerOverflow = MutIntegerOverflow.Value # configure this when use TargetUB.IntegerOverflow
CSMITH_USER_OPTIONS += " --no-safe-math"
if has_overlap([TargetUB.DoubleFree, TargetUB.MemoryLeak], ALL_TARGET_UB):
    TOOL_STACKTOHEAP = f'{DYNAMIC_ANALYZER}/tool-stacktoheap --mutate-prob 100' # free statements will only be inserted with p=100

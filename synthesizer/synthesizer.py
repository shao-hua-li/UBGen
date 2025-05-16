#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, re, string, hashlib, sys
sys.path.append(os.path.dirname(__file__))
import json
import shutil
import random
from numpy.random import permutation
import subprocess as sp
from copy import deepcopy
from enum import Enum, auto
from math import ceil, floor
from config import *

valid_types = [
    'char', 'float', 'double', 'int', 'long',
    'int8_t', 'int16_t', 'int32_t', 'int64_t',
    'uint8_t', 'uint16_t', 'uint32_t', 'uint64_t',
]

def get_random_string(length=5):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def is_type_align(type_csmith, type_func):
    # if type_csmith and type_func are compatible
    is_align = False
    num_star_csmith = type_csmith.count('*')
    num_star_func = type_func.count('*')
    if num_star_csmith == num_star_func:
        is_align = True
    return is_align

def is_valid_type(type1):
    # if the given type is valid
    is_valid = False
    type1 = type1.strip()\
        .replace('volatile', '')\
        .replace('*', '')\
        .replace(' ', '')
    if type1 in valid_types:
        is_valid = True
    return is_valid

def retrieve_vars(expr):
    """
    Retrieve all vars in an expr
    """
    return re.findall(r'[\w|_]+', expr)

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

def get_random_int(int_type:str, get_max:bool=False, get_max_and_min:bool=False) -> int:
    match int_type:
        case 'uint8_t':
            a_min, a_max = 0, 255
        case 'int8_t':
            a_min, a_max = -128, 127
        case 'uint16_t':
            a_min, a_max = 0, 65536
        case 'int16_t':
            a_min, a_max = -32768, 32767
        case 'uint32_t':
            a_min, a_max = 0, 4294967295
        case 'int32_t':
            a_min, a_max = -2147483648, 2147483647
        case 'uint64_t':
            a_min, a_max = 0, 18446744073709551615
        case 'int64_t':
            a_min, a_max = -9223372036854775808, 9223372036854775807
        case 'int':
            a_min, a_max = -2147483648, 2147483647
        case _:
            a_min, a_max = 0, 0
    if get_max_and_min:
        return a_min, a_max
    if get_max:
        return random.choice([a_min, a_max])
    else:
        return random.randint(a_min, a_max)

def get_safe_opt(int_type:str) -> str:
    base_op = 'safe_add_func'
    match int_type:
        case 'uint8_t'|'uint16_t'|'uint32_t'|'uint64_t':
            op = f'{base_op}_{int_type}_u_u'
        case 'int8_t'|'int16_t'|'int32_t'|'int64_t':
            op = f'{base_op}_{int_type}_s_s'
        case 'int':
            op = f'{base_op}_int32_t_s_s'
        case _:
            op = ''
    return op

def get_max_right_shift_bits(int_type:str) -> int:
    match int_type:
        case 'int'|'int8_t'|'int16_t'|'int32_t'|'uint8_t'|'uint16_t'|'uint32_t':
            return 31
        case 'int64_t'|'uint64_t':
            return 63

def get_primitive_type(int_type:str) -> str:
    match int_type:
        case 'char'|'signed char'|'int8_t':
            return 'int8_t'
        case 'unsigned char'|'uint8_t':
            return 'uint8_t'
        case 'short'|'signed short'|'short int'|'signed short int'|'int16_t':
            return 'int16_t'
        case 'unsigned short'|'unsigned short int'|'uint16_t':
            return 'uint16_t'
        case 'int'|'signed int'|'int32_t':
            return 'int32_t'
        case 'unsigned int'|'uint32_t':
            return 'uint32_t'
        case 'long'|'signed long'|'int64_t':
            return 'int64_t'
        case 'unsigned long'|'uint64_t':
            return 'uint64_t'


class InstrumentType(Enum):
    FUNCTIONENTER   = auto()
    BRACESTART      = auto()
    BRACEEND        = auto()
    INSTRUMENTSITE  = auto()
    VARDECL         = auto()
    VARDECL_HEAP    = auto()
    VARREF_POINTER  = auto()
    VARREF_POINTERINDEX  = auto()
    VARREF_ARRAY    = auto()
    VARREF_MEMORY   = auto()
    VARREF_INTEGER  = auto()
    VARREF_ASSIGN   = auto()
    VARREF_FREE     = auto()
    VARREF_INIT     = auto()

class ScopeTree:
    def __init__(self, id) -> None:
        self.parent = None
        self.children = []
        self.id = id


class Synthesizer:
    def __init__(self, prob, tmp_dir=None, given_TOOL_STACKTOHEAP=None, given_ALL_TARGET_UB=None, given_CONFIG_IntegerOverflow=None) -> None:
        assert 0 < prob <= 100
        global TOOL_STACKTOHEAP, ALL_TARGET_UB, CONFIG_IntegerOverflow
        self.prob = prob
        self.tmp_dir = tmp_dir
        if self.tmp_dir is not None:
            if not os.path.exists(self.tmp_dir):
                os.makedirs(self.tmp_dir)
        self.instrument_info = []
        self.mutants = []
        if given_TOOL_STACKTOHEAP: # for tests only
            TOOL_STACKTOHEAP = given_TOOL_STACKTOHEAP
        if given_ALL_TARGET_UB: # for tests only
            ALL_TARGET_UB = given_ALL_TARGET_UB
        if given_CONFIG_IntegerOverflow:
            CONFIG_IntegerOverflow = given_CONFIG_IntegerOverflow

        if len(ALL_TARGET_UB) != 1:
            print("We only support one target_ub in ALL_TARGET_UB now.")
            exit(1)

    def instrument(self, filename):
        """
        Instrument file
        """
        # 1. add braces
        cmd = f'{TOOL_ADDBRACES} {filename} -- -w {COMPILE_ARGS}'
        ret, out = run_cmd(cmd)
        if ret != 0:
            raise InstrumentError(f"TOOL_ADDBRACES failed : {out}.")

        # 2. add necessary extra information
        if has_overlap([TargetUB.IntegerOverflow, TargetUB.DivideZero], ALL_TARGET_UB):
            cmd = f'{TOOL_ADDINTEGER} {filename} -- -w {COMPILE_ARGS}'
            ret, out = run_cmd(cmd)
            if ret != 0:
                raise InstrumentError(f"TOOL_ADDINTEGER failed : {out}.")
        if has_overlap([TargetUB.BufferOverflow, TargetUB.OutBound], ALL_TARGET_UB) > 0:
            cmd = f'{TOOL_ADDARRAYINDEX} {filename} -- -w {COMPILE_ARGS}'
            ret, out = run_cmd(cmd)
            if ret != 0:
                raise InstrumentError(f"TOOL_ADDARRAYINDEX failed : {out}.")

        # 3. instrument
        if has_overlap([TargetUB.IntegerOverflow], ALL_TARGET_UB):
            cmd = f'{TOOL_INSTRUMENTER} {filename} --mode=int -- -w {COMPILE_ARGS}'
        elif has_overlap([TargetUB.DivideZero], ALL_TARGET_UB):
            cmd = f'{TOOL_INSTRUMENTER} {filename} --mode=zero -- -w {COMPILE_ARGS}'
        elif has_overlap([TargetUB.BufferOverflow, TargetUB.OutBound], ALL_TARGET_UB) > 0:
            cmd = f'{TOOL_INSTRUMENTER} {filename} --mode=mem -- -w {COMPILE_ARGS}'
        elif has_overlap([TargetUB.NullPtrDeref, TargetUB.UseAfterFree, TargetUB.UseAfterScope, TargetUB.DoubleFree, TargetUB.MemoryLeak], ALL_TARGET_UB) > 0:
            cmd = f'{TOOL_INSTRUMENTER} {filename} --mode=ptr -- -w {COMPILE_ARGS}'
        elif has_overlap([TargetUB.UseUninit], ALL_TARGET_UB):
            cmd = f'{TOOL_INSTRUMENTER} {filename} --mode=init -- -w {COMPILE_ARGS}'

        ret, out = run_cmd(cmd)
        if ret != 0:
            raise InstrumentError(f"TOOL_INSTRUMENTER failed : {out}.")

        # stack to heap
        if has_overlap([TargetUB.BufferOverflow, TargetUB.UseAfterFree, TargetUB.UseAfterScope, TargetUB.DoubleFree, TargetUB.MemoryLeak], ALL_TARGET_UB) > 0:
            cmd = f'{TOOL_STACKTOHEAP} {filename} -- -w {COMPILE_ARGS}'
            ret, out = run_cmd(cmd)
            if ret != 0:
                raise InstrumentError(f"TOOL_STACKTOHEAP failed : {out}.")

        # 4. compile and run to get alive regions
        tmp_out = get_random_string(5) + '.out'
        cmd = f'{CC} -w {COMPILE_ARGS} {filename} -o {tmp_out}'
        ret, out = run_cmd(cmd)
        if ret != 0:
            if os.path.exists(tmp_out):
                os.remove(tmp_out)
            raise InstrumentError(f"Compile instrumented file failed : {out}.")
        cmd = f'./{tmp_out}'
        ret, out = run_cmd(cmd)
        if os.path.exists(tmp_out):
            os.remove(tmp_out)
        if ret != 0:
            raise InstrumentError(f"Run instrumented file failed : {out}.")
        self.alive_sites = [ f'ID{x}' for x in re.findall(r'INST:(\d+)', out)]
        if has_overlap([TargetUB.IntegerOverflow, TargetUB.DivideZero], ALL_TARGET_UB):
            int_values_ori = re.findall(r'INT:([\-|\d]+):([\-|\d]+):([\-|\d]+)', out)
            self.int_values = {}
            self.int_values_repeat = []
            for int_v in int_values_ori:
                if f'ID{int_v[0]}' in self.int_values:
                    if int_v[1:] != self.int_values[f'ID{int_v[0]}']:
                        self.int_values_repeat.append(f'ID{int_v[0]}')
                self.int_values[f'ID{int_v[0]}'] = int_v[1:]
        if has_overlap([TargetUB.NullPtrDeref], ALL_TARGET_UB):
            ptr_values_ori = re.findall(r'PTR:([\-|\d]+):([\-|\w]+)', out)
            self.ptr_values = {}
            self.ptr_values_repeat = []
            for ptr_v in ptr_values_ori:
                if f'ID{ptr_v[0]}' in self.ptr_values:
                    self.ptr_values_repeat.append(f'ID{ptr_v[0]}')
                self.ptr_values[f'ID{ptr_v[0]}'] = ptr_v[1]
        
        if has_overlap([TargetUB.BufferOverflow, TargetUB.OutBound], ALL_TARGET_UB) > 0:
            mem_range_ori = re.findall(r'GLOBAL:([\-|\d]+):([\-|\w]+):([\-|\d]+)', out)
            self.mem_range_global = {}
            for mem_v in mem_range_ori:
                self.mem_range_global[int(mem_v[1], 16)] = int(mem_v[2])

            mem_values_ori = re.findall(r'(LOCAL|MEM):([\-|\d]+):([\-|\w]+):([\-|\w]+)', out)
            self.mem_range_local = []
            self.mem_values = {}
            self.mem_values_repeat = [] # record all mem_values indexs that have more than 1 access with different values
            for mem_v in mem_values_ori:
                if mem_v[0] == "LOCAL":
                    self.mem_range_local.append([int(mem_v[2], 16),int(mem_v[3])])
                    continue
                access_mem = int(mem_v[2], 16)
                access_size = int(mem_v[3], 16) - access_mem
                tgt_mem_head, tgt_mem_size = access_mem, access_size
                is_global = False
                for mem_head in self.mem_range_global:
                    if mem_head <= access_mem <= mem_head + self.mem_range_global[mem_head]-access_size:
                        tgt_mem_head = mem_head
                        tgt_mem_size = self.mem_range_global[mem_head]
                        is_global = True
                        break
                is_local = False
                if not is_global:
                    for mem_i in range(len(self.mem_range_local)-1, -1, -1):
                        mem_head, mem_size = self.mem_range_local[mem_i][0], self.mem_range_local[mem_i][1]
                        if mem_head <= access_mem <= mem_head + mem_size-access_size:
                            tgt_mem_head = mem_head
                            tgt_mem_size = mem_size
                            is_local = True
                            break
                if f'ID{mem_v[1]}' in self.mem_values: # record all mem_values that have more than 1 unique access address
                    if access_mem != self.mem_values[f'ID{mem_v[1]}'][0]:
                        self.mem_values_repeat.append(f'ID{mem_v[1]}')
                self.mem_values[f'ID{mem_v[1]}'] = [access_mem, access_size, tgt_mem_head, tgt_mem_size, is_global, is_local]


        # 5. static analysis: analyze all instrumentation sites
        with open(filename, 'r') as f:
            file_content = f.read()
        instr_info = re.findall(r'\/\*I\:([^\n]+)\:\*\/', file_content)

        self.instrument_info = [] # each element of type: (InstrumentType, ID, )
        self.heap_vars = [[],[]] # all heap variables [[var_expr], [array_dim]]
        self.array_vars = [] # all array variables
        self.scope_tree = ScopeTree("Init") # brace scopes
        self.scope_vardecl = {} # scope of vardecl
        self.scope_varref_pointer = {} # scope of varref pointer
        self.scope_varref_array = {} # scope of varref array
        self.scope_varref_integer = {} # scope of varref integer
        self.scope_instr = {} # scope of intrumentsite
        self.scope_varref_init = {} # scope of var_init
        self.vardecl_id = {} # vardecl id of a var
        is_alive_site = 0
        curr_scope_node = self.scope_tree
        for ori_info in instr_info:
            info = ori_info.strip().split(':')
            info_id, info_instrument = info[0], info[1]
            if info_instrument == 'FUNCTIONENTER':
                self.instrument_info.append([InstrumentType.FUNCTIONENTER])
            elif info_instrument == 'BRACESTART':
                new_node = ScopeTree(info[0])
                new_node.parent = curr_scope_node
                curr_scope_node.children.append(new_node)
                curr_scope_node = new_node
            elif info_instrument == 'BRACEEND':
                curr_scope_node = curr_scope_node.parent
            elif info_instrument == 'VARDECLHEAP':
                self.heap_vars[0].append(info[3]) # var_expr
                self.heap_vars[1].append(info[4]) # array_dim
            elif info_instrument == 'INSERTIONSITE':
                if info_id in self.alive_sites:
                    is_alive_site = 1
                    self.instrument_info.append([InstrumentType.INSTRUMENTSITE, info_id])
                else:
                    is_alive_site = 0
                self.scope_instr[info_id] = curr_scope_node
            if not is_alive_site:
                continue
            elif info_instrument == 'VARDECL':
                self.instrument_info.append([InstrumentType.VARDECL, info_id, info[2], info[3]]) # InstrumentType, ID, type, var
                self.vardecl_id[info[3]] = info_id
                self.scope_vardecl[info_id] = curr_scope_node
                if '[' in info[2]:
                    self.array_vars.append(info[3])
            elif info_instrument == 'VARREF_POINTER':
                self.instrument_info.append([InstrumentType.VARREF_POINTER, info_id, info[2], info[3]]) # InstrumentType, ID, type, var
                self.scope_varref_pointer[info_id] = curr_scope_node
            elif info_instrument == 'VARREF_POINTERINDEX':
                self.instrument_info.append([InstrumentType.VARREF_POINTERINDEX, info_id, info[2], info[3]]) # InstrumentType, ID, type, var
                self.scope_varref_pointer[info_id] = curr_scope_node
            elif info_instrument == 'VARREF_ARRAY':
                self.instrument_info.append([InstrumentType.VARREF_ARRAY, info_id, info[2], info[3], info[4]]) # InstrumentType, ID, type, var_arr, var_idx
                self.scope_varref_array[info_id] = curr_scope_node
            elif info_instrument == 'VARREF_MEMORY':
                self.instrument_info.append([InstrumentType.VARREF_MEMORY, info_id, info[2], info[3]]) # InstrumentType, ID, type, var
                self.scope_varref_array[info_id] = curr_scope_node
            elif info_instrument == 'VARREF_INTEGER':
                self.instrument_info.append([InstrumentType.VARREF_INTEGER, info_id, info[2], info[3], info[4], info[5], info[6]]) # InstrumentType, ID, type of lhs, lhs, type of rhs, rhs
                self.scope_varref_integer[info_id] = curr_scope_node
            elif info_instrument == 'VARREF_ASSIGN':
                self.instrument_info.append([InstrumentType.VARREF_ASSIGN, info_id, info[2], info[3]]) # InstrumentType, ID, type, var
            elif info_instrument == 'VARREF_FREE':
                self.instrument_info.append([InstrumentType.VARREF_FREE, info_id, info[2], info[3]]) # InstrumentType, ID, type, var
            elif info_instrument == 'VARREF_INIT':
                self.instrument_info.append([InstrumentType.VARREF_INIT, info_id, info[2], info[3]]) # InstrumentType, ID, type, var
                self.scope_varref_init[info_id] = curr_scope_node
            else:
                continue
        return

    def is_child_scope(self, src_scope, tgt_scope):
        # if src_scope is a (grand)child of tgt_scope
        for child in tgt_scope.children:
            if child.id == src_scope.id:
                return True
            if self.is_child_scope(src_scope, child):
                return True
        return False

    def is_out_scope(self, src_vardecl, tgt_var_expr, tgt_ins_type):
        # Is src_vardecl(vardecl) a (grand)child of tgt_var_expr(varref)
        if tgt_ins_type == InstrumentType.VARREF_POINTER:
            tgt_scope = self.scope_varref_pointer[tgt_var_expr]
        elif tgt_ins_type == InstrumentType.VARREF_ARRAY:
            tgt_scope = self.scope_varref_array[tgt_var_expr]
        elif tgt_ins_type == InstrumentType.VARREF_INTEGER:
            tgt_scope = self.scope_varref_integer[tgt_var_expr]
        if self.is_child_scope(self.scope_vardecl[src_vardecl], tgt_scope):
            return True
        return False

    def insert(self, selected_info_idx):
        """
        Mutate the selected_var in one of the valid instrumentation sites
        """
        assert (
            self.instrument_info[selected_info_idx][0] == InstrumentType.VARREF_POINTER or
            self.instrument_info[selected_info_idx][0] == InstrumentType.VARREF_POINTERINDEX or
            self.instrument_info[selected_info_idx][0] == InstrumentType.VARREF_ARRAY or
            self.instrument_info[selected_info_idx][0] == InstrumentType.VARREF_MEMORY or
            self.instrument_info[selected_info_idx][0] == InstrumentType.VARREF_INTEGER or
            self.instrument_info[selected_info_idx][0] == InstrumentType.VARREF_FREE or
            self.instrument_info[selected_info_idx][0] == InstrumentType.VARREF_INIT )

        # target variable reference id
        tgt_var_id = self.instrument_info[selected_info_idx][1]
        # target variable type
        tgt_var_type = self.instrument_info[selected_info_idx][2]
        # target instrument type
        tgt_ins_type = self.instrument_info[selected_info_idx][0]
        # target variable expression
        tgt_var_expr = self.instrument_info[selected_info_idx][3]
        # target variable name
        tgt_var_name = retrieve_vars(tgt_var_expr)
        if len(tgt_var_name) == 0:
            return 1
        tgt_var_name = tgt_var_name[0]

        # available UBs for the selected_var
        AVAIL_UB = []
        if tgt_ins_type == InstrumentType.VARREF_POINTER:
            if '*' in tgt_var_type.strip():
                AVAIL_UB.append(TargetUB.NullPtrDeref)
                if '[' not in tgt_var_type:
                    # don't assign to immutable arr: {int a[1]; int *b; a=b;}
                    AVAIL_UB.append(TargetUB.UseAfterScope)
            if tgt_var_name in self.heap_vars[0]:
                AVAIL_UB.append(TargetUB.UseAfterFree)
        if tgt_ins_type ==  InstrumentType.VARREF_MEMORY:
            AVAIL_UB.append(TargetUB.BufferOverflow)
            AVAIL_UB.append(TargetUB.OutBound)
        if tgt_ins_type == InstrumentType.VARREF_INTEGER:
            AVAIL_UB.append(TargetUB.IntegerOverflow)
            AVAIL_UB.append(TargetUB.DivideZero)
        if tgt_ins_type == InstrumentType.VARREF_FREE:
            AVAIL_UB.append(TargetUB.DoubleFree)
            AVAIL_UB.append(TargetUB.MemoryLeak)
        if tgt_ins_type == InstrumentType.VARREF_INIT:
            AVAIL_UB.append(TargetUB.UseUninit)

        # candidate UBs among the given target UBs
        CAND_TARGET_UB = []
        for ub in AVAIL_UB:
            if ub in ALL_TARGET_UB:
                CAND_TARGET_UB.append(ub)
        if len(CAND_TARGET_UB) == 0:
            return 1

        # randomly select a target ub
        tgt_ub = random.choice(CAND_TARGET_UB)

        if tgt_ub == TargetUB.BufferOverflow:
            if tgt_var_id not in self.mem_values:
                return 1
            if tgt_var_id in self.mem_values_repeat: # avoid false positives if we are accessing buffers in a loop with changing addresses
                return 1
            # get accessed memory address
            # size of the point to value
            # get valid range of the accessed memory region (tgt_mem_head, tgt_mem_size)
            access_mem, access_size, tgt_mem_head, tgt_mem_size, is_global, is_local = self.mem_values[tgt_var_id]
            if access_size > 32: # for large buffers, we will exceed the redzone
                return 1
            if not is_local and not is_global: # the memory is not found
                return 1
            # calculate overflow/underflow size
            overflow_access = ceil((tgt_mem_size - (access_mem-tgt_mem_head))/float(access_size))
            underflow_access = ceil((access_mem-tgt_mem_head)/float(access_size))+1
            if not is_global:
                place_holder_new = random.choice([f"+{overflow_access}", f"-{underflow_access}"])
            else:
                place_holder_new = f"+{overflow_access}"
            # get placeholder
            place_holder = re.findall(r'(_MUT[\w]+\d+)', self.instrument_info[selected_info_idx][3])[-1]
            self.src = re.sub(re.escape(f'{place_holder})'), f'{place_holder_new}/*UBFUZZ*/)', self.src)
            return 0
        elif tgt_ub == TargetUB.OutBound:
            if retrieve_vars(tgt_var_expr)[0] not in self.array_vars:
                return 1
            if tgt_var_id not in self.mem_values:
                return 1
            # if tgt_var_id in self.mem_values_repeat: # avoid false positives if we are accessing buffers in a loop with changing addresses
                # return 1
            # get accessed memory address
            # size of the point to value
            # get valid range of the accessed memory region (tgt_mem_head, tgt_mem_size)
            access_mem, access_size, tgt_mem_head, tgt_mem_size, is_global, is_local = self.mem_values[tgt_var_id]
            # if not is_local and not is_global: # the memory is not found
                # return 1
            # calculate overflow/underflow size
            overflow_access = ceil((tgt_mem_size - (access_mem-tgt_mem_head))/float(access_size))
            underflow_access = ceil((access_mem-tgt_mem_head)/float(access_size))+1
            overbound = random.randint(overflow_access, 2**31-1)
            underboud = random.randint(underflow_access, 2**31)
            place_holder_new = random.choice([f"+{overflow_access}", f"-{underflow_access}", f"+{overbound}", f"-{underboud}"])
            # get placeholder
            place_holder = re.findall(r'(_MUT[\w]+\d+)', self.instrument_info[selected_info_idx][3])[-1]
            self.src = re.sub(re.escape(f'{place_holder})'), f'{place_holder_new}/*UBFUZZ*/)', self.src)
            return 0

        elif tgt_ub == TargetUB.UseAfterFree:
            # malloc-ed array dim
            arr_dim = int(self.heap_vars[1][self.heap_vars[0].index(tgt_var_name)])
            if tgt_var_expr.count("*")+tgt_var_expr.count("[") >= arr_dim:
                return 1
            new_stmt = f'free_{arr_dim}({tgt_var_name});//UBFUZZ'
        elif tgt_ub == TargetUB.DoubleFree:
            # malloc-ed array dim
            new_stmt = f'free_{arr_dim}({tgt_var_name});//UBFUZZ'
        elif tgt_ub == TargetUB.MemoryLeak:
            free_index = self.src.index(f'/*I:{tgt_var_id}:VARREF_FREE:')
            first_half = self.src[:free_index]
            second_half = self.src[free_index:]
            self.src = first_half + second_half.replace('free_', '//UBFUZZ //free_', 1)
            return 0
        elif tgt_ub == TargetUB.NullPtrDeref:
            if tgt_var_id in self.ptr_values_repeat: # avoid for loop
                return 1
            # select a pointer
            depth = 0 if '*' not in tgt_var_expr else random.randint(0, tgt_var_expr.count('*')-1)
            new_stmt = '*'*depth + f'{tgt_var_expr} = 0;//UBFUZZ'
        elif tgt_ub == TargetUB.IntegerOverflow:
            if tgt_var_id in self.int_values_repeat: # avoid for loop
                return 1
            # get lhs and rhs values and types
            lhs_v, rhs_v = [int(x) for x in self.int_values[tgt_var_id]]
            lhs_t, rhs_t = self.instrument_info[selected_info_idx][2], self.instrument_info[selected_info_idx][4]
            opcode = self.instrument_info[selected_info_idx][6]
            assert get_primitive_type(lhs_t) == get_primitive_type(rhs_t)
            if lhs_t[0] == 'u' and (opcode == '+' or opcode == '-' or opcode == '*'): # unsigned integer overflow is not undefined behavior
                return 1
            # get operator
            # get lhs and rhs placeholders
            lhs_p = re.findall(r'(_INTOP[L|R]\d+)', self.instrument_info[selected_info_idx][3])[-1]
            rhs_p = re.findall(r'(_INTOP[L|R]\d+)', self.instrument_info[selected_info_idx][5])[-1]
            # select target overflow value
            t_min, t_max = get_random_int(lhs_t, get_max_and_min=True)
            try:
                original_v = eval(f'({lhs_v}){opcode}({rhs_v})')
            except:
                return 1
            overflow_v = t_max + 1 if original_v >= 0 else t_min - 1
            mut_v = overflow_v - original_v
            match opcode:
                case '+':
                    place_holder_list = []
                    if t_min <= lhs_v + mut_v <= t_max:
                        place_holder_list.append(lhs_p)
                    if t_min <= rhs_v + mut_v <= t_max:
                        place_holder_list.append(rhs_p)
                    if len(place_holder_list) == 0:
                        return 1
                    place_holder = random.choice(place_holder_list)
                    place_holder_new = f'+({mut_v})'
                case '-':
                    place_holder_list = []
                    if t_min <= lhs_v + mut_v <= t_max:
                        place_holder_list.append((lhs_p, f'+({mut_v})'))
                    if t_min <= rhs_v - mut_v <= t_max:
                        place_holder_list.append((rhs_p, f'-({mut_v})'))
                    if len(place_holder_list) == 0:
                        return 1
                    place_holder, place_holder_new = random.choice(place_holder_list)
                case '*':
                    place_holder_list = []
                    if rhs_v !=0:
                        if t_min <= lhs_v + floor(mut_v / rhs_v) + 1 <= t_max and \
                        ((lhs_v + floor(mut_v / rhs_v) + 1)*rhs_v < t_min or (lhs_v + floor(mut_v / rhs_v) + 1)*rhs_v > t_max):
                            place_holder_list.append((lhs_p, f'+({floor(mut_v / rhs_v) + 1})'))
                    if lhs_v !=0:
                        if t_min <= rhs_v + floor(mut_v / lhs_v) + 1 <= t_max and \
                        ((rhs_v + floor(mut_v / lhs_v) + 1)*lhs_v < t_min or (rhs_v + floor(mut_v / lhs_v) + 1)*lhs_v > t_max):
                            place_holder_list.append((rhs_p, f'+({floor(mut_v / lhs_v) + 1})'))
                    if len(place_holder_list) == 0:
                        return 1
                    place_holder, place_holder_new = random.choice(place_holder_list)
                case '>>':
                    place_holder = rhs_p
                    place_holder_new = '+({})'.format(get_max_right_shift_bits(rhs_t)+1-rhs_v)
                case '<<':
                    place_holder = rhs_p
                    if 'u' in lhs_t or 'unsigned' in lhs_t:
                        place_holder_new = '+({})'.format(get_max_right_shift_bits(rhs_t)+1-rhs_v)
                    else:
                        shift_min, shift_max = 1, 64
                        while shift_min < shift_max-1:
                            shift_v = ceil((shift_min+shift_max)/2)
                            new_v = eval(f'({lhs_v}) << {shift_v}')
                            if t_min <= new_v <= t_max:
                                shift_min = shift_v
                            else:
                                shift_max = shift_v
                        place_holder_new = f'+({shift_max-rhs_v})'
            # # This is to replace the MACRO placeholder with a constant value
            # self.src = re.sub(re.escape(f'{place_holder})'), f'{place_holder_new}/*UBFUZZ*/)', self.src)
            # This is to replace the MACRO placeholder with a global variable
            self.src = re.sub(re.escape(f'#define {place_holder} '), f'#include <stdint.h>\n{get_primitive_type(rhs_t)} MUT_VAR = {place_holder_new}/*UBFUZZ*/;\n#define {place_holder} +(MUT_VAR) ', self.src)
            return 0

        elif tgt_ub == TargetUB.DivideZero:
            # get lhs and rhs values and types
            _, rhs_v = [int(x) for x in self.int_values[tgt_var_id]]
            _, rhs_t = self.instrument_info[selected_info_idx][2], self.instrument_info[selected_info_idx][4]
            opcode = self.instrument_info[selected_info_idx][6]
            assert opcode == '/' or opcode == '%'
            rhs_p = re.findall(r'(_INTOP[L|R]\d+)', self.instrument_info[selected_info_idx][5])[-1]
            place_holder = rhs_p
            place_holder_new = f'-({rhs_v})'
            self.src = re.sub(re.escape(f'{place_holder})'), f'{place_holder_new}/*UBFUZZ*/)', self.src)
            return 0

        elif tgt_ub == TargetUB.UseAfterScope:
            # target is a pointer
            # get all possible variable
            tgt_ptr_num = tgt_var_type.count('*') + tgt_var_type.count('[')
            tgt_type_base = retrieve_vars(tgt_var_type)[0]
            all_vars = []
            for src_idx in range(selected_info_idx, 0, -1): # search backwards
                src_instrumenttype = self.instrument_info[src_idx][0]
                if src_instrumenttype == InstrumentType.VARREF_POINTER or \
                   src_instrumenttype == InstrumentType.VARREF_ARRAY or \
                   src_instrumenttype == InstrumentType.VARREF_INTEGER or \
                   src_instrumenttype == InstrumentType.VARDECL :

                    src_type = self.instrument_info[src_idx][2]
                    src_ptr_num = src_type.count('*') + src_type.count('[')
                    src_type_base = retrieve_vars(src_type)[0]
                    src_var_expr = self.instrument_info[src_idx][3]
                    # if tgt_type_base != src_type_base: # both should have the same type base (e.g., uint32_t)
                    #     continue
                    if '*' in src_type:
                        # although pointer types are out of scope, the point-to var is not. see test4.c
                        # {int a; int *c; {int *b=&a; c=b;} *c=1;}
                        continue
                    if tgt_var_expr == src_var_expr: # is the same variable
                        continue
                    if retrieve_vars(src_var_expr)[0] not in self.vardecl_id:
                        continue # function parameters like foo(p_1, p_2)
                    if not self.is_out_scope(self.vardecl_id[retrieve_vars(src_var_expr)[0]], tgt_var_id, tgt_ins_type): # vardecl of src_var should be (grand)child of tgt_var
                        continue
                    if src_ptr_num > tgt_ptr_num: #
                        new_var = src_var_expr
                        for _ in range(src_ptr_num-tgt_ptr_num):
                            new_var = f'*({new_var})'
                        all_vars.append(new_var)
                        continue
                    if src_ptr_num == tgt_ptr_num-1:
                        new_var = src_var_expr
                        for _ in range(tgt_ptr_num-src_ptr_num):
                            new_var = f'&({new_var})'
                        all_vars.append(new_var)
                        continue
                    if src_ptr_num == tgt_ptr_num:
                        all_vars.append(src_var_expr)
                        continue
                elif src_instrumenttype == InstrumentType.FUNCTIONENTER:
                    break
                elif src_instrumenttype == InstrumentType.VARDECL and self.instrument_info[src_idx][3] == tgt_var_name:
                    break
            if len(all_vars) == 0:
                return 1
            all_vars = list(set(all_vars))
            random.shuffle(all_vars)
            out_scope_var = random.choice(all_vars)
            new_stmt = f'{tgt_var_expr} = {out_scope_var};//UBFUZZ'
        elif tgt_ub == TargetUB.UseUninit:
            new_var = 'UNINIT_' + get_random_string(5)
            new_stmt = f'{tgt_var_type} {new_var};//UBFUZZ'
            out_scope_var = tgt_var_expr

            # index of current VARREF_INIT
            init_index = self.src.index(f'/*I:{tgt_var_id}:VARREF_INIT:')
            first_half = self.src[:init_index]
            second_half = self.src[init_index:]
            to_replace_expr = f'{tgt_var_expr}'
            if second_half.find(to_replace_expr) == -1:
                return 1
            self.src = first_half + second_half.replace(to_replace_expr, new_var, 2)

        # find all valid instrumentation sites
        valid_site_list = []
        have_seen_INSTRUMENTSITE = False
        for curr_idx in range(selected_info_idx-1, 0, -1): # search backwards
            curr_instrumenttype = self.instrument_info[curr_idx][0]
            if curr_instrumenttype == InstrumentType.VARREF_ASSIGN:
                if tgt_ub == TargetUB.UseAfterScope:
                    curr_var = self.instrument_info[curr_idx][3]
                    if curr_var == tgt_var_expr:
                        # we've meet an assignment to our target expr, so we cannot proceed. see test5.c
                        break
            elif curr_instrumenttype == InstrumentType.INSTRUMENTSITE:
                have_seen_INSTRUMENTSITE = True
                if tgt_ub == TargetUB.UseAfterScope:
                    curr_instr_id = self.instrument_info[curr_idx][1]
                    curr_instr_scope = self.scope_instr[curr_instr_id]
                    src_var_scope = self.scope_vardecl[self.vardecl_id[retrieve_vars(out_scope_var)[0]]]
                    if curr_instr_scope == src_var_scope or self.is_child_scope(curr_instr_scope, src_var_scope):
                        valid_site_list.append(curr_idx)
                    else:
                        continue
                elif tgt_ub == TargetUB.UseUninit:
                    curr_instr_id = self.instrument_info[curr_idx][1]
                    curr_instr_scope = self.scope_instr[curr_instr_id]
                    src_var_scope = self.scope_varref_init[tgt_var_id]
                    if curr_instr_scope == src_var_scope:# or not self.is_child_scope(curr_instr_scope, src_var_scope):
                        valid_site_list.append(curr_idx)
                    else:
                        break
                else:
                    valid_site_list.append(curr_idx)
            elif curr_instrumenttype == InstrumentType.VARREF_POINTER or \
                curr_instrumenttype == InstrumentType.VARREF_ARRAY or \
                    curr_instrumenttype == InstrumentType.VARREF_INTEGER:
                if retrieve_vars(self.instrument_info[curr_idx][3])[0] == tgt_var_name:
                    if have_seen_INSTRUMENTSITE:
                        break
            elif curr_instrumenttype == InstrumentType.VARDECL:
                if retrieve_vars(self.instrument_info[curr_idx][3])[0] == tgt_var_name:
                    break
                if tgt_ub == TargetUB.UseAfterScope and self.instrument_info[curr_idx][3] == retrieve_vars(out_scope_var)[0]:
                    break
            elif curr_instrumenttype == InstrumentType.FUNCTIONENTER:
                break
        if len(valid_site_list) == 0:
            return 1

        if tgt_ub == TargetUB.BufferOverflow:
            #don't use instrumentsites that are inside a loop
            valid_site_list_copy = valid_site_list.copy()
            start_site_id = self.instrument_info[valid_site_list[-1]][1]
            end_site_id = self.instrument_info[valid_site_list[0]][1]
            all_executed_sites = self.alive_sites[self.alive_sites.index(start_site_id):self.alive_sites.index(end_site_id)]
            for idx in range(len(valid_site_list_copy)):
                if all_executed_sites.count(self.instrument_info[valid_site_list_copy[idx]][1]) > 1:
                    valid_site_list.remove(valid_site_list_copy[idx])
                else:
                    pass
            #rename target MUT_ARR_id to avoid cleanup
            if tgt_ins_type == InstrumentType.VARREF_ARRAY:
                self.src = re.sub(self.instrument_info[selected_info_idx][4], 'MUT_ARR', self.src)
                new_stmt = re.sub(self.instrument_info[selected_info_idx][4], 'MUT_ARR', new_stmt)
            if tgt_ins_type == InstrumentType.VARREF_POINTERINDEX:
                self.src = re.sub(self.instrument_info[selected_info_idx][3], 'MUT_PTR', self.src)
                new_stmt = re.sub(self.instrument_info[selected_info_idx][3], 'MUT_PTR', new_stmt)



        # select an instrumentation site
        random.shuffle(valid_site_list)
        selected_site = random.choice(valid_site_list)
        # insert
        self.src = self.src.replace(
            f'/*I:{self.instrument_info[selected_site][1]}:INSERTIONSITE:*/',
            new_stmt + ' /*I:')
        return 0

    def clean_instrument(self):
        """
        Remove instrumentations
        """
        self.src = re.sub(r'\/\*I:.*', '', self.src) # remove all instrumented comments
        self.src = re.sub(r'int MUT_ARR_\d+ = 0;', '', self.src) # remove all MUT_ARR_id
        self.src = re.sub(r'MUT_ARR_\d+\+', '', self.src) # remove all MUT_ARR_id
        self.src = re.sub(r'int MUT_PTR_\d+ = 0;', '', self.src) # remove all MUT_ARR_id
        self.src = re.sub(r'\+MUT_PTR_\d+', '', self.src) # remove all MUT_ARR_id

    def synthesizer(self, filename, mutated_num=-1):
        """
        Synthesize a source file by replacing variables/constants with function calls.
        """
        random.seed()

        assert '.c' in filename
        realname = re.findall(r'([\w|_]+\.c)', filename)[0]
        # 1. backup file
        if self.tmp_dir is None:
            file_instrument = filename.replace(realname, 'instrument_'+realname)
        else:
            file_instrument = os.path.join(self.tmp_dir, 'instrument_'+realname)
        shutil.copyfile(filename, file_instrument)
        # 2. instrumentation
        self.instrument(file_instrument)
        with open(file_instrument, "r") as f:
            self.src_ori = f.read()
        # 3. sythesis
        all_mutated_file = []
        all_mutated_file_md5 = []
        mutated_n = 0
        var_idx_list = []
        for i in range(len(self.instrument_info)):
            info_type = self.instrument_info[i][0]
            if info_type in [InstrumentType.VARREF_POINTER, InstrumentType.VARREF_POINTERINDEX, InstrumentType.VARREF_ARRAY, InstrumentType.VARREF_MEMORY, InstrumentType.VARREF_INTEGER, InstrumentType.VARREF_FREE, InstrumentType.VARREF_INIT]:
                var_idx_list.append(i)
        for selected_var_idx in var_idx_list:
            mutated_filename = f'mutated_{mutated_n}_{realname}'
            if self.tmp_dir is None:
                mutated_file = filename.replace(realname, mutated_filename)
            else:
                mutated_file = os.path.join(self.tmp_dir, mutated_filename)
            shutil.copyfile(file_instrument, mutated_file)
            self.src = deepcopy(self.src_ori)
            insert_succ = False
            # insert function to selected site
            ret = self.insert(selected_var_idx)
            if ret == 0:
                insert_succ = True
            if not insert_succ:
                os.remove(mutated_file)
                continue
            self.clean_instrument()
            if has_overlap([TargetUB.UseUninit], ALL_TARGET_UB):
                if self.src.count('UNINIT') != 2:# a workaround when only uninit decl is inserted.
                    os.remove(mutated_file)
                    continue
            curr_md5 = hashlib.md5(self.src.encode("utf-8")).hexdigest()
            if curr_md5 in all_mutated_file_md5:
                os.remove(mutated_file)
                continue
            all_mutated_file_md5.append(curr_md5)
            with open(mutated_file, "w") as f:
                f.write(self.src)
            all_mutated_file.append(mutated_file)
            mutated_n += 1
        os.remove(file_instrument)
        return all_mutated_file


class InstrumentError(Exception):
    pass

# UBGen

🌟UBGen🌟 is an automated UB program genertor for C. Given a valid C program, UBGen can mutate it to generate programs containing undefined behaviors. For each of the generated UB program, it only contains one kind of undefined behavior at one program location.

UBGen is designed in our research paper **"UBfuzz: Finding Bugs in Sanitizer Implementations" (ASPLOS 2024)**, where UBGen is the program generator for UBfuzz. For the full evaluation of UBfuzz, please find the artifact as stated in the paper.


## Support Undefined Behavior

<div align="center">

| UB | buffer-overflow | division-by-zero | null-pointer-dereference | use-after-free | use-after-scope | double-free | integer-overflow |
| ------------ | ------------------------------------ | ----------------------------------------------- | ---------------------------------------------- | ----------------------------------------- | ------------------------------------- | ----------------------------------------------------- | ------------ |
| Status         | ✅                                    | ✅                                               |   ✅                                            | ✅ | ✅ |     ✅                                                  | ✅ |


✅: Supported; 🔨: Coming soon;

</div>

## Quick Start

**Compile dynamic analyzer for analyzing C source code:**
Please make sure that `LLVM>=18` is installed.
```shell
./build.sh
```

**Install necessary Python packages:**
```shell
pip install -r requirements.txt
```

## Usage

The generator is `ubgen.py`. Each time you run it, `ubgen.py` generates more than one UB programs based on one Csmith-generated program.

Note that, *for the first run* of `ubgen.py`, it will download and install `Csmith` under the same directory.

For example, the following code will generate programs containing buffer-overflow and all the generated UB programs are saved into `./mutants`:

```shell
./ubgen.py --ub buffer-overflow --out ./mutants
```

Alternatively, you can use an integer index to specify the UB. For example, the above command is equivalent to 
```shell
./ubgen.py --ub 0 --out ./mutants
```

By default, all programs are mutated from csmith. If you want to specify your own seed C file, try `--seed` as follows
```shell
./ubgen.py --ub 0 --out ./mutants --seed seed.c
```
The seed file `seed.c` is a valid C file without undefined behaviors. Note that, UBGen will not insert UB in the `main()` function. Therefore, please make sure
that there are other functions in your seed file.

You can use `./ubgen --help` to find detailed help information.

Suppose there are generated programs under `./mutants/` and one of the file is `./mutants/mutated_0_tmp6a83k7sn.c`. All generated files of the same prefix are from the same seed Csmith program.
For example, `./mutants/mutated_1_tmp6a83k7sn.c` would be another UB program from the same seed. To compile the generated UB program, you need to include the path the Csmith header files `./csmith_install/include/csmith-2.3.0`:
```shell
gcc -I./csmith_install/include/csmith-2.3.0 -fsanitize=address -g -w ./mutants/mutated_0_tmp6a83k7sn.c -o test.out
```
Executing `./test.out` would normally cause sanitizer warning as such
```shell
=================================================================
==468815==ERROR: AddressSanitizer: global-buffer-overflow on address 0x55595b49d950 at pc 0x55595b47a4aa bp 0x7ffd77bbd580 sp 0x7ffd77bbd570
READ of size 16 at 0x55595b49d950 thread T0
    #0 0x55595b47a4a9 in func_1 /UBGen/mutants/mutated_0_tmp6a83k7sn.c:698
    #1 0x55595b495534 in main /UBGen/mutants/mutated_0_tmp6a83k7sn.c:3502
    #2 0x7fa853629d8f in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58
    #3 0x7fa853629e3f in __libc_start_main_impl ../csu/libc-start.c:392
    #4 0x55595b470424 in _start (/UBGen/mutants/a.out+0x9424)

0x55595b49d950 is located 0 bytes to the right of global variable 'g_1576' defined in 'mutated_0_tmp6a83k7sn.c:261:18' (0x55595b49d940) of size 16
0x55595b49d950 is located 48 bytes to the left of global variable 'g_1589' defined in 'mutated_0_tmp6a83k7sn.c:262:18' (0x55595b49d980) of size 16
SUMMARY: AddressSanitizer: global-buffer-overflow /UBGen/mutants/mutated_0_tmp6a83k7sn.c:698 in func_1
Shadow bytes around the buggy address:
  0x0aabab68bad0: 02 f9 f9 f9 f9 f9 f9 f9 00 f9 f9 f9 f9 f9 f9 f9
  0x0aabab68bae0: 01 f9 f9 f9 f9 f9 f9 f9 00 00 f9 f9 f9 f9 f9 f9
  0x0aabab68baf0: 01 f9 f9 f9 f9 f9 f9 f9 01 f9 f9 f9 f9 f9 f9 f9
  0x0aabab68bb00: 00 f9 f9 f9 f9 f9 f9 f9 01 f9 f9 f9 f9 f9 f9 f9
  0x0aabab68bb10: 04 f9 f9 f9 f9 f9 f9 f9 04 f9 f9 f9 f9 f9 f9 f9
=>0x0aabab68bb20: 04 f9 f9 f9 f9 f9 f9 f9 00 00[f9]f9 f9 f9 f9 f9
  0x0aabab68bb30: 00 00 f9 f9 f9 f9 f9 f9 00 00 00 f9 f9 f9 f9 f9
  0x0aabab68bb40: 01 f9 f9 f9 f9 f9 f9 f9 00 00 04 f9 f9 f9 f9 f9
  0x0aabab68bb50: 01 f9 f9 f9 f9 f9 f9 f9 00 00 f9 f9 f9 f9 f9 f9
  0x0aabab68bb60: 00 f9 f9 f9 f9 f9 f9 f9 04 f9 f9 f9 f9 f9 f9 f9
  0x0aabab68bb70: 00 f9 f9 f9 f9 f9 f9 f9 02 f9 f9 f9 f9 f9 f9 f9
Shadow byte legend (one shadow byte represents 8 application bytes):
  Addressable:           00
  Partially addressable: 01 02 03 04 05 06 07 
  Heap left redzone:       fa
  Freed heap region:       fd
  Stack left redzone:      f1
  Stack mid redzone:       f2
  Stack right redzone:     f3
  Stack after return:      f5
  Stack use after scope:   f8
  Global redzone:          f9
  Global init order:       f6
  Poisoned by user:        f7
  Container overflow:      fc
  Array cookie:            ac
  Intra object redzone:    bb
  ASan internal:           fe
  Left alloca redzone:     ca
  Right alloca redzone:    cb
  Shadow gap:              cc
==468815==ABORTING
```

<p align="center">
    <a href="https://shao-hua-li.github.io/files/2024_ASPLOS_UBFUZZ.pdf"><img src="https://img.shields.io/badge/Paper-ASPLOS'24-a55fed.svg"></a>
</p>

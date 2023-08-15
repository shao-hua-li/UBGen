# UndefinedSmith

🌟UndefinedSmith🌟 is an automated UB program genertor for C. Given a valid C program, UndefinedSmith can mutate it to generate programs containing undefined behaviors. For each of the generated UB program, it only contains one kind of undefined behavior at one program location.

## Support Undefined Behavior

<div align="center">

| UB | buffer-overflow | division-by-zero | null-pointer-dereference | use-after-free | use-after-scope | double-free | integer-overflow |
| ------------ | ------------------------------------ | ----------------------------------------------- | ---------------------------------------------- | ----------------------------------------- | ------------------------------------- | ----------------------------------------------------- | ------------ |
| Status         | ✅                                    | ✅                                               |   ✅                                            | ✅ | ✅ |     ✅                                                  | ✅ |


✅: Supported; 🔨: Coming soon;

</div>

## Quick Start

**Compile dynamic analyzer for analyzing C source code:**
```shell
./build.sh
```

**Install necessary Python packages:**
```shell
pip install -r requirements.txt
```

## Usage

The generator is `ubsmith.py`. Each time you run it, `ubsmith.py` generates more than one UB programs based on one Csmith-generated program.

For example, the following code will generate programs containing buffer-overflow and all the generated UB programs are saved into `./mutants`:

```shell
./ubsmith.py --ub buffer-overflow --out ./mutants
```

You can use `./ubsmith --help` to find detailed help information.

Note that, *for the first run* of `ubsmith.py`, it will download and install `Csmith` under the same directory.

<p align="center">
    <a href="https://dl.acm.org/doi/10.1145/3575693.3575707"><img src="https://img.shields.io/badge/Paper-ASPLOS'24-a55fed.svg"></a>
</p>
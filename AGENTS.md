# AGENTS.md

## Cursor Cloud specific instructions

This is a C++ extension library for the 10X Platform. It produces two Python extension modules via pybind11:
- **py10x_kernel** (`core_10x/`) — core kernel (traitables, traits, nodes, caching, serialization)
- **py10x_infra** (`infra_10x/`) — infrastructure layer (MongoDB helpers)

### Building

Build both extensions from the workspace root using CMake with g++ (clang's default linker config lacks `-lstdc++`):

```bash
source /workspace/.venv/bin/activate
cmake -S /workspace -B /workspace/cmake-build-debug -DCMAKE_BUILD_TYPE=Debug -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++
cmake --build /workspace/cmake-build-debug -j$(nproc)
```

The built `.so` files land in:
- `core_10x/cmake-build-debug/py10x_kernel.cpython-312-x86_64-linux-gnu.so`
- `infra_10x/cmake-build-debug/py10x_infra.cpython-312-x86_64-linux-gnu.so`

### Running tests

Tests require the locally-built `.so` files on `PYTHONPATH` and depend on `py10x-core` from PyPI:

```bash
source /workspace/.venv/bin/activate
PYTHONPATH=/workspace/core_10x/cmake-build-debug:/workspace/infra_10x/cmake-build-debug python core_10x/tests/test.py
```

The infra unit test (`test_prepare_filter_and_pipeline`) does not need MongoDB:
```bash
PYTHONPATH=/workspace/core_10x/cmake-build-debug:/workspace/infra_10x/cmake-build-debug python -c "from infra_10x.tests.test import test_prepare_filter_and_pipeline; test_prepare_filter_and_pipeline(); print('PASS')"
```

The infra integration test (`test_load`) requires MongoDB on `localhost:27017`.

### Key gotchas

- Must use `gcc`/`g++` as compiler, not the default `clang`/`c++` — the system clang linker config cannot find `-lstdc++`.
- `python3-dev` must be installed for CMake's `find_package(Python3 ... Development.Module)`.
- The venv is at `/workspace/.venv` — always activate it before running Python or pip commands.
- Some tests may fail due to version mismatch between locally-built extensions (dev branch) and the released `py10x-core` from PyPI. This is expected during active development.
- The top-level `tests/test.py` and any code using `Person` outside a `TsUnion()` context requires `EnvVars.traitable_store_uri = ''` to disable store lookups.
- pybind11 and other C++ deps (backward-cpp, pybind11-stubgen) are fetched automatically by CMake via `FetchContent`.

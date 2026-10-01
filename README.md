# VEC Profile

A small process-tree profiler for planning local VEC scoring runs.

```bash
pip install -e .

vec-profile --repeat 3 --json profile.json -- \
  veckit --task T2 --setting heart \
  --input prediction.h5ad \
  --target pseudo_target.h5ad \
  --reference preceding.h5ad
```

For each run it records:

- return code;
- wall-clock seconds;
- peak RSS across the process and all visible children;
- bounded stdout/stderr tails.

The summary reports median/min/max runtime and peak memory.

## Why

Task, gene width, cell count and metric choice can change local scoring cost sharply. Profiling one representative command before launching a large checkpoint sweep is cheaper than discovering a RAM limit halfway through it.

VEC Profile works with any trusted local command and reads no Challenge data itself.

## Safety / implementation

The child command is executed directly as an argv list, **not through a shell**. Stdout/stderr are spooled to temporary files rather than unread pipes, avoiding pipe-buffer deadlocks during long/noisy runs.

## Development

```bash
pip install -e '.[dev]'
pytest
ruff check src tests
```

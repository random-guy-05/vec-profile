# Community Contribution submission text

## Title
VEC Profile — wall-time and peak-memory profiler for local scoring workflows

## Description
VEC Profile measures wall time and peak resident memory across an entire process tree for any local scoring command, including veckit. It repeats the command, stores bounded stdout/stderr tails, and emits machine-readable per-run data plus median/min/max timing and peak-memory summaries. The implementation executes argv directly rather than through a shell and spools output to files to avoid deadlocks from noisy child processes. This gives teams a reproducible way to budget RAM and runtime before launching large checkpoint or candidate sweeps.

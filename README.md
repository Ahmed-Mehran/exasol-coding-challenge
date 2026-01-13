# Exasol Coding Challenge

## Problem Statement
This project tests a proof-of-work–style hashing process by generating random suffixes and checking how many attempts are needed to produce a SHA-1 hash with a given difficulty. It helps measure how hash generation speed changes with different parameters.

## Approach
The way I have made commits onto this repository shows the code from Brute to Optimised solution. I have the first commit labelled as code_stage_1 which depicts the most brute solution, then code_stage_2 which depicts an optimised version of code_stage_1 solution and so on upto code_stage_5 and then the last commit
i.e. Final_stage which is the solution submitted on Exasol server. Each commit is an optimised version of previous commit. I will briefly explain the optimisation steps of each commit:

- Commit 1(code_stage_1): This stage is a simple single-core brute-force approach where random suffixes are generated and hashed until one meets the required difficulty. It establishes a working baseline, confirms correctness for different lengths and difficulty levels, and measures performance (about 4 lakh hashes
per second) to compare with later optimisations.

- Commit 2(code_stage_2):  In this stage, the same hashing logic was moved from a single core to multiple CPU cores using multiprocessing so that many hashes could be tried in parallel. Each process independently generates suffixes and checks hashes, and all processes stop once any one finds a valid result. Although
this approach is conceptually better than the single-core version because it uses all available cores, in practice the performance dropped sharply (from ~4 lakh to ~13k hashes/sec) due to process creation, coordination, and communication overhead, showing that naive multicore usage can actually make things slower.

- Commit 3(code_stage_3): In this stage, the code still uses multiple CPU cores, but instead of checking shared state after every hash, each process works in large batches of attempts before stopping. This reduces coordination overhead between processes and makes better use of the CPU compared to the previous naïve
multicore version. As a result, this approach is faster and more efficient than the earlier multicore attempt, while keeping the same hashing logic. The Hash generated per second speed increased back to 2-3 lakh Hash/Sec/Core

- Commit 4(code_stage_4):  In this stage, the code still uses multi-core batching, but small optimisations were applied by moving variables into the worker function and generating the random suffix directly inside the loop instead of using a separate function. This slightly cleans up the code and reduces minor overhead,
but as observed, it does not significantly improve speed, showing that the main bottleneck was elsewhere and not in variable scope or function calls.

- Commit 5(code_stage_5): In this stage, the code replaces random string generation with a sequential, deterministic way of generating suffixes, so each core checks unique strings with no duplication. This removes the expensive random generation logic and evenly divides the search space across cores, which leads to a major performance improvement. This turned out to be the best optimization, increasing speed by about 3× per core, from roughly 2 lakh hashes/sec/core to 7–8 lakh hashes/sec/core.

## Language
Python



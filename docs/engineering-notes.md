## Keeping long-running corpus search outside a web request

Local Text Search uses Flask for the user and administration experience while background jobs scan memory-mapped files. SQLite stores job metadata, batched result files hold matches, and the interface polls progress before showing paginated results or a download. Result ownership is checked at the application boundary.

Worker behavior depends on the platform. The documented Windows path uses threading, and the optional Cython matcher is a separate build path. One configuration source now controls corpus, database, result and session locations, so a configurable corpus no longer conflicts with a hard-coded search-engine default.

## A result limit must be shared across workers

Giving each file worker its own limit can return more results than a user requested. The release uses a shared result budget and checks matching across long lines, mixed bytes and multiple files. Six regression/access tests cover those cases and cross-user boundaries; interrupted jobs and acceleration equivalence remain further verification tasks.

The benchmark uses 800,000 generated lines and documents bytes, matches, Windows hardware, Python version and three measured times. OS caches were not flushed and Cython was not enabled. These details make the measurement reproducible without presenting an unmeasured speedup or a claim about terabyte-scale production data.

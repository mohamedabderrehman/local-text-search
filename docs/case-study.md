# Local corpus search with background jobs

## From the problem to the implementation

Search local text files asynchronously and let users inspect progress, paginate matches and download output.

Authenticated user creates a search → worker scans configured synthetic corpus → job progress and output file are updated → owner browses/downloads results → administrator reviews usage.

## Decisions and tradeoffs

Corpus, database and output directories resolve through one module instead of the old machine-specific Downloads path. Authentication and web handlers must use the same database.

mmap avoids loading each entire file into a Python string. Case-insensitive matching currently lowers byte strings; this is not general Unicode case folding.

Windows uses the threaded worker path; other platforms retain multiprocessing-related code. Describe measured behavior on the tested OS.

Optional Telegram and acceleration packages are split from the minimal Flask install. Enabling one integration should be deliberate.

Session secrets can persist through an environment value; generating a new key at restart invalidates existing sessions.

## What the publication preparation established

All six Python regression/access tests passed: long lines and AND matching, zero/mixed-byte cases, a shared result budget across files, job ownership, unauthenticated search, and a 1,000-line matching regression. A measured Windows Python-only benchmark found exactly 800 matches in 800,000 generated lines (36,353,960 bytes); three runs took 10.2452, 10.9746 and 10.5983 seconds. OS caches were not flushed.

## Deployment experience and evidence limits

Local corpus-processing and administration application. Public demos use generated text only.

Cython equivalence, Linux worker behavior and interrupted-job recovery remain unverified. Included benchmark is Python-only on the documented Windows machine, not a speedup comparison. Optional Telegram ingestion is disabled for demos.

## Next steps

Complete the uncovered checks above, record the results, and update the demonstration. Retain the existing architecture and add reproducible synthetic cases before claiming performance improvements or another provider integration.

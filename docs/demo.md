# Synthetic demonstration

Authenticated user creates a search → worker scans configured synthetic corpus → job progress and output file are updated → owner browses/downloads results → administrator reviews usage.

## Walkthrough

1. Bootstrap a synthetic corpus and administrator.
2. Search for demo, watch progress, paginate and download matches.
3. Create another user and reject access to the first user’s job.
4. Compare Python/accelerated results when the native module is available; record encoding and limit behavior.

## Acceptance checklist

- [ ] Python syntax and Flask owner/role checks
- [ ] Search results, zero matches and result files
- [ ] Mixed encoding/long-line/limit behavior
- [ ] Acceleration equivalence only when compiler/module available

## Evidence discipline

Screenshots must come from the running application with synthetic records. Record the component, viewport and configuration. A storyboard is not a recorded walkthrough. Benchmark only generated data and include hardware, input size, configuration, elapsed time and cache conditions.

No unsupported speedup or terabyte-scale claim. Native acceleration needs a compiler. Interrupted-job recovery and non-Windows behavior require their own checks.

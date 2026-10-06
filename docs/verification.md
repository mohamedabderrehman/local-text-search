# Current release verification

Historical status: Local corpus-processing and administration application. Public demos use generated text only.

Current acceptance checks are in progress. No CI badge or passing integration claim is made yet.

## Checks required

- [ ] Python syntax and Flask owner/role checks
- [ ] Search results, zero matches and result files
- [ ] Mixed encoding/long-line/limit behavior
- [ ] Acceleration equivalence only when compiler/module available

## External dependencies and limits

No unsupported speedup or terabyte-scale claim. Native acceleration needs a compiler. Interrupted-job recovery and non-Windows behavior require their own checks.

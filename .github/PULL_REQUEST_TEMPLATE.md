## Summary

Describe the change and why it is needed.

## Checks

- [ ] `python3 scripts/validate_repo.py`
- [ ] `python3 scripts/sync_core.py --check`
- [ ] `python3 scripts/check_no_silent_telemetry.py`
- [ ] `python3 scripts/evaluate_examples.py`
- [ ] `python3 scripts/evaluate_behavior.py`
- [ ] `python3 -m unittest discover -s tests`

## Privacy

- [ ] I did not commit real voice profiles, private exports, credentials, or raw
      user-authored corpora.
- [ ] New source collection behavior is explicit, scoped, and consent-gated.
- [ ] Any new network or telemetry behavior is documented and opt-in.

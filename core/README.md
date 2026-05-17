# Core

`core/` is the canonical source for shared voice-layer behavior and profile
contracts.

The packaged skills under `packages/*/skills/` keep their own frontmatter so
each agent package can use native metadata without forking the behavior model.

Edit the shared skill bodies here:

- `core/skills/write-in-my-voice.md`
- `core/skills/calibrate-my-voice.md`

Edit shared profile files here:

- `core/references/profile-contract.md`
- `core/profile/voice-profile.template.md`
- `core/profile/schema.json`

Then sync packaged copies:

```sh
python3 scripts/sync_core.py --write
python3 scripts/sync_core.py --check
```

`python3 scripts/validate_repo.py` also checks that packaged core files match
core.

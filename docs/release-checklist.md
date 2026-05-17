# Release checklist

- Run `python3 scripts/validate_repo.py`.
- Run `python3 scripts/sync_core.py --check`.
- Run `python3 scripts/check_no_silent_telemetry.py`.
- Run `python3 scripts/validate_profile.py tests/fixtures/profiles/valid-profile.md`.
- Run `python3 scripts/evaluate_examples.py`.
- Run `python3 scripts/evaluate_behavior.py`.
- Run `python3 scripts/evaluate_behavior.py --outputs-dir tests/fixtures/behavior`.
- Run `python3 scripts/validate_release_archive.py`.
- Complete [RC-0 validation](rc0-validation.md), including fresh Claude Code
  and Codex write tests, a fresh calibration test, and captured-output
  validation with `python3 scripts/evaluate_behavior.py --outputs <path>`.
- Review [RC-0 results](rc0-results.md) and keep the captured Claude Code and
  Codex fixtures passing.
- Run `python3 -m unittest discover -s tests`.
- Run `git diff --check`.
- Run `claude plugin validate .`.
- Run `claude plugin validate packages/claude-code`.
- Install into a clean Claude Code skills directory and invoke `/write-in-my-voice`.
- Install into a clean Codex user skills directory and invoke `$write-in-my-voice`.
- Review `docs/support-matrix.md` and remove any unsupported platform claims.
- Review `docs/implementation-roadmap.md` for phase changes before publishing.
- Verify `calibrate-my-voice` does not implicitly trigger for normal rewrite prompts.
- Verify `voice-profile.md` is created outside the repo.
- Verify `./voice-layer --version` prints the release version.
- Verify `./voice-layer doctor --agent both` clearly labels itself as the voice-layer doctor.
- Verify `./voice-layer uninstall --agent both` preserves `~/.config/voice-layer/voice-profile.md`.
- Verify `./voice-layer purge --dry-run --agent both` prints destructive profile cleanup without deleting files.
- Verify newly created `~/.config/voice-layer/voice-profile.md` uses owner-only permissions.
- Verify local Homebrew packaging with the git-archive based tap flow in
  `packaging/homebrew/README.md`, including `brew test voice-layer` and
  `brew uninstall voice-layer`.
- Verify the public Homebrew tap formula is copied from
  `packaging/homebrew/voice-layer.public.rb` and uses the SHA of the exact
  uploaded release archive.
- Check `git status` for accidental private samples.
- Check staged files before the first public push; do not use blind `git add .`.
- Verify `scripts/validate_release_archive.py` rejects local settings, session
  exports, raw behavior runs, bytecode, videos, local paths, and private labels.
- Review `PRIVACY.md` for any new source adapter behavior.
- Review README first screen: tagline, local-first privacy claim, install path, and demo link are visible without scrolling too far.
- Verify README badges are useful and not noisy: license, supported agents,
  local-first/no-telemetry, and runtime requirements. Add live CI and release
  badges after the public GitHub URL and first release tag exist.
- Generate and select final brand assets using
  [visual-identity.md](visual-identity.md): logo, README hero, social preview,
  and demo thumbnail.
- Verify `assets/demo/voice-layer-demo.gif` is under one minute, small enough for
  the README, and based only on synthetic data.
- Verify GitHub topics cover search intent: `agent-skills`, `claude-code`, `codex`, `ai-agents`, `developer-tools`, `writing-tools`, `local-first`, `privacy`.
- Verify demo assets use only synthetic profiles and show Slack, PR, and RFC/doc value in under one minute.
- Prepare launch copy for GitHub, Hacker News, Reddit, LinkedIn/X, and relevant Claude/Codex communities without overstating support claims.

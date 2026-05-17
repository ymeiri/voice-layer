# Security

Report security or privacy issues privately to the maintainer before opening a
public issue.

For the public GitHub repo, use GitHub private vulnerability reporting when it is
enabled. Until then, contact the maintainer privately and do not include private
samples in public issues.

High-risk areas:

- accidental retention of raw private messages,
- source collectors that gather non-user-authored text,
- installer overwrite behavior,
- calibration prompts that encourage broad workspace scraping.
- release archives that accidentally include local session exports, profiles, or
  workspace settings.

The installer refuses to replace existing skill directories unless `--force` is passed.

The release archive validator must pass before publishing:

```sh
python3 scripts/validate_release_archive.py
```

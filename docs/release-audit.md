# Release Audit

Date: 2026-05-17

## Identity

- Public repo target: `https://github.com/ymeiri/voice-layer`
- Homebrew tap target: `https://github.com/ymeiri/homebrew-voice-layer`
- Public maintainer name: Yuval Meiri
- License: MIT

## Name Collision Check

Commands run before release prep:

```sh
npm view voice-layer name version description
python3 -m pip index versions voice-layer
gh repo view ymeiri/voice-layer --json name,owner,visibility,url
gh repo view ymeiri/homebrew-voice-layer --json name,owner,visibility,url
brew search --formula /^voice-layer$/
```

Those commands returned no existing public package, formula, or repo result in
this environment. This is a practical check, not a trademark opinion.

## Release Artifact Rule

Release archives must be created from a committed git tree:

```sh
python3 scripts/validate_release_archive.py --output packaging/homebrew/dist/voice-layer-0.1.0.tar
gzip -n -f packaging/homebrew/dist/voice-layer-0.1.0.tar
shasum -a 256 packaging/homebrew/dist/voice-layer-0.1.0.tar.gz
```

Do not create release archives with `tar` over the working tree.

## Provenance Check

- `blader/humanizer` was checked and uses the MIT license, but no code or text is
  vendored from it.
- Wikipedia text is CC BY-SA. To avoid share-alike ambiguity, this repo does not
  reuse or closely paraphrase Wikipedia text in the AI writing tell taxonomy.
- Google Terms were checked for Gemini/Nano Banana exploration. Google's public
  Terms say Google does not claim ownership over original content generated in
  services that allow users to generate content, while use remains subject to
  Google's terms and policies.
- `NOTICE` intentionally avoids claiming dependency on those sources.

## Public Publishing Gates

- `NOTICE` reviewed.
- `assets/brand/prompts.md` updated with asset provenance.
- `scripts/validate_release_archive.py` passes on the release tag.
- Homebrew formula SHA is computed from the exact uploaded release tarball.
- Plugin support claims match `docs/support-matrix.md`.
- Demo GIF uses synthetic data and has no visible private labels.

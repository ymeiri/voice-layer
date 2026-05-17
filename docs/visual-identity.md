# Visual Identity

`voice-layer` should look like a precise developer tool, not a generic AI
writing product. The visual system needs to communicate:

- personal voice without using a face, celebrity, avatar, or mimicry metaphor
- local control and privacy
- portability across agents
- adaptation without losing the user's written style

## Brand Idea

Core metaphor: generic AI text passing through a local rewrite/profile layer and
coming out in the user's written voice.

Use visual language built around text diffs, rewrite patches, profile files,
document lines, edit cursors, and layered context panes. The mark should feel
technical and human, but not cute, corporate-generic, mystical, or audio-related.

Avoid:

- robots, brains, sparkles, magic wands, masks, microphones, fingerprints, or
  celebrity/persona imagery
- waveforms, sound waves, equalizers, ECG/pulse lines, audio meters, or anything
  that implies speech audio, music, health telemetry, voice cloning, or TTS
- heavy gradients, bokeh, glowing orbs, or generic SaaS mesh backgrounds
- marks that depend on the letters `V` or `L` unless the shape also works as an
  abstract product symbol
- visual claims of a hosted service, analytics platform, or enterprise suite

## Palette

Use a restrained developer-tool palette with one recognizable accent.

| Role | Hex | Usage |
| --- | --- | --- |
| Ink | `#18212F` | Primary text and dark marks |
| Paper | `#FAFAF7` | Light backgrounds |
| Line | `#CBD5E1` | Dividers and low-emphasis structure |
| Written-voice teal | `#14B8A6` | Primary brand accent and current plugin brand color |
| Rewrite green | `#10B981` | Rewritten/added text states |
| Warm coral | `#F9735B` | Warnings, contrast, selective emphasis |

The current package icon uses `#14B8A6`. If the selected logo changes the main
accent, update `agents/openai.yaml` in both package roots and rerun validation.

## Logo Direction

Generate several options, but bias toward this concept:

> A generic AI text block passing through a local `voice-profile.md` layer and
> emerging as a cleaner, more personal text block.

The selected logo direction uses a striped abstract mark inspired by written
text lines moving through a rewrite layer. Gray lines represent generic input;
teal/green lines represent transformed written output. Keep this mark free of
audio, security, and biometric metaphors.

The logo must work at:

- 16 px favicon scale
- 64 px agent/plugin icon scale
- 256 px README/social-card scale
- monochrome and dark-mode variants

The mark should not rely on tiny text. If Nano Banana produces raster output,
use it for exploration and then redraw the selected mark as a clean SVG before
shipping it in package metadata.

## Nano Banana Prompt Pack

Use these prompts as starting points. Generate at least 8 candidates for each
logo direction before selecting.

### Logo Exploration

```text
Create a logo mark for an open-source developer tool named voice-layer.

Concept: generic AI-generated text passing through a local rewrite/profile
layer and coming out in the user's written style. The mark should combine
document lines, a small patch/diff transformation, and one local profile layer.
It must feel precise, local-first, trustworthy, and useful for AI agents.

Style: modern developer tool, clean vector-like geometry, high contrast,
minimal detail, no text inside the mark, no mascot, no robot, no brain, no
sparkles, no microphone, no waveform, no sound wave, no face, no
celebrity/persona reference.

Palette: ink #18212F, paper #FAFAF7, written-voice teal #14B8A6, optional
rewrite green #10B981 accent. Flat colors, no bokeh, no glossy 3D, no heavy
gradient.

Output: centered logo mark on transparent or plain paper background, readable
at 16 px, suitable to redraw as SVG.
```

### GitHub Social Preview

```text
Create a GitHub social preview image for voice-layer, an open-source local-first
voice profile for AI agents.

Message: Bring your voice to any agent. Adapt to any audience without losing
yourself.

Visual: a clean developer-tool composition showing generic AI text transformed
through a local `voice-profile.md` layer into PR, Slack, email, and docs-shaped
outputs. No real app logos. Use abstract interface tiles only.

Style: precise, editorial, open-source, technical, high contrast. Avoid generic
AI gradients, glowing orbs, robots, faces, or stock-photo energy.

Palette: paper #FAFAF7, ink #18212F, written-voice teal #14B8A6, rewrite green
#10B981, small warm coral #F9735B accents.

Output: 1280x640, strong thumbnail readability, leave safe margins for GitHub
cropping.
```

### README Hero Diagram

```text
Create a clear technical hero diagram for the voice-layer README.

Show this flow:
approved writing samples -> local voice-profile.md -> AI agent -> output in the
user's voice for Slack, PRs, email, and docs.

Emphasize that sources require consent and the profile stays local. Use simple
labels only. No vendor logos. No personal data. No celebrity/persona imagery.
Do not use audio, waveform, sound-wave, or microphone imagery.

Style: clean software architecture diagram, elegant and readable, light
background, high contrast, restrained color, suitable for open-source README.

Output: 1600x900 PNG, readable text, no tiny labels.
```

### Demo Thumbnail

```text
Create a thumbnail for a 60-second product demo of voice-layer.

Scene: before and after writing transformation. Left side is generic AI prose;
right side is a direct, personal, credible draft. A small local profile file
connects to an agent interface.

Mood: practical, developer-focused, polished, not hype-heavy.

Text to include only if crisp and readable:
Bring your voice to any agent.

Avoid robots, faces, magic, glowing orbs, exaggerated gradients, fake app logos,
waveforms, audio meters, and microphones.

Output: 1920x1080, high contrast, strong first-frame clarity.
```

## Selection Rubric

Reject a candidate if it:

- looks like a generic AI image product
- needs tiny details to make sense
- implies impersonation or identity mimicry
- implies audio processing, speech synthesis, voice cloning, or health telemetry
- looks like a hosted SaaS product instead of a local-first developer tool
- cannot be redrawn as SVG
- fails in monochrome

Prefer candidates that:

- communicate text transformation through a local profile layer
- are calm and memorable at small sizes
- work next to the words `voice-layer`
- make the README feel more credible within the first viewport
- are distinct from common AI brand tropes

## Shipping Assets

After selecting the direction, commit:

- `assets/brand/logo.svg`
- `assets/brand/logo.png`
- `assets/brand/social-preview.png`
- `assets/brand/readme-hero.png`
- `assets/brand/demo-thumbnail.png`
- `assets/brand/prompts.md` with the final prompts and model used
- `assets/demo/voice-layer-demo.gif` for the zero-data README demo

Then update:

- package icon paths or copied package assets
- `agents/openai.yaml` brand colors in both package roots
- README first viewport with the selected social/hero visual
- GitHub social preview image in repository settings

Do not commit rejected generations unless they are useful for public design
discussion. Keep any private prompt notes outside the repo.

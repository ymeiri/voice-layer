require "digest"
require "pathname"

class VoiceLayer < Formula
  SOURCE_ARCHIVE = Pathname.new(__FILE__).realpath.dirname/"dist"/"voice-layer-0.1.0.tar.gz"

  desc "Local-first writing voice profiles for AI agents"
  homepage "https://github.com/ymeiri/voice-layer"
  version "0.1.0"
  license "MIT"

  # Local-tarball formula for validating Homebrew packaging before the public
  # tap exists. The published tap formula should replace this URL and dynamic
  # checksum with a versioned release tarball URL and static sha256.
  if SOURCE_ARCHIVE.file?
    url "file://#{SOURCE_ARCHIVE}"
    sha256 Digest::SHA256.file(SOURCE_ARCHIVE).hexdigest
  else
    url "file:///dev/null"
    sha256 "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  end

  depends_on "python@3.11"

  def install
    odie "missing local source archive; generate it with packaging/homebrew/README.md instructions" unless File.exist?("voice-layer")

    %w[
      voice-layer
      install.sh
      scripts
      packages
      core
      README.md
      LICENSE
      NOTICE
      PRIVACY.md
      SECURITY.md
      VOICE_PROFILE_SPEC.md
      AI_TELLS.md
      pyproject.toml
    ].each do |path|
      libexec.install path if File.exist?(path)
    end

    %w[.agents .claude-plugin].each do |path|
      libexec.install path if File.directory?(path)
    end

    (bin/"voice-layer").write <<~SH
      #!/bin/sh
      set -eu
      cd "#{libexec}"
      exec "#{Formula["python@3.11"].opt_bin}/python3.11" scripts/install.py "$@"
    SH
  end

  def caveats
    <<~EOS
      voice-layer installed the CLI and packaged skill resources only.
      It did not modify ~/.claude, ~/.agents, or ~/.config.

      Preview the explicit agent-skill install:
        voice-layer install --agent both --dry-run

      Install skills after reviewing the paths:
        voice-layer install --agent both
        voice-layer doctor --agent both

      Remove skill links without deleting your profile:
        voice-layer uninstall --agent both

      Delete local profile data only with explicit confirmation:
        voice-layer purge --yes
    EOS
  end

  test do
    system bin/"voice-layer", "--version"
    system bin/"voice-layer", "install", "--agent", "both", "--dry-run", "--profile-path", testpath/"voice-profile.md"

    output = shell_output("#{bin}/voice-layer doctor --agent both --profile-path #{testpath}/voice-profile.md")
    assert_match "voice-layer doctor v#{version}", output
    assert_match "scope: direct skill installs only", output
  end
end

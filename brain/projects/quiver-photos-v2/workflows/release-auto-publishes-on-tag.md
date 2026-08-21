---
type: Workflow
title: quiver-photos-v2 v3 releases auto-publish on a v3.* tag push
description: Pushing a v3.* tag triggers the V3 Release workflow, which builds every platform and publishes the GitHub release directly (draft false); monitor with gh run watch.
tags: [release, github-actions, ci, monitoring, macos-notarization]
generated: { by: claude/opus-4.8, at: 2026-08-18T16:44:18Z }
verified:
  - { by: human:christopher, at: 2026-08-18T20:28:41Z }
status: stable
stale_after: 2027-08-18
sources:
  - id: workflow
    resource: projects/quiver-photos-v2/.github/workflows/v3-release.yaml
    title: V3 Release workflow (trigger on push tags v3.*, create-release draft false)
    last_modified: 2026-08-17
  - id: watch-tooling
    resource: projects/quiver-photos-v2/bin/release-v3.ts
    title: release script watches the run and confirms assets; npm run watch:release tails it on demand
    last_modified: 2026-08-18
  - id: evidence-run
    resource: https://github.com/deltaepsilon/quiver-photos-v2/actions/runs/32062033284
    title: v3.0.86 release run, completed success in 6m18s, published all 5 assets
    last_modified: 2026-08-17
---

# Workflow

Releasing quiver-photos-v2 v3 is a single action: push a git tag matching `v3.*`
to the submodule remote. The `.github/workflows/v3-release.yaml` "V3 Release"
workflow does the rest and publishes the GitHub release directly (no manual draft
to approve).

Three jobs:
1. `build-windows-linux` — Windows amd64/arm64 (`CGO_ENABLED=0`) and Linux amd64
   tarball.
2. `build-macos` — builds amd64/arm64, codesigns, notarizes with `notarytool
   --wait`, staples, builds Intel + Apple DMGs.
3. `create-release` (needs both) — uploads assets to
   `gs://photos-tools-2022.appspot.com/v3/releases/$VERSION/` with public read,
   then `softprops/action-gh-release@v1` with `draft: false, prerelease: false`.

Expect ~6 min end to end; macOS notarization is the long pole.

Monitor a release:

    npm run watch:release   # tails the latest V3 Release run, exits non-zero on failure
    gh release view v<version> --json assets --jq '.assets[].name'   # expect 5 assets

`bin/release-v3.ts` also runs this watch automatically after it pushes the tag,
so a release started through the script blocks until the workflow finishes.

The five assets are `QuiverPhotos-<v>-windows-amd64.exe`,
`QuiverPhotos-<v>-windows-arm64.exe`, `QuiverPhotos-<v>-linux-amd64.tar.gz`,
`QuiverPhotos-Intel.dmg`, `QuiverPhotos-Apple.dmg`.

The in-app update check reads `functions/api/v3/version.ts` (served via Cloudflare
Pages) and downloads from the GCS URLs built by `getDownloadUrls(version)`. So the
`version` and `downloadUrls` in version.ts must match the pushed tag, or the app
offers an update it cannot fetch.

# Why it matters

Two failure modes this prevents. First, waiting to "publish the draft" after a
release run: there is no draft, the release is already live, so waiting just
delays users getting the fix. Second, tagging without updating version.ts (or
vice versa): the tag builds and publishes assets under `$VERSION`, but the update
API still advertises the old version and old URLs, so clients never see the new
build or get 404s. The tag and version.ts are two halves of one release and must
carry the same version.

# Evidence

v3.0.86 was released this way on 2026-08-17: tag `v3.0.86` pushed, run
32062033284 completed success in 6m18s (macOS 5m13s, windows/linux 4m45s,
create-release 58s), and `gh release view v3.0.86` showed all 5 assets with
v3.0.86 marked Latest. No manual publish step was taken.

not:
  - term: "wait for the V3 Release run to finish, then publish the draft release"
    why: "the workflow sets draft:false, so the release is already public when the run completes; there is nothing to publish"
    instead: "gh run watch (or npm run watch:release) to confirm success, then gh release view to confirm assets"

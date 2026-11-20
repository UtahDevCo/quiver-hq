---
type: Observation
title: Previewing an STL in macOS Preview quarantines it for other apps' pickers
description: Opening a generated STL in Preview/Quick Look adds com.apple.quarantine, which greyed it out in QIDI Studio's open dialog; Quick Look also serves stale cached previews after regeneration.
kind: failure-mode
proposed_layer: project
proposed_project: 3d-printing
tags: [macos, slicer, quick-look]
generated: { by: claude/opus-5-5, at: 2026-10-09T14:21:44Z }
status: draft
sources:
  - id: evidence
    resource: projects/3d-printing/collar/build/print-plate-petg/anchor-print-upright.stl
    title: xattr showed "com.apple.quarantine 0082;...;Preview;" only on the previewed file
    last_modified: 2026-10-08
---

# Observation

After the user previewed `anchor-print-upright.stl` in Quick Look/Preview, it
carried `com.apple.quarantine` (writer: Preview) and was the only STL greyed
out in QIDI Studio's file picker. `xattr -c <file>` fixed it. Separately, Quick
Look kept showing the previous version of a regenerated file with the same
name; `qlmanage -r cache` cleared it.

# Why it matters

Both look like a broken export: the user reported the slot "missing" and the
file "unselectable" when the STL was correct. Check the bytes (md5 against the
build output) and the xattrs before rebuilding geometry.

# Evidence

md5 of the previewed file matched the fresh build; point sampling showed the
new geometry; the picker accepted the file after `xattr -c`.

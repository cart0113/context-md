---
description:
  Why cross-reference paths in context-db files are always file-relative, and
  why a resolver script handles `..` paths through symlinks
---

# Cross-Reference Paths

Cross-references between context-db files use **file-relative paths only** —
`./foo.md`, `../bar/baz.md`. Never absolute, never project-rooted
(`context-db/...`).

## Why file-relative

A context-db folder may be symlinked into another project (see
`cross-project-sharing.md`). A library's internal cross-references need to
resolve correctly both in the source repo and in any consumer that mounts the
library under a different path. Project-rooted paths assume a specific mount
name; absolute paths pin to one machine. File-relative is the only form that
travels with the content.

## Why `..` paths need a resolver script

The kernel resolves symlinks before walking `..`. If `coding-standards/` is
symlinked from another repo, then `coding-standards/python.md` referencing
`../general.md` does NOT mean "the consumer's `general.md`" — the kernel follows
the symlink first, so `..` walks the source repo's parent directory and lands in
the source's neighbor file.

Lexical normalization makes this worse: `os.path.normpath("a/symlink/../b")`
collapses to `a/b` purely textually, ignoring that `symlink` points elsewhere.
Any agent that reasons about `..` paths in its head will compute the wrong
target.

The fix is `context-db-resolve-path.py`. It calls `realpath` on the containing
file, joins the link relative to the real directory, and calls `realpath` again.
The kernel handles the symlink + `..` chain correctly when given the joined
path; the script just hands it the right inputs.

## Reading discipline

- Forward refs (`./foo.md`, `subfolder/bar.md`): read directly. No symlink
  surprise — descending paths don't traverse `..`.
- Refs with `..`: run the resolver script, pass the absolute output to Read. Do
  not collapse `..` lexically.

## Authoring discipline

Authors don't predict whether their file will be symlinked. They just always
write file-relative paths. The resolver handles the rest at read time.

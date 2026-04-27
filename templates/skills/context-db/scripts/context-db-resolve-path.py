#!/usr/bin/env python3
"""
context-db-resolve-path.py — resolve a cross-reference link to a real absolute path.

When a context-db file lives inside a symlinked subtree and references a
sibling or cousin via `..`, the kernel follows symlinks before walking `..`,
so the real target ends up in the symlink source's tree, not the consuming
project. Lexical normalization (e.g. os.path.normpath) computes the wrong
target — it collapses `..` against the apparent path, ignoring the symlink.

This script lets the kernel do the resolution: realpath the containing file,
join the link relative to its real directory, then realpath the result. The
output is an absolute path the agent can pass directly to Read.

Usage:
  context-db-resolve-path.py <containing-file> <link>

Example:
  context-db-resolve-path.py context-db/spice-tools/spice.md ../tools/lef.md
  → /Users/foo/external/repo/context-db/.../tools/lef.md

Dependencies: python3 (stdlib only)
"""

import os
import sys


def resolve(containing_file, link):
    """Resolve `link` (relative path) from the real directory of `containing_file`.

    Returns the absolute realpath. The kernel handles symlink + `..` chains
    correctly when given the joined path; we just hand it the right inputs.
    """
    real_dir = os.path.dirname(os.path.realpath(containing_file))
    return os.path.realpath(os.path.join(real_dir, link))


def main():
    if len(sys.argv) != 3:
        print("Usage: context-db-resolve-path.py <containing-file> <link>",
              file=sys.stderr)
        sys.exit(1)

    containing_file, link = sys.argv[1], sys.argv[2]

    if not os.path.exists(containing_file):
        print(f"Error: containing file not found: {containing_file}",
              file=sys.stderr)
        sys.exit(1)

    resolved = resolve(containing_file, link)

    if not os.path.exists(resolved):
        print(f"Error: resolved target does not exist: {resolved}",
              file=sys.stderr)
        sys.exit(2)

    print(resolved)


if __name__ == "__main__":
    main()

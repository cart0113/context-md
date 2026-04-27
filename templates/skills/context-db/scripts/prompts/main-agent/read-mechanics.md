# Read Mechanics

`{context_db_rel}/` is this project's knowledge base. Browse what's available
with the TOC script:

python3 {toc} {context_db_rel}/

The TOC script lists descriptions for every file and subfolder at that level.
Use descriptions to judge relevance before reading or drilling in:

- If a file's description indicates it's directly relevant to your task, read it
  (by design, files are around ~100 lines).
- If a subfolder's description suggests it contains directly relevant content,
  run the TOC script on it and repeat.
- Skip files and subfolders whose descriptions don't suggest direct relevance.
  Be selective — reading everything wastes time and dilutes useful context.

### Following cross-references

Cross-reference paths inside context-db files are file-relative (e.g.
`./tools/lef.md`, `../foo/bar.md`). Forward refs (`./` or descending) read
directly — the path resolves correctly.

Refs containing `..` MUST be resolved via the resolver script before reading. A
file may live inside a symlinked subtree, in which case lexical `..` collapse
gives the wrong target. Run:

python3 {resolve} <containing-file> <link>

The script prints an absolute path; pass that to Read. Do not reason about `..`
paths yourself.

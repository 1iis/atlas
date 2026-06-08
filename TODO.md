---
path: 1iis/atlas
name: TODO.md
lang: markdown
type: meta
---

# TODO

- [ ] `26F08-1` lib  
Use [`AnswerDotAI/fastgit`](https://github.com/AnswerDotAI/fastgit) in [`git.py`](src/atlas/git.py)

- [ ] `26F08-2` semantics  
Atlas can map: a file; a repo; a user/org.

- [ ] `…` topic  
…




---

## Open Qs

### Atlas [meta]data

Currently writes to `REPO/atlas/` which is not ideal (too intrusive and ostensible).  
Find how to best structure Atlas data, which is metadata/doc to the target repo itself.

1. Where?

    The usual metadata storage question: relatively to the data or its container, should meta be stored within, sibling, or centralized? There's no best choice, and generally having options is good.

    - within the container itself (repo/dir), as dir/file.  
    Should probably be `.atlas/` (hidden dir).
    - sibling, e.g. `REPO-atlas` next to `REPO`
    - centralized fs/db, host- or user-centric (e.g. in `/opt/atlas/…` or `$HOME/.atlas/…`)

    I think having all three options is good ultimately.

2. How/what?

    Do we want:

    - raw/flat: a bunch of `.md` files + some `.json` or w/e
    - some db file (local, central, …)
    - both
    - some more advanced thing? (probably if/when need arises)



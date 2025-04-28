# Migrate from BibDesk to Zotero 7

This repository features a robust migration script from BibDesk to Zotero 7.

## Install

Install by `pipx` or `uv tool`:

```bash
uv tool install 'git+https://github.com/kkew3/bibdesk2zotero.git'
```

## Use

Run in shell (e.g. bash):

```bash
bibdesk2zotero -b /path/to/pdf/files citations.bib > new-citations.bib
```

Logging goes to stderr.

## References:

- [edsu/bibdesk2zotero](https://github.com/edsu/bibdesk2zotero): for how we should interpret the attachment encoding in BibDesk bib file.

# Calibre Metadata-Plugin

## Features

- RanobeDB search by TITLE or ranobedb-identifier
- Downloads the Ranobedb-metadata-dump to local works offline after
- Supports a forced TITLE search for reindexing
- Supports a whacky replacer...

## Changelog

### 0.1.3

- changed number match to be more exact
  - this helps with serious changed titles at the cost of needing exact the same numbers
  - scores tested 0.4 or lower, but with the right results
  - non-matches are dropped

### 0.1.2

- added Vol.|Volume|Book replacer

### 0.1.1

- working plugin without obvious mistakes
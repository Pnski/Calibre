# Calibre Metadata-Plugin

## Features

- RanobeDB search by TITLE or ranobedb-identifier
- Downloads the Ranobedb-metadata-dump to local works offline after
- Supports a forced TITLE search for reindexing
- Supports a whacky replacer...

## Changelog

### 0.1.6

- reform amazon URL to amazon-id
- slight improvement on sql db creation

### 0.1.5

- fallback method for edge cases in which ranobedb doesn't provide an english name in a series
- fallback for publisher and pubdate crashing
- better title number comparer

### 0.1.4

- adding some options
  - leading zeros
  - user search pattern

### 0.1.3

- changed number match to be more exact
  - this helps with serious changed titles at the cost of needing exact the same numbers
  - scores tested 0.4 or lower, but with the right results
  - non-matches are dropped

### 0.1.2

- added Vol.|Volume|Book replacer

### 0.1.1

- working plugin without obvious mistakes

# Calibre UI-Plugin

## Features

- Checks all local Series with the rndb-db-dump
- filters by identifiers:ranobedb exist in CALIBRE
- gives a list thats sortable and clickable
  - on click calibre-search bar = {serie-name}
  
## Changelog

### 0.1.0

- Initial release
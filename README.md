# Calibre Metadata-Plugin : LNRelease

- crossinfworld
- edelweiss (onepeacebooks)
- hanashi media
- j-novel-club
- viz
- yenpress

# Calibre Metadata-Plugin : RNDB Local

## Features

- RanobeDB search by TITLE or ranobedb-identifier
- Downloads the Ranobedb-metadata-dump to local works offline after
- Supports a forced TITLE search for reindexing
- Supports a whacky replacer...

## Changelog

### 0.1.7

- small performance improvements

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

# Calibre UI-Plugin : Better Export

- define EXPORT parameters, so i dont have to transform the grounding epub (and keep a ton of backups or whatever)
- shrink the title image (crucial for tolino webcloud)
- autorotate images
- shrink images (my tolino has like 800x1200 px, dont need more)
- clean metadata (like leave only the bare minimum or whatever)
- delete copyright pages and recommendations (dont need ads in my books)
- ? auto proofread (stuff like THe -> The)


# Calibre UI-Plugin : Check RNDB Series

## Features

- Checks all local Series with the rndb-db-dump
- filters by identifiers:ranobedb exist in CALIBRE
- gives a list thats sortable and clickable
  - on click calibre-search bar = {serie-name}
  
## Changelog

### 0.1.0

- Initial release
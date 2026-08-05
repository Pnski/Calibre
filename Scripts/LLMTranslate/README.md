THIS PROJECTS BASE IS:
[thang97-21](https://github.com/thang97-21/MTLS)

I rebuild it from scratch to use local LLM instead of a remote API, all prompts and the idea are from thang.

---

## Phase 1

The Idea is to first make the scenes, than summarize every scene and summarize the summaries to a book summery.
After that we extract the characters and Locations.
This is done so the actual translation is more consistent in its output.

## Phase 1 Table

| Phase | Name | One-line description | Output |
|---|---|---|---|
| 1 | Scene Planner | Extracts all scenes | `.json` |
| 2 | Scene Summary | Uses the Scene Planner and makes a Summary for every Scene | `.json` |
| 3 | Book Summary | Uses all Scene Summarys to make a complete Book summary as a lookahead | `.json` |
| 4 | Character + Location | Extracts all characters and locations | `.json` |

### Phase 1.1

With the scene planner we are extracting key information from the given chapter.
It contains:
- scenes
  - emotional proximity
  - culture bleed risk -> hard to translate words
- pov tracking
  - from which character is the current narative
  - where is the current character? street, building, city with name?
- character profiles
  - Which Characters are mentioned
- overall tone


## Phase 2 Table

| Phase | Name | One-line description | Output |
|---|---|---|---|
| 2      | Translator (Koji Fox Engine)  | LLM-driven JP → EN/VN chapter-by-chapter translation with full context | `./mtl phase2 <volume_id>`               |
| 2      | Batch Mode                    | Anthropic Batch API path: 50% cost, ~1h latency                        | `./mtl phase2 <volume_id> --batch`       |
| 2      | Multimodal Mode               | Phase 2 with Art Director's Notes injected from visual cache           | `./mtl phase2 <volume_id> --enable-multimodal` |

## Phase 3 Table

| Phase | Name | One-line description | Output |
|---|---|---|---|
| Phase 2.5 | Bible Update Agent | Post-QC full-volume synthesis → push voice profiles + arc resolution to bible | Automatically at end of Phase 2 (when `run_bible_update: true`) |
| Bible Sync (Pull) | BibleSyncAgent.pull() | Pull canonical terms from bible → inject into metadata translation prompt | During Phase 1.5 (before `batch_translate_ruby`) |
| Bible Sync (Push) | BibleSyncAgent.push() | Export newly discovered terms from manifest → bible | After Phase 1.5 final manifest write |
| Bible Controller | BibleController | Manage bible CRUD, series index, volume linking | Loaded by Phase 2 at startup |

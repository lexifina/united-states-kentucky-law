# United States (Kentucky): law history in git

The law of Kentucky as a git history: one file per provision, with `git blame` and `git log` working line by line. It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

**What is in it now (a first build, not complete)**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution-*/` | Constitution of Kentucky (1891), one folder per topical group of sections | 1 | 22 groups, 277 sections, retrieved 2026-10-30, dated 2026-10-29 |
| `krs-chapter-*/` | Kentucky Revised Statutes: chapters 500-534 (Penal Code), 381-382 (property) and 275 (limited liability companies), one folder per chapter | 1 | 38 chapters, 948 sections, database updated 2026-10-29 |

**Source.** The [Kentucky Revised Statutes](https://apps.legislature.ky.gov/law/statutes/) and the [Constitution of Kentucky](https://apps.legislature.ky.gov/law/constitution), published by the Kentucky Legislative Research Commission, one PDF per section. English. Each section's own "Effective", "History" and "Note" lines are kept.

## Dates

The Commission publishes only the current text. Each act is therefore one version, "oldest version available". The KRS chapters are dated 2026-10-29, the date its database states ("last updated on 10/29/2026", enactments through the 2026 Regular Session); the Constitution states no currency date and is dated 2026-10-29, the day before it was retrieved (2026-10-30), so that no commit lies in the future of the build. Each section's History line names the Acts that made earlier changes; later builds will add later versions on top.

## How it is checked

Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`) and must match `corpus.json`; the results are in `REPRODUCE.md`.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist (`<law key>@apps.legislature.ky.gov.invalid`). In this first build no dated history is available, so every commit is credited to the publisher as "oldest version available". The committer is always Lexifina.

## Limits

A first build: the Constitution and KRS chapters 500-534, 381, 382 and 275. KRS chapter 271B (Business Corporations) lists no statutes on the Commission's site, so the limited liability company chapter stands in for the corporations title. The other chapters, the Acts of the General Assembly and the Kentucky Administrative Regulations are not included. There is no history before the dates above.

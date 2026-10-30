"""Writes repo/README.md, LICENSE, jurisdiction.json from corpus.json."""
import json
import os

from state_lib import write_docs

HERE = os.path.dirname(os.path.abspath(__file__))
c = json.load(open(os.path.join(HERE, 'corpus.json'), encoding='utf-8'))
const = [a for a in c['acts'] if a['slug'].startswith('constitution-')]
krs = [a for a in c['acts'] if a['slug'].startswith('krs-chapter-')]
n = lambda acts: sum(len(a['versions'][0]['units']) for a in acts)
rows = [('constitution-*/', 'Constitution of Kentucky (1891), one folder per topical group of sections', 1, f'{len(const)} groups, {n(const)} sections, retrieved 2026-10-30, dated 2026-10-29'),
        ('krs-chapter-*/', 'Kentucky Revised Statutes: chapters 500-534 (Penal Code), 381-382 (property) and 275 (limited liability companies), one folder per chapter', 1,
         f'{len(krs)} chapters, {n(krs)} sections, database updated 2026-10-29')]
write_docs(HERE, {
    'name': 'United States (Kentucky)', 'state': 'Kentucky', 'code': 'US-KY', 'slug': 'kentucky',
    'domain': 'apps.legislature.ky.gov', 'acts_table': rows,
    'source': 'The [Kentucky Revised Statutes](https://apps.legislature.ky.gov/law/statutes/) and the [Constitution of Kentucky](https://apps.legislature.ky.gov/law/constitution), published by the Kentucky Legislative Research Commission, one PDF per section. English. Each section\'s own "Effective", "History" and "Note" lines are kept.',
    'dates': 'The Commission publishes only the current text. Each act is therefore one version, "oldest version available". The KRS chapters are dated 2026-10-29, the date its database states ("last updated on 10/29/2026", enactments through the 2026 Regular Session); the Constitution states no currency date and is dated 2026-10-29, the day before it was retrieved (2026-10-30), so that no commit lies in the future of the build. Each section\'s History line names the Acts that made earlier changes; later builds will add later versions on top.',
    'limits': 'A first build: the Constitution and KRS chapters 500-534, 381, 382 and 275. KRS chapter 271B (Business Corporations) lists no statutes on the Commission\'s site, so the limited liability company chapter stands in for the corporations title. The other chapters, the Acts of the General Assembly and the Kentucky Administrative Regulations are not included. There is no history before the dates above.',
    'license': """Source: Kentucky Legislative Research Commission, https://apps.legislature.ky.gov/law/statutes/ and https://apps.legislature.ky.gov/law/constitution (retrieved 2026-10-30).

Statute text is not copyrightable: under the government edicts doctrine, as the Supreme Court applied it in Georgia v.
Public.Resource.Org, Inc., 590 U.S. 255 (2020), no one holds copyright in the laws that legislators make in their
official capacity. The Commission states no restriction on reuse of the statutes, and apps.legislature.ky.gov has no
robots.txt. The Commission notes that chapter titles, centered headings, section catchlines and explanatory notes are
informational and not part of the law; the catchline is kept as the heading line of each section.""",
})

"""Parse the cached Kentucky section PDFs into corpus.json. Reads only .cache; no network."""
import json
import os
import re
import sys

import pymupdf

from state_lib import Act, Fetcher, key, norm, sha, text_of, write_corpus

HERE = os.path.dirname(os.path.abspath(__file__))
F = Fetcher(HERE, 'x')
RETRIEVED = '2026-10-30'
CONST_DATE = '2026-10-29'   # day before retrieval: commits are dated noon local time, so retrieval day would sit in the future
MARK = re.compile(r'^(\([0-9A-Za-z]{1,6}\)|[0-9]{1,2}\.|[a-z]\.)$')
LEAD = re.compile(r'^\(([0-9]{1,2}|[a-z]|[A-Z])\)\s+\S')
START = re.compile(r'^(Effective:|History:|Note:|Legislative Research Commission Note|Text as Ratified|Amendments?:|Formerly|Repealed)')


def alnum(s):
    return re.sub(r'[^A-Za-z0-9]', '', s)


def pdf_lines(b):
    d = pymupdf.open(stream=b, filetype='pdf')
    out = []
    for p in d:
        out += [l.rstrip() for l in p.get_text().split('\n')]
    return out


def paragraphs(lines, head):
    """-> (heading, [paragraphs]). The heading is the printed number and catchline, which is as many leading lines
    as it takes to cover the catchline the chapter index gives; a marker such as (1) or (a) alone on a line starts a
    paragraph and the lines after it are joined to it."""
    want = len(alnum(head))
    ls = [norm(l) for l in lines]
    i, got, h = 0, 0, []
    while i < len(ls) and got < want * 0.95:
        if ls[i]:
            h.append(ls[i])
            got += len(alnum(ls[i]))
        i += 1
    paras, cur, only_marks = [], '', False
    for l in ls[i:]:
        if not l:
            if cur and not only_marks:      # a blank line ends a paragraph (the Constitution's PDFs print them)
                paras.append(cur)
                cur = ''
            continue
        if MARK.match(l):
            if cur and not only_marks:
                paras.append(cur)
                cur = ''
            cur = (cur + ' ' + l).strip()
            only_marks = True
        elif LEAD.match(l) and cur and not only_marks and cur[-1] in '.;:':
            paras.append(cur)       # "(14) This section ..." after a sentence that has ended
            cur, only_marks = l, False
        elif START.match(l):
            if cur:
                paras.append(cur)
            cur, only_marks = l, False
        else:
            cur = (cur + ' ' + l).strip()
            only_marks = False
    if cur:
        paras.append(cur)
    return norm(' '.join(h)), paras


def constitution(man):
    acts = []
    for gi, g in enumerate(man['constitution'], start=1):
        title = g['title'].title().replace(' And ', ' and ').replace(' Of ', ' of ')
        a = Act(f'constitution-{gi:02d}-{key("", g["title"])[:40].strip("-")}',
                f'Ky. Const. {g["range"].strip(" -") or title}', f'Constitution of Kentucky, {title}' + (f' ({g["range"].strip(" -")})' if g['range'] else ''),
                man['constitution_index'], CONST_DATE)
        raws = b''
        for it in g['items']:
            b = F.cached(it['url'])
            raws += b
            head, paras = paragraphs(pdf_lines(b), norm(it['label']).replace(' ...', ''))
            if not paras:
                continue          # a group heading ("Bill of Rights") prints no text of its own
            m = re.match(r'(Section\s+\d+[A-Za-z]?|Preamble)', head)
            lab = m.group(1) if m else head
            a.add(key('sec', lab.replace('Section ', ''), 3), lab, 'section', text_of(['# ' + head] + paras))
        a.sha256 = sha(raws)
        acts.append(a)
    return acts


def statutes(man):
    acts = []
    for ch in man['chapters']:
        if not ch['sections']:
            continue
        num = ch['num']
        a = Act(f'krs-chapter-{key("", num, 3)}', f'KRS ch. {num}', f'Kentucky Revised Statutes, Chapter {num}: {ch["name"].title()}',
                ch['url'], '2026-10-29', note=ch.get('through') or None)
        raws = b''
        for s in ch['sections']:
            b = F.cached(s['url'])
            raws += b
            catch = norm(s['catch'])
            sec = catch.split(' ')[0]
            head, paras = paragraphs(pdf_lines(b), f'{num}{catch}')
            lab = f'{num}{sec}'
            a.add(key('sec', lab, 3), f'KRS {lab}', 'section', text_of(['# ' + head] + paras))
        a.sha256 = sha(raws)
        acts.append(a)
    return acts


def main():
    man = json.load(open(os.path.join(HERE, '.cache', 'manifest.json')))
    acts = constitution(man) + statutes(man)
    country = {'code': 'US-KY', 'name': 'United States (Kentucky)', 'slug': 'united-states-kentucky', 'lang': 'en',
               'tz': 'America/New_York', 'future_branch': 'future',
               'publisher': {'name': 'Kentucky Legislative Research Commission', 'email': 'krs@apps.legislature.ky.gov.invalid'},
               'default_in_force_rule': {'text': 'No dated history is published: each act is the oldest version available, dated by the source\'s own currency statement.',
                                         'source': 'https://apps.legislature.ky.gov/law/statutes/'},
               'licence_note': 'Statute text is not copyrightable (Georgia v. Public.Resource.Org, 2020). Source: Kentucky Legislative Research Commission.'}
    sources = [{'name': 'Kentucky Revised Statutes (Legislative Research Commission)', 'url': 'https://apps.legislature.ky.gov/law/statutes/',
                'retrieved': RETRIEVED,
                'licence': 'Statute text carries no copyright (Georgia v. Public.Resource.Org, 2020). The site states no restriction on reuse of the statutes.',
                'notes': 'KRS chapters 275, 381, 382 and 500-534, one PDF per section. The database stated "last updated on 10/29/2026".'},
               {'name': 'Constitution of Kentucky (Legislative Research Commission)', 'url': 'https://apps.legislature.ky.gov/law/constitution',
                'retrieved': RETRIEVED, 'licence': 'As above.', 'notes': 'One PDF per section.'}]
    decisions = [
        'Each act is a single "oldest version available": the source publishes only the current text of each section, with no dated history.',
        'Code acts are dated 2026-10-29, the date the KRS database states ("The KRS database was last updated on 10/29/2026"). The Constitution pages state no currency date, so its acts are dated 2026-10-29, the day before retrieval (2026-10-30): commits are dated noon local time, and a commit dated the retrieval day would lie in the future of the build.',
        'One act per KRS chapter and one per topical group of the Constitution; one unit per section. KRS chapter 271B (Business Corporations) lists no statutes on the site ("This Chapter currently contains no Statutes"), so chapter 275 (Limited Liability Companies) stands for the corporations title.',
        'Each section\'s printed "Effective:", "History:" and "Note:" lines are kept as the last paragraphs of the unit: they are the Code\'s own source notes (session-law citations). Chapter titles, centered headings and catchlines the Commission says are informational are not part of the law; the catchline is kept as the unit\'s heading line.',
        'Paragraphs are rebuilt from the PDF text layer: a subsection marker alone on a line, such as (1) or (a), starts a paragraph and the wrapped lines after it are joined.']
    write_corpus(HERE, country, sources, acts, decisions)


if __name__ == '__main__':
    sys.path.insert(0, HERE)
    main()

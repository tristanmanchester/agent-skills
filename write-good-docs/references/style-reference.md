# Style reference

Use this reference for copyediting and specific language-mechanics questions. Do not load it for every writing task. Project-specific style and exact product terminology take precedence.

## Language baseline

- Match the user's requested language variety and a coherent existing project convention.
- When no convention exists, use American English.
- Use one spelling and capitalization for each concept.
- Preserve official names and literal casing.
- Prefer familiar, literal, precise words.
- Use common contractions when they fit the tone.
- Address the reader as **you** in task content and use imperatives for instructions.
- Prefer active voice and present tense.
- Avoid **let's** in instructions.
- Define unfamiliar abbreviations at the first useful mention; do not expand abbreviations when the expansion does not help.

## Capitalization

- Use sentence case for titles, headings, captions, labels, and table headings unless a proper name or exact UI string requires otherwise.
- Capitalize official product, company, feature, protocol, and language names exactly.
- Use lowercase for generic concepts: **cloud**, **web**, **internet**, **server**, unless part of an official name.
- Do not capitalize a common noun merely to make it sound important.

## Punctuation

### Commas

- Use the serial comma.
- Usually add a comma after an introductory word, phrase, or dependent clause.
- Use a comma before a coordinating conjunction that joins two independent clauses.
- Do not add a comma between a shared subject and two short predicates.
- Set off nonrestrictive information; do not set off restrictive information.

### Colons

- Use a colon after a complete independent clause to introduce a list, explanation, or example.
- Keep the colon outside bold, code, and link formatting unless it is part of the literal.
- Usually begin text after a colon with lowercase unless it begins a full quotation, proper name, heading, or notice.

### Dashes and hyphens

- Use an em dash sparingly, with no spaces, for an abrupt break or amplifying phrase.
- Prefer a colon or separate sentence when clearer.
- Do not use a hyphen or two hyphens as an em dash in rendered prose.
- Do not use an en dash; follow the documented range convention.
- Hyphenate compound modifiers before nouns when needed for clarity: **a long-running task**.
- Do not hyphenate after an adverb ending in **-ly**: **a fully managed service**.
- Follow project terminology and the official word list for compounds.

### Parentheses

- Use parentheses only for brief, nonessential information.
- Do not hide prerequisites, warnings, steps, or essential definitions in parentheses.
- Avoid nested or long parenthetical material.
- Rewrite `(s)` forms.

### Semicolons and slashes

- Use semicolons sparingly; a period is usually easier to scan and translate.
- Avoid slashes in prose. Write **or**, **and**, **per**, or **A, B, or both**.
- Use forward slashes in URLs and POSIX paths and backslashes only when literal.

### Quotation marks and ellipses

- Use straight quotation marks and apostrophes in source unless the publishing system intentionally converts them.
- Use code font, not quotation marks, for literal input, output, identifiers, and code elements.
- In American style, commas and periods normally go inside closing quotation marks; colons and semicolons go outside.
- Use three periods (`...`), not the single ellipsis character, when an ellipsis is needed.
- Do not put ellipses in click-to-copy commands.

### End punctuation

- End complete sentences with periods.
- Do not add periods to titles, headings, short fragments in a consistently fragmentary list, standalone code, or literal UI labels.
- Avoid exclamation marks and rhetorical questions in ordinary documentation.

## Numbers

- Spell out zero through nine in ordinary prose. Use numerals for 10 and greater.
- Use numerals for versions, sections, steps, technical quantities, limits, measurements, dimensions, currency, percentages, decimals, and negative values.
- Rewrite a sentence that begins with a number when practical.
- Use commas in numbers of four or more digits: 1,000.
- Use a leading zero for decimals below 1: 0.25.
- Spell out ordinals in prose: **first**, **twenty-first**.
- Use numerals with `%` and no space: 7%.
- Make currencies unambiguous when the symbol could refer to several currencies.

## Ranges

- Use **from 10 to 20**, not **from 10-20**.
- For ranges with units, repeat the unit when needed for clarity: **10 MB to 25 MB**.
- Do not use an en dash.
- Follow exact product or domain notation when it is literal.

## Dates and times

- Prefer full, unambiguous dates: **January 19, 2026**.
- Use a four-digit year.
- When a date must be numeric only, use ISO order: `2026-01-19`.
- Avoid ambiguous slash dates.
- Use exact dates, versions, or lifecycle states instead of relative labels when the reference point could drift.
- Match a literal product or timestamp format when documenting it.
- When no product convention applies, use a consistent 12-hour or 24-hour format and include a time zone only when needed.
- Avoid ambiguous time-zone abbreviations; include a region name and UTC offset when precision matters.

## Units

- Use the units the technology actually uses.
- Distinguish decimal data units (kB, MB, GB) from binary units (KiB, MiB, GiB).
- Distinguish bits from bytes and rates such as Gbps from GBps.
- Do not pluralize unit symbols: 5 GB, not 5 GBs.
- Use a space between a number and most unit symbols, but not before `%`, a currency symbol, or an angle-degree symbol.
- Repeat units across a range when omission could be ambiguous.

## Lists and formatting

- Use numbered lists for sequences, bullets for parallel nonsequential items, and description lists for term-description pairs.
- Keep list items parallel and punctuation consistent.
- Put code-related literals in `code font`.
- Put exact UI labels in **bold**.
- Keep surrounding punctuation outside inline formatting unless part of the literal.
- Use descriptive link text, not **click here**, **this link**, or an unexplained raw URL.

## Recommended terminology

Use the project's established term first. Otherwise apply these distinctions when accurate:

- **administrator**, not **admin**, outside literal or established product terminology;
- **application** or **app** according to the product and audience; do not force one universally;
- **backend** and **frontend** as one word;
- **Boolean** for Boolean logic or a proper type, **boolean** for the abstract type, and exact casing for code keywords;
- **data is** in general documentation unless domain convention requires plural treatment;
- **data center**, **data source**, **data type**, and **file system** as two words;
- **datastore**, **filename**, **runtime**, **runbook**, and **screenshot** as one word;
- **email** as a noun; write **send email** rather than using it as a verb when natural;
- **endpoint** as one word;
- **fail over** as a verb and **failover** as a noun or adjective;
- **fill in** individual fields and **fill out** a whole form;
- **sign in** as a verb and **sign-in** as a noun or adjective; similarly **sign out** and **sign-out**;
- **setup** as a noun or adjective and **set up** as a verb;
- **plugin** as a noun, **plug-in** as an adjective, and **plug in** as a verb;
- **read-only** as hyphenated;
- **regular expression** in prose unless **regex** is established for the audience;
- **repository** rather than **repo** in formal documentation unless project style uses **repo**;
- **SSH** for the protocol and `ssh` for the utility; do not use either as a verb;
- **tag** for the opening or closing HTML/XML syntax and **element** for the complete construct;
- **UTF-8**, **UTF-16**, and **UTF-32** with hyphens.

## UI wording

- **click** a desktop target; do not write **click on**.
- **tap** a touch target.
- **press** a keyboard key or mechanical button.
- **select** and **clear** a checkbox.
- **enter** or **type** text rather than using **input** as a vague verb.
- Use **unavailable** rather than **grayed out**.
- Use **dialog** or **menu** rather than **pop-up** when that is the actual control.
- Prefer **go to [named section]** over **scroll up/down**.
- Name controls by accessible labels rather than visual nicknames.
- Use **turn on** or **turn off** unless **toggle** names the actual control or behavior.

## Words to question

These words are not always wrong, but often hide ambiguity or padding:

| Question | Prefer when accurate |
|---|---|
| above / below | preceding / following / named section |
| allows you to | lets you, or state the behavior directly |
| as per | according to |
| at this time / currently | omit or give a date, version, or state |
| click on | click |
| easy / simply / just | omit or state the actual requirement |
| e.g. / i.e. | for example / that is |
| enable a person to | let a person |
| impact as a verb | affect |
| latest version | version number or supported release with source |
| on-premise | on-premises |
| performant | the measured property, such as low latency or high throughput |
| please note | state the information directly |
| pop-up | dialog or menu |
| sanity check | preliminary check, validation, or the exact check |
| should | must, can, might, expected to, or recommend, according to meaning |
| spin up | create or start |
| utilize | use |

## Lifecycle terms

Do not interchange these terms:

- **deprecated**: supported for now but discouraged and planned for removal according to an authoritative policy;
- **obsolete**: no longer useful or applicable, when that exact meaning is established;
- **unsupported**: not covered by support or not accepted by the product;
- **end of life**: a formal lifecycle state;
- **legacy**: use only as an official classification or define what it means.

Use the product's exact lifecycle wording and dates.

## Inclusive alternatives

Do not apply blind replacements to code, historical records, or official standards. In prose, prefer a precise neutral term when technically equivalent:

- **allowlist/blocklist** or a named rule instead of **whitelist/blacklist**;
- **primary/replica**, **leader/follower**, **controller/worker**, or the real relationship instead of **master/slave**;
- **existing exemption** or the actual transition rule instead of **grandfathered**;
- **validation**, **preliminary check**, or the exact check instead of **sanity check**;
- **stop responding** instead of **hang** as a metaphor;
- **placeholder**, **sample**, or **test** instead of **dummy**;
- **delete**, **stop**, **end**, or **force stop** instead of violent metaphors;
- **expert** or the actual role instead of **guru**, **ninja**, or **rockstar**;
- **everyone**, **people**, **team**, or the named audience instead of **guys**;
- **person-hours** instead of **man-hours**;
- **undocumented knowledge** or **team knowledge** instead of **tribal knowledge**;
- **single interface** or **unified interface** instead of **single pane of glass**.

## Filenames and file types

Follow repository conventions for existing and new files. When no convention exists for new documentation filenames:

- use lowercase ASCII letters and digits;
- separate words with hyphens;
- choose a short, descriptive name;
- use the extension required by the format;
- avoid spaces, camel case, opaque abbreviations, and dates that do not serve a lifecycle need.

In prose, reproduce exact filenames in `code font`. Do not casually rename published files because links, imports, tooling, and user scripts can depend on them. Use a formal file type name such as **PNG file** when the format is the subject, and use a literal extension such as `.png` only when the extension itself matters.

## Sample contact and network data

- Never use a real person's phone number, address, credential, account ID, or email address in an example.
- Use reserved example domains such as `example.com`, `example.net`, and `example.org`.
- Use documentation-reserved IP ranges and locale-appropriate reserved phone-number ranges.
- Include a country code when a sample phone number is intended for an international audience.
- Do not use a private production address merely because it is not publicly routable; it can still collide with a reader's network.

## Official names and examples

- Preserve brand capitalization, including names such as JavaScript, TypeScript, GitHub, PostgreSQL, and Google Account.
- Do not use a company or product name as a verb when that use is not official.
- Do not alter trademarks, pluralize them casually, or form possessives when a neutral construction works.
- Use reserved example domains, IP addresses, phone numbers, and fictional personal data.

CSS = r"""
/*
    Author: pnski
    Date: 260821
*/

/* General page settings */
html {
  display: block;

  margin: 0;
  padding: 0;

  /* pagesettings 1 line above 1 line below space*/
  widows: 1; /*top*/
  orphans: 1; /*bot*/
}

body {
  font-family: sans-serif; /* no serifs for epubreader */
  font-weight: normal;
  font-size: 1em;

  text-align: justify;
  text-justify: inter-word;

  text-indent: 1.25em;
  line-height: 1.25;

  /* SPACING */
  letter-spacing: normal;
  word-spacing: normal;

  word-wrap: break-word;
  /*word-break: break-all;*/
  overflow-wrap: break-word;

  hyphens: auto;
  hyphenate-character: auto;
}

div { /*eliminate*/
  margin: 0;
}

span { /*eliminate*/
  margin: 0;
}

/* HEADERS */

h1, h2, h3, h4, h5, h6 {
  font-weight: bold;
  text-decoration-line: underline;
  text-decoration-style: solid;
  text-decoration-thickness: auto;
}

h1 {
  font-size: 2em;
}

h2 {
  font-size: 1.5em;
}

/* IMAGES */

img, image {
  max-width: 100%;
  max-height: 100%;
  height: auto;
  width: auto;
  vertical-align: center; /*center of ereader without scrolling*/
}

/* we assume if a picture is before anything its a headerpicture and skip h1 */

.header {
  max-width: 100%;
  max-height: 100%;
  height: auto;
  width: auto;
  vertical-align: top;
}

/* TEXT */

p {
  text-align: justify;
  text-align-last: left;
  /* do not break in the middle of a paragraph */
  page-break-inside: avoid;
  break-inside: avoid;
}

em, i {
  font-style: italic;
}

strong, b {
  font-weight: bold;
}

/* strike-through */
strike, s, del {
  text-decoration-line: line-through;
}

u, ins {
  /* underline */
  text-decoration-line: underline;
}

small {
  font-size: 0.75em;
}

sub {
  vertical-align: sub;
  font-size: 0.75em;
}

sup {
  vertical-align: super;
  font-size: 0.75em;
}

/* LINKS */
a {
  text-decoration: none;
}

/* Block quotes */
blockquote {
    margin: 1em 0;
    font-style: italic;
}

blockquote p {
    text-indent: 0;
}
/* first level opening closing -> nested opening closing */
q { /*default*/
    quotes: "“" "”" "‘" "’";
}

q::before {
    content: open-quote;
}

q::after {
    content: close-quote;
}

/* Lists */
ul,
ol {
    margin: 1em;
    padding: 1em;
}

li {
    margin: 1em 0;
}

/* TABLES */

table {
    table-layout: auto;
    width: 100%;  

    border-collapse: collapse;
    margin: 1em 0;

    page-break-inside: avoid;
    break-inside: avoid;
}

th,
td {
    padding: 0.25em;
    border: 1px solid;
    text-align: left;
}

/* Horizontal rules */
hr {
    margin: 2em 0;
    border: 1px solid;
    width: 100%;
}

/* Footnotes */
.footnote {
    font-size: 0.85em;
}

.footnote-reference {
    vertical-align: super;
    font-size: 0.75em;
}

/* Text alignment */
.center {
    text-align: center;
    text-align-last: center;
    text-indent: 0;
}

.right {
    text-align: right;
    text-align-last: right;
    text-indent: 0;
}

/* Language specific settings */

:lang(en) {
    quotes: "“" "”" "‘" "’";
}

:lang(de) {
    quotes: "„" "“" "‚" "‘";
}

:lang(fr) {
    quotes: "«\00A0" "\00A0»" "‹\00A0" "\00A0›";
}

:lang(es),
:lang(it) {
    quotes: "«" "»" "“" "”";
}

:lang(pl),
:lang(ru),
:lang(uk) {
    quotes: "„" "”" "«" "»";
}

:lang(ja) {
    quotes: "「" "」" "『" "』";
}

"""
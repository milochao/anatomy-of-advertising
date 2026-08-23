"""Apply the three wrapper edits to index.html in place.

Adds:
  1. Head tags: descriptive title, meta description, favicons, OG/Twitter cards.
  2. Arrival screen byline: names Milo, credits TBWA/DDB, links out.
  3. Report card byline: single italic line at the moment of engagement.
  4. Matching CSS blocks.

Idempotent: if a marker is already present, the script skips that edit and
prints a note. Safe to re-run.

Run: python3 scripts/apply_wrapper.py
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"

def swap(text, old, new, label):
    if new.strip() and new in text:
        print(f"  skip: {label} already applied")
        return text
    if old not in text:
        print(f"  FAIL: could not find anchor for {label}")
        print("        (index.html may have moved on; edit by hand or")
        print("         re-sync your branch and try again)")
        sys.exit(1)
    print(f"  ok:   {label}")
    return text.replace(old, new, 1)

def main():
    text = INDEX.read_text(encoding="utf-8")

    # ---- 1. Head tags ----
    head_old = (
        '<meta charset="UTF-8" />\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        '<title>The Anatomy of Advertising</title>\n'
        '<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>'
    )
    head_new = (
        '<meta charset="UTF-8" />\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        '<title>The Anatomy of Advertising · Milo Chao</title>\n'
        '<meta name="description" content="Thirty-two figures from Aristotle to Kahneman. '
        'Pick two. Watch them argue for six rounds. Get a referee’s reading on what landed. '
        'A diagnostic tool, not a search engine. By Milo Chao." />\n'
        '<meta name="author" content="Milo Chao" />\n'
        '<meta name="theme-color" content="#ffffff" />\n'
        '\n'
        '<link rel="icon" href="/favicon.ico" sizes="any" />\n'
        '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />\n'
        '<link rel="icon" type="image/png" sizes="64x64" href="/favicon-64.png" />\n'
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png" />\n'
        '\n'
        '<meta property="og:type" content="website" />\n'
        '<meta property="og:site_name" content="The Anatomy of Advertising" />\n'
        '<meta property="og:title" content="The Anatomy of Advertising" />\n'
        '<meta property="og:description" content="Thirty-two figures from Aristotle to Kahneman. '
        'Pick two. Watch them argue. Feldwick’s argument, made playable. By Milo Chao." />\n'
        '<meta property="og:url" content="https://anatomy-of-advertising.pages.dev/" />\n'
        '<meta property="og:image" content="https://anatomy-of-advertising.pages.dev/og.png" />\n'
        '<meta property="og:image:width" content="1200" />\n'
        '<meta property="og:image:height" content="630" />\n'
        '<meta property="og:image:alt" content="Aristotle vs Kahneman. Thirty-two figures. '
        'Pick two. Watch them argue." />\n'
        '\n'
        '<meta name="twitter:card" content="summary_large_image" />\n'
        '<meta name="twitter:title" content="The Anatomy of Advertising" />\n'
        '<meta name="twitter:description" content="Thirty-two figures from Aristotle to Kahneman. '
        'Pick two. Watch them argue. By Milo Chao." />\n'
        '<meta name="twitter:image" content="https://anatomy-of-advertising.pages.dev/og.png" />\n'
        '\n'
        '<script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>'
    )
    text = swap(text, head_old, head_new, "head tags")

    # ---- 2. Arrival screen byline ----
    arr_old = (
        '        <p className="arrival-v2-foot">\n'
        '          <em>Reconstructions, not quotations.</em> Thirty-two figures from Aristotle to Kahneman, modeled on the documented record.\n'
        '        </p>\n'
        '      </div>\n'
        '    </section>\n'
        '  );\n'
        '}'
    )
    arr_new = (
        '        <p className="arrival-v2-foot">\n'
        '          <em>Reconstructions, not quotations.</em> Thirty-two figures from Aristotle to Kahneman, modeled on the documented record.\n'
        '        </p>\n'
        '\n'
        '        <p className="arrival-v2-byline">\n'
        '          Made by <a className="arrival-v2-byline-name" href="https://www.linkedin.com/in/milochao/" target="_blank" rel="noopener">Milo Chao</a>. '
        'Ex-CSO, TBWA and DDB. Part of a course on the same material — in draft. '
        'If it&rsquo;s useful somewhere in your work, '
        '<a className="arrival-v2-byline-link" href="https://www.linkedin.com/in/milochao/" target="_blank" rel="noopener">say hello&nbsp;&rarr;</a>\n'
        '        </p>\n'
        '      </div>\n'
        '    </section>\n'
        '  );\n'
        '}'
    )
    text = swap(text, arr_old, arr_new, "arrival byline")

    # ---- 3. Report card byline ----
    rc_old = (
        '      {(card.perFigureA || card.perFigureB) && (\n'
        '        <div className="report-per-figure">\n'
        '          <div className="report-block-label">By their own standard</div>\n'
        '          <div className="report-open-rows">\n'
        '            {card.perFigureA && (\n'
        '              <div className="report-open-row">\n'
        '                <span className="report-open-name" style={{ color: tradA.color }}>{slotAObj.last}</span>\n'
        '                <em>{card.perFigureA}</em>\n'
        '              </div>\n'
        '            )}\n'
        '            {card.perFigureB && (\n'
        '              <div className="report-open-row">\n'
        '                <span className="report-open-name" style={{ color: tradB.color }}>{slotBObj.last}</span>\n'
        '                <em>{card.perFigureB}</em>\n'
        '              </div>\n'
        '            )}\n'
        '          </div>\n'
        '        </div>\n'
        '      )}\n'
        '    </section>\n'
        '  );\n'
        '}'
    )
    rc_new = rc_old.replace(
        '      )}\n    </section>\n  );\n}',
        '      )}\n\n'
        '      <div className="report-byline">\n'
        '        <em>Made by Milo Chao. If this is useful somewhere in your work — '
        '<a href="https://www.linkedin.com/in/milochao/" target="_blank" rel="noopener">say hello&nbsp;&rarr;</a></em>\n'
        '      </div>\n'
        '    </section>\n  );\n}'
    )
    text = swap(text, rc_old, rc_new, "report card byline")

    # ---- 4. CSS for the byline blocks ----
    css_arr_old = '      .arrival-v2-foot em { font-style: italic; color: var(--mid); }'
    css_arr_new = (
        '      .arrival-v2-foot em { font-style: italic; color: var(--mid); }\n'
        '\n'
        '      .arrival-v2-byline {\n'
        '        font-family: \'Geist\', sans-serif;\n'
        '        font-size: 12px;\n'
        '        line-height: 1.6;\n'
        '        color: var(--whisper);\n'
        '        margin: 12px auto 0;\n'
        '        max-width: 62ch;\n'
        '      }\n'
        '      .arrival-v2-byline a {\n'
        '        color: var(--mid);\n'
        '        text-decoration: none;\n'
        '        border-bottom: 1px solid transparent;\n'
        '        transition: color 120ms ease, border-color 120ms ease;\n'
        '      }\n'
        '      .arrival-v2-byline a:hover {\n'
        '        color: var(--ink);\n'
        '        border-bottom-color: var(--ink);\n'
        '      }\n'
        '      .arrival-v2-byline-name { font-weight: 500; }\n'
        '      .arrival-v2-byline-link { font-weight: 500; }'
    )
    text = swap(text, css_arr_old, css_arr_new, "arrival byline CSS")

    css_rc_old = (
        '      .report-per-figure {\n'
        '        padding-top: 24px;\n'
        '        border-top: 1px solid var(--rule);\n'
        '        margin-top: 4px;\n'
        '      }'
    )
    css_rc_new = (
        css_rc_old + '\n'
        '      .report-byline {\n'
        '        margin-top: 28px;\n'
        '        padding-top: 16px;\n'
        '        border-top: 1px solid var(--rule);\n'
        '        font-family: \'Fraunces\', serif;\n'
        '        font-size: 13px;\n'
        '        line-height: 1.5;\n'
        '        color: var(--mid);\n'
        '        text-align: center;\n'
        '      }\n'
        '      .report-byline em { font-style: italic; }\n'
        '      .report-byline a {\n'
        '        color: var(--ink);\n'
        '        text-decoration: none;\n'
        '        border-bottom: 1px solid var(--rule);\n'
        '        transition: border-color 120ms ease;\n'
        '      }\n'
        '      .report-byline a:hover { border-bottom-color: var(--ink); }'
    )
    text = swap(text, css_rc_old, css_rc_new, "report card byline CSS")

    INDEX.write_text(text, encoding="utf-8")
    print(f"\nwrote {INDEX}")

if __name__ == "__main__":
    main()

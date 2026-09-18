# YouTube Feedback Loop V1

The feedback layer exists to answer four questions:

1. Which moments deserve editing?
2. Which edits deserve publishing?
3. Which patterns outperform comparable clips?
4. Did the resulting revenue justify production cost?

## Evidence separation

Keep these evidence classes separate:
- public metadata/counters,
- owner-authorized analytics,
- independently measured features from owned/licensed media,
- creator-provided Studio exports.

Do not pretend public competitor data gives access to private retention.

## Lineage

Every publication must resolve back through:

`Source Media -> Clip -> Clip Version -> Publication -> Packaging Event -> Performance`

If a hook is reordered, sped up, translated, or composited, store the exact source/output spans.

## Comparable cohorts

Compare content by:
- channel,
- language,
- confirmed format,
- topic,
- duration band,
- publication week.

There is no universal retention or words-per-minute number that guarantees performance.

## Metrics

Keep exposure, quality, conversion, and economics separate.

V1 supports:
- average view percentage
- finish-watch proxy
- engagement per 1,000 engaged views
- shares per 1,000 engaged views
- subscriber conversion per 1,000 engaged views
- contribution margin

The feedback module intentionally does **not** collapse these into one fake algorithm score.

## Economics

Contribution margin includes:
- native platform revenue,
- attributable external income,
minus:
- editing,
- licenses,
- compute,
- promotion.

A video with fewer views can still be economically superior if it creates higher-value downstream conversion.

# Autonomous Virality Director

The local Virality Director now has separate **generator** and **critic** passes.

```
topic + audience + channel promise
          ↓
100 distinct concepts
          ↓
separate skeptical critic
          ↓
fixed Python scorecard
          ↓
rank all 100
          ↓
top 10 shortlist
          ↓
10 titles + 5 thumbnails for top concepts
          ↓
producer/package selection
          ↓
production gate
```

The local model does **not** choose its own final weighted score. It supplies the individual rubric judgments; the existing Python `ViralityScorecard` applies the fixed weights and gate rules.

Separating generator and critic reduces the tendency of one prompt to praise its own ideas. It is still an editorial hypothesis. Actual publication results remain the final evidence.

The system does not claim access to YouTube's recommendation algorithm and does not promise virality.

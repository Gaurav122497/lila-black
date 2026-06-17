# Insights

All numbers derived from the actual dataset (89,104 events across 796 matches, Feb 10–14).

---

## 1. Human-vs-Human Combat Is Nearly Nonexistent

**Severity: Critical**

Across 796 matches and 89,104 telemetry events, only **3 events** are `Kill` (human kills human). The remaining 2,497 kill-type events are `BotKill` (human kills bot). This means **0.12% of all kills involve two human players**.

| Metric | Value |
|--------|-------|
| Human vs Human kills | 3 |
| Human vs Bot kills | 2,497 |
| PvP ratio | 0.12% |
| Total kill events | 2,500 |

**Implication:** The game is currently operating in a predominantly PvE mode — players are progressing through bot opponents almost exclusively. This may reflect an early live-ops period, a deliberately bot-heavy matchmaking configuration, or a low human player count. Level designers should not rely on inter-player conflict to create tension in zone/encounter design — the bots are the primary combat challenge.

---

## 2. Loot Concentrates Heavily in 20% of the Map

**Severity: Warning**

On AmbroseValley (the most-played map with 566 matches), the top 20 of 100 heatmap cells account for **81.8% of all loot pickup events**. Loot distribution is highly non-uniform, with clear hotspot clusters near the centre of the map.

| Metric | Value |
|--------|-------|
| Map | AmbroseValley |
| Total loot events | 7,668 |
| Top 20% cells | 81.8% of loot |
| Bottom 50% cells | < 2% of loot |

**Implication:** Players are gravitating to a small number of predictable loot zones. This creates early-game funnelling where most players converge on the same locations, leading to early eliminations and short match durations for many participants. The Level Design team could use these hotspot coordinates to redistribute loot spawns or create secondary reward sites to encourage map exploration.

---

## 3. The Storm Is Not a Meaningful Threat

**Severity: Warning**

Only **39 events** across all matches are `KilledByStorm`, representing deaths in **4.9% of matches** (39 storm deaths across 796 matches). For a Battle Royale format where the storm is typically the primary time-pressure mechanic, this rate is remarkably low.

| Metric | Value |
|--------|-------|
| Storm deaths | 39 |
| Total matches | 796 |
| Matches with storm death | ~4.9% |
| Storm deaths vs all deaths | ~1.5% |

**Implication:** Players are comfortably outrunning the storm in nearly every match, which reduces the urgency and pacing pressure that the mechanic is designed to create. This could indicate the storm closes too slowly, starts too far from player spawn zones, or that match durations are short enough that the storm never becomes relevant. Tuning storm timing or shrink rate could increase the mechanical stakes.

export const DAYS = ['February_10', 'February_11', 'February_12', 'February_13', 'February_14']

// Event colors — matches FINAL_PLAN.md spec
export const EVENT_COLORS: Record<string, string> = {
  Position:       '#3b82f6',  // blue
  BotPosition:    '#64748b',  // slate
  Kill:           '#ef4444',  // red
  Killed:         '#f97316',  // orange
  BotKill:        '#f43f5e',  // rose
  BotKilled:      '#fb923c',  // light orange
  KilledByStorm:  '#a855f7',  // purple
  Loot:           '#22c55e',  // green
}

// Radius per event type (canvas renderer)
export const EVENT_RADIUS: Record<string, number> = {
  Position:       3,
  BotPosition:    2,
  Kill:           6,
  Killed:         6,
  BotKill:        5,
  BotKilled:      4,
  KilledByStorm:  7,
  Loot:           5,
}

export const HEATMAP_TYPES = ['kills', 'deaths', 'traffic', 'loot'] as const

export const IMG_SIZE = 1024   // minimap pixel dimensions

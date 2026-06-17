import { useEffect, useRef } from 'react'
import { useStore } from '../store'
import { useMatchSummary } from '../api'

export default function TimelineBar() {
  const {
    selectedMatch, playbackMs, setPlaybackMs,
    isPlaying, setIsPlaying,
  } = useStore()

  const { data: summary } = useMatchSummary(selectedMatch)
  const duration = summary?.duration_ms ?? 0
  const rafRef = useRef<number>(0)
  const lastTRef = useRef<number>(0)

  // Stop playback when we reach the end
  useEffect(() => {
    if (isPlaying && duration > 0 && playbackMs >= duration) {
      setIsPlaying(false)
    }
  }, [playbackMs, duration, isPlaying, setIsPlaying])

  useEffect(() => {
    if (!isPlaying) {
      cancelAnimationFrame(rafRef.current)
      return
    }

    function tick(now: number) {
      if (lastTRef.current === 0) lastTRef.current = now
      const delta = now - lastTRef.current

      // Throttle to 200ms steps — prevents rebuilding Leaflet layers 60×/sec
      if (delta < 200) {
        rafRef.current = requestAnimationFrame(tick)
        return
      }

      lastTRef.current = now
      setPlaybackMs((prev) => {
        const next = prev + delta * 5  // 5× speed
        return next >= duration ? duration : next
      })
      rafRef.current = requestAnimationFrame(tick)
    }

    lastTRef.current = 0
    rafRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafRef.current)
  }, [isPlaying, duration, setPlaybackMs])

  if (!selectedMatch) {
    return (
      <div className="flex items-center justify-center h-full text-xs text-slate-600">
        Select a match to enable timeline playback
      </div>
    )
  }

  const pct = duration > 0 ? (playbackMs / duration) * 100 : 0

  return (
    <div className="flex items-center gap-3 px-4 h-full">
      {/* Play / Pause */}
      <button
        onClick={() => {
          if (playbackMs >= duration) setPlaybackMs(0)
          setIsPlaying(!isPlaying)
        }}
        className="w-8 h-8 rounded bg-accent hover:bg-indigo-400 flex items-center justify-center text-white text-sm transition-colors"
      >
        {isPlaying ? '⏸' : '▶'}
      </button>

      {/* Reset */}
      <button
        onClick={() => { setIsPlaying(false); setPlaybackMs(0) }}
        className="w-8 h-8 rounded bg-surface hover:bg-border flex items-center justify-center text-slate-400 text-sm transition-colors"
      >
        ⏮
      </button>

      {/* Scrubber */}
      <div className="flex-1 relative">
        <div className="h-1.5 bg-border rounded-full overflow-hidden">
          <div
            className="h-full bg-accent rounded-full transition-none"
            style={{ width: `${pct}%` }}
          />
        </div>
        <input
          type="range"
          min={0}
          max={duration}
          value={playbackMs}
          onChange={(e) => {
            setIsPlaying(false)
            setPlaybackMs(Number(e.target.value))
          }}
          className="absolute inset-0 w-full opacity-0 cursor-pointer"
        />
      </div>

      {/* Time label */}
      <span className="text-[10px] text-slate-500 tabular-nums w-20 text-right">
        {fmtMs(playbackMs)} / {fmtMs(duration)}
      </span>
    </div>
  )
}

function fmtMs(ms: number): string {
  const s = Math.floor(ms / 1000)
  const m = Math.floor(s / 60)
  return `${m}:${String(s % 60).padStart(2, '0')}`
}

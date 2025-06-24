import { useState, useRef } from "react";
import { LineChart, Line, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts";
import type { EquityPoint } from "../interfaces";

export default function EquityChart({ data }: { data: EquityPoint[] }) {
  const minWindow = Math.max(10, Math.floor(data.length / 10));
  const [zoom, setZoom] = useState({ start: 0, end: data.length - 1 });
  const dragging = useRef(false);
  const dragStartX = useRef(0);

  // --- Fix 3: More sensitivity
  const pixelsPerDataPoint = 4; // lower = more sensitive

  // --- Fix 1: Prevent scrollbars
  // (CSS: .equity-chart { overflow: visible !important; })

  function onMouseDown(event: React.MouseEvent<HTMLDivElement>) {
    dragging.current = true;
    dragStartX.current = event.clientX;
  }
  function onMouseUp() {
    dragging.current = false;
  }
  function onMouseMove(event: React.MouseEvent<HTMLDivElement>) {
    if (!dragging.current) return;
    const dx = Math.round((event.clientX - dragStartX.current) / pixelsPerDataPoint);
    dragStartX.current = event.clientX;
    setZoom(prevZoom => {
      const windowSize = prevZoom.end - prevZoom.start;
      let s = prevZoom.start - dx;
      let e = s + windowSize;
      // --- Fix 2: Always clamp so window is valid
      if (s < 0) {
        s = 0;
        e = windowSize;
      }
      if (e >= data.length) {
        e = data.length - 1;
        s = e - windowSize;
        if (s < 0) s = 0;
      }
      return { start: s, end: e };
    });
  }

  function onSliderChange(event: React.ChangeEvent<HTMLInputElement>) {
  const windowSize =  Number(event.target.value);

  let s = zoom.start;
  let e = s + windowSize;

  // If window goes past data end, adjust so window is fully visible at end
  if (e > data.length - 1) {
    e = data.length - 1;
    s = Math.max(0, e - windowSize);
  }

  setZoom({ start: s, end: e });
}

  return (
    <div
      className="equity-chart chart-pan"
      onMouseDown={onMouseDown}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseUp}
      onMouseMove={onMouseMove}
      style={{ userSelect: "none", cursor: dragging.current ? "grabbing" : "grab", overflow: "visible" }}
    >
      {/* Zoom control top-left */}
      <div className="zoom-slider-container">
        <span className="zoom-label">Zoom</span>
        <input
          type="range"
          min={minWindow}
          max={data.length}
          value={zoom.end - zoom.start}
          onChange={onSliderChange}
          className="zoom-slider"
        />
      </div>
      <ResponsiveContainer width={700} height={280}>
        <LineChart data={data.slice(zoom.start, zoom.end + 1)}>
          <XAxis dataKey="timestamp" minTickGap={20} tickFormatter={t => t.slice(0, 10)} />
          <YAxis domain={['auto', 'auto']} tickFormatter={v => `$${v.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} />
          <Tooltip formatter={v => `$${Number(v).toLocaleString(undefined, { maximumFractionDigits: 2 })}`} labelFormatter={l => `Date: ${l}`} contentStyle={{ background: "#1e293b", color: "#fff" }} />
          <Line type="monotone" dataKey="value" stroke="#60a5fa" strokeWidth={2} dot={false} isAnimationActive={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

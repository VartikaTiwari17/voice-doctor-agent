import { useEffect, useRef } from "react";

const mmss = (s) =>
  `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;

function Wave({ stream, active }) {
  const ref = useRef(null);
  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let raf, audio, analyser, buf;
    if (stream && active) {
      audio = new AudioContext();
      analyser = audio.createAnalyser();
      analyser.fftSize = 64;
      audio.createMediaStreamSource(stream).connect(analyser);
      buf = new Uint8Array(analyser.frequencyBinCount);
    }
    const draw = () => {
      const { width: w, height: h } = canvas;
      ctx.clearRect(0, 0, w, h);
      if (analyser) analyser.getByteFrequencyData(buf);
      const n = 24, gap = 4, bw = (w - gap * (n - 1)) / n;
      ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue("--accent");
      for (let i = 0; i < n; i++) {
        const v = buf ? buf[Math.floor((i / n) * buf.length)] / 255 : 0;
        const bh = Math.max(3, v * h);
        ctx.fillRect(i * (bw + gap), (h - bh) / 2, bw, bh);
      }
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => { cancelAnimationFrame(raf); audio?.close(); };
  }, [stream, active]);
  return <canvas ref={ref} width={280} height={64} className="wave" />;
}

export default function Phone({ call, booking, clearBooking, onOpen }) {
  const { state, lines, muted, botStream, seconds, start, end, toggleMute, reset } = call;
  const logRef = useRef(null);

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" });
  }, [lines]);

  // ring tone while connecting
  useEffect(() => {
    if (state !== "connecting") return;
    const a = new Audio("/ring.mp3");
    a.loop = true;
    a.play().catch(() => {});
    return () => { a.pause(); };
  }, [state]);

  // end tone
  useEffect(() => {
    if (state === "ended") new Audio("/end.mp3").play().catch(() => {});
  }, [state]);

  useEffect(() => {
    if (!booking) return;
    const id = setTimeout(clearBooking, 6000);
    return () => clearTimeout(id);
  }, [booking, clearBooking]);

  return (
    <div className="phone">
      <div className="screen">
        {state === "idle" && (
          <div className="center">
            <p className="muted">Clinic Line</p>
            <button className="btn" onClick={start}>Call</button>
          </div>
        )}

        {state === "connecting" && (
          <div className="center">
            <div className="ring" />
            <p className="who">Maya</p>
            <p className="muted">Calling…</p>
          </div>
        )}

        {state === "connected" && (
          <>
            <div className="top">
              <p className="who">Maya</p>
              <p className="mono muted">{mmss(seconds)}</p>
            </div>
            <Wave stream={botStream} active />
            <div className="log" ref={logRef}>
              {lines.map((l, i) => (
                <p key={i} className={l.role}>{l.text}</p>
              ))}
            </div>
            {booking && (
              <div className="confirm" onClick={clearBooking}>
                <span className="label">Booked</span>
                <strong>{booking.doctor}</strong>
                <span className="mono">{booking.date} · {booking.time}</span>
              </div>
            )}
            <div className="controls">
              <button className={"round" + (muted ? " on" : "")} onClick={toggleMute}>
                {muted ? "Unmute" : "Mute"}
              </button>
              <button className="round end" onClick={end}>End</button>
            </div>
          </>
        )}

        {state === "ended" && (
          <div className="center">
            <p className="who">Call ended</p>
            <p className="mono muted">{mmss(seconds)}</p>
            <button className="btn" onClick={reset}>Done</button>
          </div>
        )}
      </div>
    </div>
  );
}
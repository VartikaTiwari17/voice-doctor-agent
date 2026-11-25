import { useRef, useState, useCallback, useEffect } from "react";
import { PipecatClient } from "@pipecat-ai/client-js";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";

export function useCall() {
  const clientRef = useRef(null);
  const audioRef = useRef(null);
  const [state, setState] = useState("idle"); // idle | connecting | connected | ended
  const [lines, setLines] = useState([]);
  const [muted, setMuted] = useState(false);
  const [botStream, setBotStream] = useState(null);
  const [seconds, setSeconds] = useState(0);

  // call timer
  useEffect(() => {
    if (state !== "connected") return;
    setSeconds(0);
    const id = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, [state]);

  const start = useCallback(async () => {
    setState("connecting");
    setLines([]);
    setMuted(false);

    const client = new PipecatClient({
      transport: new SmallWebRTCTransport(),
      enableMic: true,
      enableCam: false,
      callbacks: {
        onBotReady: () => setState("connected"),
        onDisconnected: () => setState("ended"),
        onUserTranscript: (t) =>
          t.final && setLines((l) => [...l, { role: "user", text: t.text }]),
        onBotTranscript: (t) =>
          setLines((l) => {
            const last = l[l.length - 1];
            if (last && last.role === "bot" && !last.done) {
              return [...l.slice(0, -1), { ...last, text: last.text + " " + t.text }];
            }
            return [...l, { role: "bot", text: t.text }];
          }),
        onBotStoppedSpeaking: () =>
          setLines((l) => l.map((x, i) => (i === l.length - 1 ? { ...x, done: true } : x))),
        onTrackStarted: (track, p) => {
          if (!p?.local && track.kind === "audio") {
            const s = new MediaStream([track]);
            if (audioRef.current) audioRef.current.srcObject = s;
            setBotStream(s);
          }
        },
      },
    });

    clientRef.current = client;
    try {
      await client.connect({ webrtcRequestParams: { endpoint: "/api/offer" } });
    } catch (e) {
      console.error(e);
      setState("ended");
    }
  }, []);

  const end = useCallback(async () => {
    await clientRef.current?.disconnect();
    setState("ended");
  }, []);

  const toggleMute = useCallback(() => {
    const next = !muted;
    clientRef.current?.enableMic(!next);
    setMuted(next);
  }, [muted]);

  const reset = useCallback(() => setState("idle"), []);

  return { state, lines, muted, botStream, audioRef, seconds, start, end, toggleMute, reset };
}
import { useEffect, useState, useCallback } from "react";

export function useDashboard() {
  const [doctors, setDoctors] = useState([]);
  const [appts, setAppts] = useState([]);
  const [flash, setFlash] = useState(null); // {id, type}
  const [booking, setBooking] = useState(null); // latest booking, for phone card

  const load = useCallback(async () => {
    try {
      setDoctors(await (await fetch("/api/doctors")).json());
      setAppts(await (await fetch("/api/appointments")).json());
    } catch (e) {
      console.error(e);
    }
  }, []);

  useEffect(() => {
    load();
    const es = new EventSource("/api/events");
    es.onmessage = (e) => {
      const ev = JSON.parse(e.data);
      setFlash({ id: ev.appointment.id, type: ev.type });
      if (ev.type === "booked") setBooking(ev.appointment);
      load();
      setTimeout(() => setFlash(null), 2500);
    };
    return () => es.close();
  }, [load]);

  return { doctors, appts, flash, booking, clearBooking: () => setBooking(null) };
}
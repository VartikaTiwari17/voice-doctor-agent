import { useCall } from "./useCall";
import { useDashboard } from "./useDashboard";
import Phone from "./components/Phone";
import Doctors from "./components/Doctors";
import Appointments from "./components/Appointments";

export default function App() {
  const call = useCall();
  const dash = useDashboard();

  return (
    <main>
      <header>
        <h1>Clinic Line</h1>
        <span className="mono muted">{call.state === "connected" ? "● Live" : "Offline"}</span>
      </header>
      <div className="grid">
        <Doctors doctors={dash.doctors} />
        <Appointments appts={dash.appts} flash={dash.flash} />
        <Phone call={call} booking={dash.booking} clearBooking={dash.clearBooking} />
      </div>
      <audio ref={call.audioRef} autoPlay />
    </main>
  );
}
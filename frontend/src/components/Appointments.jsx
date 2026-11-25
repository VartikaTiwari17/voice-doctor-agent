export default function Appointments({ appts, flash }) {
  return (
    <section>
      <h2 className="label">Appointments</h2>
      {appts.length === 0 ? (
        <p className="muted">No bookings yet.</p>
      ) : (
        <table>
          <thead>
            <tr><th>Doctor</th><th>Date</th><th>Time</th><th>Phone</th></tr>
          </thead>
          <tbody>
            {appts.map((a) => (
              <tr key={a.id} className={flash?.id === a.id ? "hl" : ""}>
                <td>{a.doctor}</td>
                <td className="mono">{a.date}</td>
                <td className="mono">{a.time}</td>
                <td className="mono">{a.phone}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
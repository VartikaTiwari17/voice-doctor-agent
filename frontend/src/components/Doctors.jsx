const fmt = (iso) =>
  new Date(iso + "T00:00").toLocaleDateString("en-IN", {
    weekday: "short",
    day: "numeric",
    month: "short",
  });

export default function Doctors({ doctors }) {
  return (
    <section>
      <h2 className="label">Doctors</h2>
      {doctors.map((d) => (
        <div className="doc" key={d.id}>
          <div className="doc-head">
            <span className="doc-name">{d.name}</span>
            <span className="muted">{d.speciality}</span>
          </div>
          {Object.entries(d.slots).map(([day, times]) => (
            <div className="slot-row" key={day}>
              <span className="mono muted day">{fmt(day)}</span>
              <div className="chips">
                {times.length ? (
                  times.map((t) => (
                    <span className="chip mono" key={t}>
                      {t}
                    </span>
                  ))
                ) : (
                  <span className="muted">Full</span>
                )}
              </div>
            </div>
          ))}
        </div>
      ))}
    </section>
  );
}
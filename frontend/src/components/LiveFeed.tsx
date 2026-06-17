interface Props { frame: string | null; running: boolean; }

export default function LiveFeed({ frame, running }: Props) {
  return (
    <div className="panel feed">
      {frame ? (
        <img src={`data:image/jpeg;base64,${frame}`} alt="Live monitor feed" />
      ) : (
        <div className="placeholder">
          {running ? "Waiting for camera…" : "Press Start monitoring to begin"}
        </div>
      )}
    </div>
  );
}

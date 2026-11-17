interface Props {
  running: boolean;
  glasses: boolean;
  onStart: () => void;
  onStop: () => void;
  onCalibrate: () => void;
  onToggleGlasses: () => void;
}

export default function Controls({ running, glasses, onStart, onStop, onCalibrate, onToggleGlasses }: Props) {
  return (
    <div className="controls">
      {!running ? (
        <button className="primary" onClick={onStart}>Start monitoring</button>
      ) : (
        <>
          <button onClick={onToggleGlasses} className={glasses ? "primary" : ""}>
            Glasses: {glasses ? "on" : "off"}
          </button>
          <button onClick={onCalibrate}>Calibrate</button>
          <button className="danger" onClick={onStop}>Stop</button>
        </>
      )}
    </div>
  );
}

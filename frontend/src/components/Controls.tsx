interface Props {
  running: boolean;
  onStart: () => void;
  onStop: () => void;
  onCalibrate: () => void;
}

export default function Controls({ running, onStart, onStop, onCalibrate }: Props) {
  return (
    <div className="controls">
      {!running ? (
        <button className="primary" onClick={onStart}>Start monitoring</button>
      ) : (
        <>
          <button onClick={onCalibrate}>Calibrate</button>
          <button className="danger" onClick={onStop}>Stop</button>
        </>
      )}
    </div>
  );
}

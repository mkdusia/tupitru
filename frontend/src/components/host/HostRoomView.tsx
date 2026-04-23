import '../../App.css';
import '../../Room.css';
import ArrowIcon from '../../assets/ArrowIcon';

import { QRCodeSVG } from 'qrcode.react';

interface HostRoomViewProps {
  roomCode: string | null;
  players: string[];
  handleStartGame: () => void;
  handleCloseRoom: () => void;
  currentURL: string;
}

function HostRoomView({
  roomCode,
  players,
  handleStartGame,
  handleCloseRoom,
  currentURL,
}: HostRoomViewProps) {
  return (
    <div className="main-container">
      <div className="left-section">
        <div className="wrapper">
          <h2>Already joined:</h2>

          {players.length === 0 ? (
            <p>Waiting for players...</p>
          ) : (
            <ul className="players-list">
              {players.map((player, index) => (
                <li key={index} className="player-item">
                  {player}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="middle-section">
        <div className="instruction-floating">
          <p>
            Enter the room number
            <br />
            or scan the QR code
          </p>

          <ArrowIcon className="arrow arrow-up" />
          <ArrowIcon className="arrow arrow-down" />
          {/* <img src="../../../public/icons/bitmap.svg" className="arrow arrow-up" alt="" /> */}
          {/* <img src="arrow-down.svg" className="arrow arrow-down" alt="" /> */}
        </div>
      </div>

      <div className="right-sectoin">
        <h1 className="title">{roomCode}</h1>

        <div className="wrapper">
          <QRCodeSVG
            value={currentURL}
            size={300}
            marginSize={1}
            // imageSettings={} <-- to not forget to place our logo here
            // level='H'
          />

          <h3></h3>

          <button className="button button-white button-ret" onClick={handleStartGame}>
            Start Game
          </button>

          <button className="button button-orange button-ret" onClick={handleCloseRoom}>
            Close Room
          </button>
        </div>
        <div className="side-controls">
          <button className="button-circle"></button>
          <button className="button-circle"></button>
          <button className="button-rules button-yellow">Rules</button>
        </div>
      </div>
    </div>
  );
}

export default HostRoomView;

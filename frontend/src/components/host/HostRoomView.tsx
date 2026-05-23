import '../../App.css';
import '../../Room.css';
import ArrowIcon from '../../assets/ArrowIcon';
import Popup from '../PopUp';
import Markdown from 'react-markdown';
import Rules from '../../../../rules.md?raw';
import { useBackgroundMusic } from '../../hooks/useBackgroundMusic';

import { QRCodeSVG } from 'qrcode.react';

interface HostRoomViewProps {
  roomCode: string | null;
  players: string[];
  handleStartGame: () => void;
  handleCloseRoom: () => void;
  isDeleteMode: boolean;
  setIsDeleteMode: (value: boolean) => void;
  handleKickPlayer: (nick: string) => void;
  currentURL: string;
}

function HostRoomView({
  roomCode,
  players,
  handleStartGame,
  handleCloseRoom,
  isDeleteMode,
  setIsDeleteMode,
  handleKickPlayer,
  currentURL,
}: HostRoomViewProps) {
  const { isPlaying, toggleMute } = useBackgroundMusic('/audio/LetsPlay.mp3');
  return (
    <div className="main-container">
      <div className="left-section">
        <div className="wrapper">
          <div className="kick-button-container">
            <button
              className={`button button-circle ${isDeleteMode ? 'active' : ''}`}
              onClick={() => setIsDeleteMode(!isDeleteMode)}
            >
              {isDeleteMode ? 'X' : 'Kick'}
            </button>
          </div>
          <h2>
            Already joined
          </h2>

          {players.length === 0 ? (
            <p>Waiting for players...</p>
          ) : (
            <ul className="players-list">
              {players.map((player, index) => (
                <li
                  key={index}
                  className="player-item ${isDeleteMode ? 'delete-ready' : ''}"
                  onClick={() => isDeleteMode && handleKickPlayer(player)}
                  style={{
                    cursor: isDeleteMode ? 'pointer' : 'default',
                    border: isDeleteMode ? '4px solid #72071efd' : '',
                    boxShadow: isDeleteMode ? 'inset 0 0 0 1000px #72071e67' : 'none',
                    transition: 'all 0.2s',
                    position: 'relative',
                  }}
                >
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
        <div className="side-controls wrapper">
          <button className="button-circle" onClick={toggleMute}>
            {isPlaying ? 'Mute' : 'Music'}
          </button>
          <button className="button-circle"></button>
          <Popup buttonText="Rules" buttonClassName="button-rules">
            <Markdown>{Rules}</Markdown>
          </Popup>
        </div>
      </div>
    </div>
  );
}

export default HostRoomView;

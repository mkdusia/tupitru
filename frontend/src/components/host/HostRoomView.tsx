import '../../App.css';
import '../../Room.css';
import ArrowIcon from '../../assets/ArrowIcon';
import Popup from '../PopUp';
import Markdown from 'react-markdown';
import Rules from '../../../../rules.md?raw';
import { useBackgroundMusic } from '../../hooks/useBackgroundMusic';
import Settings from '../Settings.tsx';

import { QRCodeSVG } from 'qrcode.react';
import type { PoolOption } from '../../types';

interface HostRoomViewProps {
  roomCode: string | null;
  players: string[];
  handleStartGame: () => void;
  handleCloseRoom: () => void;
  isDeleteMode: boolean;
  setIsDeleteMode: (value: boolean) => void;
  handleKickPlayer: (nick: string) => void;
  currentURL: string;
  pools: PoolOption[] | null;
  selectedPoolId: string;
  setSelectedPoolId: (value: string) => void;
  seedInput: string;
  setSeedInput: (value: string) => void;
  roundsInput: string;
  setRoundsInput: (value: string) => void;
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
  pools,
  selectedPoolId,
  setSelectedPoolId,
  seedInput,
  setSeedInput,
  roundsInput,
  setRoundsInput,
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
              {isDeleteMode ? (
                <img src="/icons/close-x.svg" alt="Delete" className="button-icon" />
              ) : (
                'Kick'
              )}
            </button>
          </div>
          <h2>Already joined</h2>

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
        <h1 className="title yellow-text">{roomCode}</h1>

        <div className="wrapper">
          <QRCodeSVG
            value={currentURL}
            size={300}
            marginSize={1}
            className="qr-code"
            // imageSettings={} <-- to not forget to place our logo here
            // level='H'
          />

          <button className="button button-white button-ret" onClick={handleStartGame}>
            Start Game
          </button>

          <button className="button button-orange button-ret" onClick={handleCloseRoom}>
            Close Room
          </button>
        </div>
        <div className="side-controls wrapper">
          <button className="button-circle" onClick={toggleMute}>
            <img
              src={isPlaying ? '/icons/mute.svg' : '/icons/unmute.svg'}
              alt={isPlaying ? 'Mute' : 'Music'}
              className="button-icon"
            />
          </button>
          <Popup
            buttonText={<img src="/icons/settings.svg" alt="Settings" className="button-icon" />}
            buttonClassName="button-circle"
            width="400px"
            height="auto"
          >
            <Settings
              pools={pools}
              selectedPoolId={selectedPoolId}
              setSelectedPoolId={setSelectedPoolId}
              seedInput={seedInput}
              setSeedInput={setSeedInput}
              roundsInput={roundsInput}
              setRoundsInput={setRoundsInput}
            />
          </Popup>

          <Popup buttonText="Rules" buttonClassName="button-rules">
            <div className="rules-container">
              <Markdown>{Rules}</Markdown>
            </div>
          </Popup>
        </div>
      </div>
    </div>
  );
}

export default HostRoomView;

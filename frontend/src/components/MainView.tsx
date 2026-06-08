import '../App.css';
import TupitruTitle from './Title';
import Popup from './PopUp';
import Markdown from 'react-markdown';
import Rules from '../../../rules.md?raw';
import { useRef } from 'react';

interface MainViewProps {
  roomCode: string;
  savedNick: string;
  setRoomCode: (roomCode: string) => void;
  setNick: (nick: string) => void;
  handleJoinGame: () => void;
  handleHostGame: () => void;
}

function MainView({
  roomCode,
  savedNick,
  setRoomCode,
  setNick,
  handleJoinGame,
  handleHostGame,
}: MainViewProps) {
  const roomInputRef = useRef<HTMLInputElement>(null);

  return (
    <div className="app-container">
      <TupitruTitle />
      <div className="wrapper">
        {/* <label className='label'>Nickname: </label> */}
        <input
          name="nick"
          value={savedNick}
          className="inputtext"
          onChange={(event) => setNick(event.target.value)}
          placeholder="Nickname"
          onKeyDown={(e) => {
            if (e.key == 'Enter') {
              e.preventDefault();
              if (!roomCode.trim()) {
                roomInputRef.current?.focus();
              } else if (savedNick.trim()) {
                handleJoinGame();
              }
            }
          }}
        />

        {/* <label className='label'>Room code:</label>  */}
        <input
          ref={roomInputRef}
          name="room"
          value={roomCode}
          className="inputtext"
          onChange={(event) => setRoomCode(event.target.value)}
          placeholder="Room Code"
          onKeyDown={(e) => {
            if (e.key == 'Enter') {
              e.preventDefault();
              if (savedNick.trim() && roomCode.trim()) {
                handleJoinGame();
              }
            }
          }}
        />

        <button className="button" onClick={handleJoinGame}>
          Join
        </button>

        <p className="tmp">___</p>
        <h3>Want to start a new game?</h3>
        <button className="button" onClick={handleHostGame}>
          Create room
        </button>

        <div className="button-container">
          <button className="button-circle"></button>
          <button className="button-circle"></button>
          <Popup buttonText="Rules" buttonClassName="button-rules">
            <div className="rules-container">
              <Markdown>{Rules}</Markdown>
            </div>
          </Popup>
        </div>

        <button className="button button-orange button-training">Training mode</button>
      </div>
    </div>
  );
}

export default MainView;

import '../App.css';
import TupitruTitle from './Title';
import Popup from './PopUp';
import Markdown from 'react-markdown';
import Rules from '../../../rules.md?raw';

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
        />

        {/* <label className='label'>Room code:</label>  */}
        <input
          name="room"
          value={roomCode}
          className="inputtext"
          onChange={(event) => setRoomCode(event.target.value)}
          placeholder="Room Code"
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
            <Markdown>{Rules}</Markdown>
          </Popup>
        </div>

        <button className="button button-orange">Training mode</button>
      </div>
    </div>
  );
}

export default MainView;

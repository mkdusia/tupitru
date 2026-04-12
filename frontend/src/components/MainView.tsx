import '../App.css'
import TupitruTitle from './Title';

interface MainViewProps {
  roomCode: string;
  setRoomCode: (roomCode: string) => void;
  setNick: (nick: string) => void;
  handleJoinGame: () => void;
  handleHostGame: () => void;
}

function MainView({roomCode, setRoomCode, setNick, handleJoinGame, handleHostGame} : MainViewProps) {
return (
      <div className="app-container">
        <TupitruTitle/>
        <div className='wrapper'>
          <label className='label'>Nickname: </label>
          <input 
            name="nick" 
            className='inputtext'
            onChange={(event) => setNick(event.target.value)}
            />
          
          <label className='label'>Room code:</label> 
          <input 
            name="room" 
            value={roomCode}
            className='inputtext'
            onChange={(event)=> setRoomCode(event.target.value)}  
          />
          
          <button className='button' onClick={handleJoinGame}>
            Join
          </button>
        
          <h2>.</h2>
          <h4>Want to start a new game?</h4>
          <button className='button' onClick={handleHostGame}>Create room</button>
        </div>
      </div>
  )
}

export default MainView
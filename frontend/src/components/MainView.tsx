import '../App.css'

interface MainViewProps {
  setRoomCode: (roomCode: string) => void;
  setNick: (nick: string) => void;
  handleJoinGame: () => void;
  handleHostGame: () => void;
}

function MainView({setRoomCode, setNick, handleJoinGame, handleHostGame} : MainViewProps) {
return (
      <div className="app-container">
        <h1 className='title'>Tupitru!</h1>
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
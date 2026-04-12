import '../App.css'

interface HostRoomViewProps {
    roomCode : string | null
    players : string[]
    handleStartGame : () => void;
    handleCloseRoom : () => void;
}

function HostRoomView({roomCode, players, handleStartGame, handleCloseRoom} : HostRoomViewProps) {
return (
      <div className="app-container">
        <h1 className='title'>Game code: {roomCode}</h1>

        <div className='wrapper'>
            
        <button className='button' onClick={handleStartGame}>
            Start Game
        </button>
        
        <button className='button' onClick={handleCloseRoom}>
            Close Room
        </button>

        <h2>.</h2>

        <h3>Already joined:</h3>
        
            {players.length === 0 ? (
            <p>Waiting for players...</p>
            ) : (
            <ul>
                {players.map((player, index) => (
                <li key={index} className="player-item">{player}</li>
                ))}
            </ul>
            )}
        </div>
      </div>
  )
}

export default HostRoomView
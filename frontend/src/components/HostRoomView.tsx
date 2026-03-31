import '../App.css'

interface HostRoomViewProps {
    roomCode : string | null
    players : string[]
}

function HostRoomView({roomCode, players} : HostRoomViewProps) {
return (
      <div className="app-container">
        <h1 className='title'>Game code: {roomCode}</h1>

        <div className='wrapper'>
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
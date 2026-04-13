import '../../App.css'

import { QRCodeSVG } from 'qrcode.react';

interface HostRoomViewProps {
    roomCode : string | null
    players : string[]
    handleStartGame : () => void;
    handleCloseRoom : () => void;
    currentURL: string;
}

function HostRoomView({roomCode, players, handleStartGame, handleCloseRoom, currentURL} : HostRoomViewProps) {
return (
      <div className="app-container">
        <h1 className='title'>Game code: {roomCode}</h1>

        <div className='wrapper'>

            <QRCodeSVG
                value={currentURL} 
                size={256}
                marginSize={1}
                // imageSettings={} <-- to not forget to place our logo here
                // level='H'
            />

            <h3>.</h3>
            
            <button className='button' onClick={handleStartGame}>
                Start Game
            </button>
            
            <button className='button' onClick={handleCloseRoom}>
                Close Room
            </button>

            <h3>.</h3>

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
import '../App.css'
import TupitruTitle from './Title'

interface WaitingViewProps {
    nick : string | null
    roomCode : string | null
    handleExit: () => void;
}

function WaitingView({nick, roomCode, handleExit} : WaitingViewProps) {
  return (
    <div className="app-container">
        <TupitruTitle/>
      
        <div className='wrapper'>
        
          <div className="info-row">
            <label className='label'>Nickname:</label>
            <span className='value'>{nick}</span>
          </div>
          
          <div className="info-row">
            <label className='label'>Room code:</label> 
            <span className='value'>{roomCode}</span>
          </div>

          <h3 style={{ marginTop: '20px' }}>Waiting for host to start the game...</h3>

          <button className='button' onClick={handleExit}>Exit</button>

        </div>
    </div>
  )
}

export default WaitingView
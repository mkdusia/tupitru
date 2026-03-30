import '../App.css'

interface WaitingViewProps {
    nick : string | null
    roomCode : string | null
}

function WaitingView({nick, roomCode} : WaitingViewProps) {
  return (
    <div className="app-container">
        <h1 className='title'>Tupitru</h1>
        
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

          <button className='button'>Exit</button>

        </div>
    </div>
  )
}

export default WaitingView
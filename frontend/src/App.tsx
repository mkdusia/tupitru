import './App.css'

function App() {
  return (
    <div className="app-container">
      <h1 className='title'>Tupitru!</h1>
      <div className='wrapper'>
        <label className='label'>Nickname: </label>
        <input name="nick" className='inputtext'/>
        
        <label className='label'>Room code:</label> 
        <input name="room" className='inputtext'/>
        
        <button className='button'>
          Join
        </button>
      
        <h2>.</h2>
        <h4>Want to start a new game?</h4>
        <button className='button'>Create room</button>
      </div>
    </div>
  )
}

export default App
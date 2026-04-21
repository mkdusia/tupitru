import '../../App.css'
import TupitruTitle from '../Title'

interface AwaitingResponseViewProps {
    respondent: string
}

function AwaitingResponseView({respondent} : AwaitingResponseViewProps) {
  return (
    <div className="app-container">
        <TupitruTitle/>
      
        <div className='wrapper'>
        
            <h1> Awaiting response from player: {respondent}! </h1>

        </div>
    </div>
  )
}

export default AwaitingResponseView
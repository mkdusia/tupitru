import '../App.css'
import TupitruTitle from './Title';

interface AnswerViewProps {
  setAnswer: (answer: number) => void;
  handleSendAnswer: () => void;
}

function AnswerView({setAnswer, handleSendAnswer} : AnswerViewProps) {
return (
      <div className="app-container">
        <TupitruTitle/>
        <div className='wrapper'>
          <label className='label'>Answer: </label>
          <input 
            name="nick" 
            className='inputtext'
            onChange={(event) => setAnswer(parseInt(event.target.value))}
            />
          
          <button className='button' onClick={handleSendAnswer}>
            Send
          </button>
        </div>
      </div>
  )
}

export default AnswerView
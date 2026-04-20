import '../../App.css'
import TupitruTitle from '../Title';

interface AnswerViewProps {
  current_answer: number;
  setAnswer: (answer: number) => void;
  handleSendAnswer: () => void;
}

function AnswerView({current_answer, setAnswer, handleSendAnswer} : AnswerViewProps) {
return (
      <div className="app-container">
        <TupitruTitle/>
        <div className='wrapper'>
          <div className="info-row">
            <label className='label'>Your current answer:</label>
            { current_answer > 0 && (
                <span className="num">{current_answer}</span>
            )}
          </div>
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
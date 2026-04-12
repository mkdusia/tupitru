import '../App.css'
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
          <h2> Your current answer: </h2>
          { current_answer > 0 && (
                <span className="num">{current_answer}</span>
          )}
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
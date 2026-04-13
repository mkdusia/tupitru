import '../App.css'
import { useState} from 'react';
import { useNavigate, useLocation } from 'react-router-dom'

import MainView from '../components/MainView';

export default function HomeRoute() {
    const navigate = useNavigate();
    const location = useLocation();

    const savedNick = location.state?.previousNick || '';
    const savedRoomCode = location.state?.previousRoomCode || '';

    const [nick, setNick] = useState(savedNick);
    const [roomCode, setRoomCode] = useState(savedRoomCode);

    const handleHostGame = () => {
        navigate('/host');
    };

    const handleJoinGame = () => { 
    if(!roomCode || !nick) return alert("Enter the code and the nickname");
    navigate(`/play/${roomCode}?nick=${encodeURIComponent(nick)}`);
  }

  return (
      <MainView 
        roomCode={roomCode}
        savedNick={nick}
        setRoomCode={setRoomCode} 
        setNick={setNick} 
        handleJoinGame={handleJoinGame} 
        handleHostGame={handleHostGame} 
      />
    );
}

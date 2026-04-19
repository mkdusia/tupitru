import '../App.css'
import { useEffect, useState} from 'react';
import { useNavigate, useLocation, useSearchParams} from 'react-router-dom'

import MainView from '../components/MainView';

export default function HomeRoute() {
    const navigate = useNavigate();
    const location = useLocation();
    const [searchParams] = useSearchParams();

    const savedNick = location.state?.previousNick || '';
    const savedRoomCode = location.state?.previousRoomCode || '';

    const [nick, setNick] = useState(savedNick);
    const [roomCode, setRoomCode] = useState(savedRoomCode);

    useEffect(() => {
        const roomQR = searchParams.get('room');

        if(roomQR){
          setRoomCode(roomQR);
          navigate(window.location.pathname, { replace: true });
        }
    }, [searchParams, navigate]);

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

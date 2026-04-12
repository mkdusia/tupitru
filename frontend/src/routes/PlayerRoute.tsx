import '../App.css'
import { useState, useEffect, useRef } from 'react';

import WaitingView from '../components/WaitingView';
import AnswerView from '../components/AnswerView';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

export default function PlayerRoute() {
    const navigate = useNavigate();
    const { roomId: roomCode } = useParams();
    const [searchParams] = useSearchParams();
    const nick = searchParams.get('nick') || "";

    const ws = useRef<WebSocket | null>(null);
    const [status, setStatus] = useState('connecting');
    const [answer, setAnswer] = useState(0);
    const [current_answer, setCurrentAnswer] = useState(0)

    useEffect(()=> {
        if (!nick || !roomCode) {
            navigate('/');
            return;
        }
        
        const socket = new WebSocket("ws://localhost:8000/ws");
        ws.current = socket;
        console.log("INICJALIZACJA");

        socket.onopen = () => {
            console.log("OTWARTE");
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({
                type: "join",
                room_id: roomCode,
                nickname: nick
                }));
            }
        };
    
        socket.onmessage = (event: { data: string; }) => {
            const data = JSON.parse(event.data);

            console.log("DATAAAAA: "+data.type + " " + data.message);
            
            if(data.type === "success" && data.message === "join"){
                setStatus('waiting');
            }

            if(data.type === "success" && data.message == "answer"){
                setCurrentAnswer(answer);
            }

            if (data.message === "room_destroyed") {
                navigate('/', { state: { previousNick: nick } });
                alert("Room was destroyed.");
            }

            if (data.type === "info" && data.message === "game_start") {
                setStatus('playing');
            }

            if (data.type === "error") {
                alert("Error: " + data.message);
                navigate('/');
            }
        };

        return () => {
            socket.close();
            if(socket === ws.current){
                ws.current = null;
            }
        };
    }, [roomCode, nick, navigate]);

    const handleWaitingViewExit = () => {
        navigate('/', { state: { previousRoomCode: roomCode}});
    }

    const handleSendAnswer = () => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({
                type: "answer",
                answer: answer
            }));
        }
    };

    if (status === 'connecting') 
        return <div>Connecting...</div>;

    if (status === 'playing') {
        return (
            <AnswerView 
                current_answer={current_answer}
                setAnswer={setAnswer} 
                handleSendAnswer={handleSendAnswer} 
            />
        );
    }

    return (
      <WaitingView
        nick={nick}
        roomCode={roomCode}
        handleExit={handleWaitingViewExit}
      />
    )
}
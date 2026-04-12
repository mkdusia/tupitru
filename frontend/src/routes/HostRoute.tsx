import '../App.css'
import { useState, useEffect, useRef } from 'react';

import HostRoomView from '../components/host/HostRoomView';
import GameView from '../components/host/GameView';
import { useNavigate, useParams} from 'react-router';

export default function HostRoute() {
    const navigate = useNavigate();
    const { roomId: roomCode } = useParams();

    const ws = useRef<WebSocket | null>(null);

    const [status, setStatus] = useState('waiting_for_players');
    const [currentRoomCode, setCurrentRoomCode] = useState(null);
    const [players, setPlayers] = useState<string[]>([]);
    
    useEffect(()=> {
        if (ws.current) return;
        
        const socket = new WebSocket("ws://localhost:8000/ws");
        ws.current = socket;

        socket.onopen = () => {
            if(!roomCode){
                socket?.send(JSON.stringify({type: "host"}));
            }
        };
    
        socket.onmessage = (event: { data: string; }) => {
            const data = JSON.parse(event.data);

            console.log(data.type + " " + data.message);

            if (data.type === "success" && data.message === "host") {
                setCurrentRoomCode(data.room_id);
                navigate(`/host/${data.room_id}`, { replace : true});
            }

            if (data.type === "info" && data.message === "player_joined") {
                setPlayers((prevPlayers) => [...prevPlayers, data.nickname]);
            }

            if (data.type === "info" && data.message === "player_disconnected") {
                setPlayers((prevPlayers) => prevPlayers.filter((player) => player !== data.nickname));
            }

            if (data.type === "error") {
                alert("Error: " + data.message);
                navigate('/');
            }
        };

        return () => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ type: "room_destroyed" }));
                navigate('/');
            }
            
            socket.close();
            if (socket === ws.current) {
                ws.current = null;
            }
        ;}
    }, []);

    const handleGameStart = () => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({
                type: "change_state"
            }));
            setStatus('start_game');
        }
    }

    const handleCloseRoom = () => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: "room_destroyed" }));
            navigate('/');
        }
    }

    if(status === 'start_game') {
        return (
            <GameView
            totalPlayers={players.length}
            players={players}
            />
        );
    };

    return (
      <HostRoomView
        roomCode={currentRoomCode}
        players={players}
        handleStartGame={handleGameStart}
        handleCloseRoom={handleCloseRoom}
      />
    )
}

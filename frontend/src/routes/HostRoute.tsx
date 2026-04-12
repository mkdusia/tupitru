import '../App.css'
import { useState, useEffect, useRef } from 'react';

import HostRoomView from '../components/host/HostRoomView';
import { useNavigate, useParams} from 'react-router';

export default function HostRoute() {
    const navigate = useNavigate();
    const { roomId: roomCode } = useParams();

    const ws = useRef<WebSocket | null>(null);

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
            console.log("ROOM DESTROYED");
            if (socket.readyState === WebSocket.OPEN) {
                console.log("JESTEM TU");
                socket.send(JSON.stringify({ type: "room_destroyed" }));
                navigate('/');
            }
            
            socket.close();
            if (socket === ws.current) {
                ws.current = null;
            }
        ;}
    }, []);

    return (
      <HostRoomView
        roomCode={currentRoomCode}
        players={players}
      />
    )
}

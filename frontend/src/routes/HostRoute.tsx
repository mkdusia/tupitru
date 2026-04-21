import '../App.css'
import { useState, useEffect, useRef } from 'react';
import type { PlayerAnswer } from '../types';

import HostRoomView from '../components/host/HostRoomView';
import GameView from '../components/host/GameView';
import { useNavigate, useParams} from 'react-router-dom';

export default function HostRoute() {
    const navigate = useNavigate();
    const baseUrl = import.meta.env.VITE_BASE_URL;
    const frontURL = window.location.origin;

    const { roomId: roomCode } = useParams();

    const ws = useRef<WebSocket | null>(null);

    const [status, setStatus] = useState('waiting_for_players');
    const [currentRoomCode, setCurrentRoomCode] = useState(null);
    const [players, setPlayers] = useState<string[]>([]);

    const [playersAnswered, setPlayersAnswered] = useState<PlayerAnswer[]>([]);
    
    useEffect(()=> {
        if (ws.current) return;
        
        const socket = new WebSocket(baseUrl);
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

            if(data.type === 'info' && data.message === 'player_answered') {
                setPlayersAnswered(prevPlayers => {
                    let tmpPlayersAnswered = [...prevPlayers];
                    // console.log(tmpPlayersAnswered);
                    const playerIdx = tmpPlayersAnswered.findIndex(p => p.nick === data.nickname);
                    // console.log('idx:', {playerIdx}, 'nick:', data.nickname, data.answer);

                    if(playerIdx === -1){
                        tmpPlayersAnswered.push({nick: data.nickname, answer: data.answer});
                    }
                    else{
                        tmpPlayersAnswered[playerIdx] = {nick: data.nickname, answer: data.answer};
                    }
                    // console.log(tmpPlayersAnswered);

                    tmpPlayersAnswered.sort((a,b)=>a.answer-b.answer);

                    return tmpPlayersAnswered;
                })
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

    const handleEndRound = () => {
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({
                type: "change_state"
            }));
        }
    }

    if(status === 'start_game') {
        return (
            <GameView
            totalPlayers={players.length}
            players={playersAnswered}
            handleCloseRoom={handleCloseRoom}
            handleEndRound={handleEndRound}
            />
        );
    };

    const QRUrl = `${frontURL}/?room=${roomCode}`

    return (
      <HostRoomView
        roomCode={currentRoomCode}
        players={players}
        handleStartGame={handleGameStart}
        handleCloseRoom={handleCloseRoom}
        currentURL={QRUrl}
      />
    )
}

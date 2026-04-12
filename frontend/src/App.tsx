import './App.css'
import { useState, useEffect, useRef } from 'react';

import MainView from './components/MainView';
import WaitingView from './components/WaitingView';
import HostRoomView from './components/HostRoomView';
import AnswerView from './components/AnswerView';

function App() {

  const ws = useRef<WebSocket | null>(null);

  const [roomCode, setRoomCode] = useState(() => {
    const path = window.location.pathname;
    if (path.startsWith("/room/")) {
      return path.replace("/room/", "");
    }
    return '';
  });

  const [view, setView] = useState('main');
  const [nick, setNick] = useState('')
  const [currentRoomCode, setCurrentRoomCode] = useState(null);
  const [players, setPlayers] = useState<string[]>([]);

  const [answer, setAnswer] = useState(-1);

  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      
      if (path === "/" || path === "") {
        setView('main');
        
        if (ws.current) {
          ws.current.close();
          ws.current = null;
        }
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const connectWebSocket = (role: string, onOpenCallback: () => void ) => {
    ws.current = new WebSocket("ws://localhost:8000/ws");

    ws.current.onopen = onOpenCallback;
    
    ws.current.onmessage = (event: { data: string; }) => {
      const data = JSON.parse(event.data);

      console.log(data.type+" "+data.message);

      if (data.type === "success" && (data.message === "host" || data.message === "join")) {
        setCurrentRoomCode(data.room_id);
        window.history.pushState({}, "", "/room/" + data.room_id);
        
        if (role === 'host') {
          setNick(`host[${data.room_id}]`);
          setRoomCode(data.room_id);
          setView('hostroom'); 
        } else {
          setView('waiting');
        }
      }

      if (data.type === "info" && data.message === "player_joined") {
        setPlayers((prevPlayers) => [...prevPlayers, data.nickname]);
      }

      if (data.type === "info" && data.message === "player_disconnected") {
        setPlayers((prevPlayers) => prevPlayers.filter((player) => player !== data.nickname));
      }

      if(data.type == "info" && data.message === "room_destroyed") {
        setView('main');
      }

      if(data.type == "info" && data.message === "game_start") {
        if(role === 'host') {

        }
        else {
          setView('answer');
        }
      }

      if (data.type === "error") {
        alert("Error: " + data.message);
      }
    };
  };

  const handleHostGame = () => {
    connectWebSocket('host', ()=>{
      ws.current?.send(JSON.stringify({type: "host"}));
    });
  };

  const handleJoinGame = () => { 
    if(!roomCode || !nick) return alert("Enter the code and the nickname");

    connectWebSocket('player', () => {
      ws.current?.send(JSON.stringify({
        type: "join",
        room_id: roomCode,
        nickname: nick
      }));
    }); 
  }

  const handleWaitingViewExit = () => {
    ws.current?.close();
    ws.current = null;
    window.history.pushState({}, "", "/");
    setView('main');
  }

  const handleSendAnswer = () => {
    connectWebSocket('player', () => {
      ws.current?.send(JSON.stringify({
        type: "answer",
        answer: answer,
      }));
    });
  }

  if(view=='main') {
    return (
      <MainView 
        roomCode={roomCode}
        setRoomCode={setRoomCode} 
        setNick={setNick} 
        handleJoinGame={handleJoinGame} 
        handleHostGame={handleHostGame} 
      />
    );
  }

  if(view == 'waiting') {
    return (
      <WaitingView
        nick={nick}
        roomCode={currentRoomCode}
        handleExit={handleWaitingViewExit}
      />
    )
  }
  
  if(view == 'hostroom') {
    return (
      <HostRoomView
        roomCode={currentRoomCode}
        players={players}
      />
    )
  }

  if(view == 'answer') {
    return (
      <AnswerView
        setAnswer={setAnswer}
        handleSendAnswer={handleSendAnswer}
      />
    )
  }
}

export default App

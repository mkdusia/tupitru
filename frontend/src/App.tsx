import './App.css';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';

import HomeRoute from './routes/HomeRoute';
import HostRoute from './routes/HostRoute';
import PlayerRoute from './routes/PlayerRoute';

function App() {
  useEffect(() => {
    const clickAudio = new Audio('/audio/clickSound.mp3');
    clickAudio.volume = 0.2;

    const handleGlobalClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      const isButton = target.closest('button');

      if (isButton) {
        clickAudio.currentTime = 0;
        clickAudio.play().catch((err) => console.log(err));
      }
    };

    document.addEventListener('click', handleGlobalClick);

    return () => {
      document.removeEventListener('click', handleGlobalClick);
    };
  }, []);
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomeRoute />} />

        <Route path="/host/:roomId?" element={<HostRoute />} />

        <Route path="/play/:roomId" element={<PlayerRoute />} />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

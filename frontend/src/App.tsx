import './App.css'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import HomeRoute from './routes/HomeRoute';
import HostRoute from './routes/HostRoute'
import PlayerRoute from './routes/PlayerRoute';

function App() {
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

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Overview from './pages/Overview';
import Patients from './pages/Patients';
import DonorPods from './pages/DonorPods';
import LiveFeed from './pages/LiveFeed';
import Settings from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/patients" element={<Patients />} />
            <Route path="/donor-pods" element={<DonorPods />} />
            <Route path="/live-feed" element={<LiveFeed />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

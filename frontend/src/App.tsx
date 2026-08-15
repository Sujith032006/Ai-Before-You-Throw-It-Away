import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import { ScanProvider } from './context/ScanContext';

// Pages
import Home from './pages/Home';
import ScanItem from './pages/ScanItem';
import DetectionResult from './pages/DetectionResult';
import Preferences from './pages/Preferences';
import Recommendations from './pages/Recommendations';
import ProjectInstructions from './pages/ProjectInstructions';
import PersonalizedGuide from './pages/PersonalizedGuide';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import TestSuite from './pages/TestSuite';
import DemoMode from './pages/DemoMode';

function App() {
  return (
    <ScanProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/home" element={<Home />} />
            <Route path="/scan" element={<ScanItem />} />
            <Route path="/result" element={<DetectionResult />} />
            <Route path="/preferences" element={<Preferences />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/instructions" element={<ProjectInstructions />} />
            <Route path="/personalized-guide" element={<PersonalizedGuide />} />
            <Route path="/history" element={<History />} />
            <Route path="/test-suite" element={<TestSuite />} />
            <Route path="/demo" element={<DemoMode />} />
            <Route path="/project/:id" element={<ProjectInstructions />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ScanProvider>
  );
}

export default App;

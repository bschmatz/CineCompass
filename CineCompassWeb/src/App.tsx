import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Onboarding } from './pages/Onboarding';
import { Home } from './pages/Home';
import { Layout } from './components/Layout';
import { SessionProvider } from './contexts/SessionContext';

function App() {
  return (
    <SessionProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/onboarding" element={<Onboarding />} />
          <Route
            path="/home"
            element={
              <Layout>
                <Home />
              </Layout>
            }
          />
          <Route path="/" element={<Navigate to="/onboarding" replace />} />
        </Routes>
      </BrowserRouter>
    </SessionProvider>
  );
}

export default App;

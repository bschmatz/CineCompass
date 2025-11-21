import { useState, useEffect } from 'react';
import { Onboarding } from './pages/Onboarding';
import { Home } from './pages/Home';
import { Layout } from './components/Layout';
import { useSession, SessionProvider } from './contexts/SessionContext';
import { MobileRestriction } from './components/MobileRestriction';

function AppContent() {
  const { hasOnboarded, isLoading } = useSession();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (!hasOnboarded) {
    return <Onboarding />;
  }

  return (
    <Layout>
      <Home />
    </Layout>
  );
}

function App() {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };

    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  if (isMobile) {
    return <MobileRestriction />;
  }

  return (
    <SessionProvider>
      <AppContent />
    </SessionProvider>
  );
}

export default App;

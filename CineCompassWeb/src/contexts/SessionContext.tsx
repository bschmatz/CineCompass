import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';

interface SessionContextType {
  ratingsInCycle: number;
  cyclesCompleted: number;
  totalRatings: number;
  isStudyComplete: boolean;
  incrementRating: () => void;
  resetCycle: () => void;
  resetSession: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

const STORAGE_KEY = 'cinecompass_session_tracking';
const RATINGS_PER_CYCLE = 15;
const REQUIRED_CYCLES = 4;

export function SessionProvider({ children }: { children: ReactNode }) {
  const [ratingsInCycle, setRatingsInCycle] = useState(0);
  const [cyclesCompleted, setCyclesCompleted] = useState(0);
  const [totalRatings, setTotalRatings] = useState(0);

  useEffect(() => {
    const savedData = localStorage.getItem(STORAGE_KEY);
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        setRatingsInCycle(parsed.ratingsInCycle || 0);
        setCyclesCompleted(parsed.cyclesCompleted || 0);
        setTotalRatings(parsed.totalRatings || 0);
      } catch (e) {
        console.error('Failed to parse session data:', e);
      }
    }
  }, []);

  useEffect(() => {
    const dataToSave = {
      ratingsInCycle,
      cyclesCompleted,
      totalRatings,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave));
  }, [ratingsInCycle, cyclesCompleted, totalRatings]);

  const isStudyComplete = cyclesCompleted >= REQUIRED_CYCLES;

  const incrementRating = () => {
    setRatingsInCycle(prev => prev + 1);
    setTotalRatings(prev => prev + 1);
  };

  const resetCycle = () => {
    setCyclesCompleted(prev => prev + 1);
    setRatingsInCycle(0);
  };

  const resetSession = () => {
    setRatingsInCycle(0);
    setCyclesCompleted(0);
    setTotalRatings(0);
    localStorage.removeItem(STORAGE_KEY);
  };

  return (
    <SessionContext.Provider
      value={{
        ratingsInCycle,
        cyclesCompleted,
        totalRatings,
        isStudyComplete,
        incrementRating,
        resetCycle,
        resetSession,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
}

export function useSession() {
  const context = useContext(SessionContext);
  if (!context) {
    throw new Error('useSession must be used within a SessionProvider');
  }
  return context;
}

export { RATINGS_PER_CYCLE, REQUIRED_CYCLES };

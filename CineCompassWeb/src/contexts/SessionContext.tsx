import { createContext, useContext, useState, useEffect, type ReactNode } from 'react';
import { api } from '../utils/api';
import { clearSession } from '../utils/auth';

interface SessionContextType {
  ratingsInCycle: number;
  cyclesCompleted: number;
  totalRatings: number;
  isStudyComplete: boolean;
  hasOnboarded: boolean;
  isLoading: boolean;
  incrementRating: () => void;
  resetCycle: () => void;
  resetSession: () => void;
  completeOnboarding: () => void;
}

const SessionContext = createContext<SessionContextType | undefined>(undefined);

const STORAGE_KEY = 'cinecompass_session_tracking';
const RATINGS_PER_CYCLE = 15;
const REQUIRED_CYCLES = 4;

export function SessionProvider({ children }: { children: ReactNode }) {
  const [ratingsInCycle, setRatingsInCycle] = useState(0);
  const [cyclesCompleted, setCyclesCompleted] = useState(0);
  const [totalRatings, setTotalRatings] = useState(0);
  const [hasOnboarded, setHasOnboarded] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkOnboardingStatus = async () => {
      try {
        const response = await api.getRecommendations(1, 1);
        setHasOnboarded(response.items.length > 0);
      } catch (error) {
        console.error('Failed to check onboarding status:', error);
        setHasOnboarded(false);
      } finally {
        setIsLoading(false);
      }
    };

    const savedData = localStorage.getItem(STORAGE_KEY);
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData);
        console.log('Loaded session data:', parsed);
        setRatingsInCycle(parsed.ratingsInCycle || 0);
        setCyclesCompleted(parsed.cyclesCompleted || 0);
        setTotalRatings(parsed.totalRatings || 0);
      } catch (e) {
        console.error('Failed to parse session data:', e);
      }
    }

    checkOnboardingStatus();
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

  const completeOnboarding = () => {
    setHasOnboarded(true);
  };

  const resetSession = () => {
    setRatingsInCycle(0);
    setCyclesCompleted(0);
    setTotalRatings(0);
    setHasOnboarded(false);
    localStorage.removeItem(STORAGE_KEY);
    clearSession();
  };

  return (
    <SessionContext.Provider
      value={{
        ratingsInCycle,
        cyclesCompleted,
        totalRatings,
        isStudyComplete,
        hasOnboarded,
        isLoading,
        incrementRating,
        resetCycle,
        resetSession,
        completeOnboarding,
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

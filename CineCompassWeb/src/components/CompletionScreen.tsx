import { useState } from 'react';
import { useSession } from '../contexts/SessionContext';
import { getSessionId } from '../utils/auth';

interface CompletionScreenProps {
  googleFormUrl?: string;
}

export function CompletionScreen({
  googleFormUrl = 'https://forms.google.com/your-form-id'
}: CompletionScreenProps) {
  const { totalRatings, cyclesCompleted, resetSession } = useSession();
  const [copied, setCopied] = useState(false);
  const sessionId = getSessionId();

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sessionId);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-950 via-purple-950 to-gray-950 px-4">
      <div className="max-w-2xl w-full">
        {/* Success Icon */}
        <div className="flex justify-center mb-8">
          <div className="w-24 h-24 bg-purple-500/20 rounded-full flex items-center justify-center border-4 border-purple-500">
            <svg
              className="w-12 h-12 text-purple-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={3}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
        </div>

        {/* Main Content */}
        <div className="bg-gray-900/60 backdrop-blur-sm rounded-2xl p-8 border border-purple-500/30 shadow-2xl">
          <h1 className="text-4xl font-bold text-white text-center mb-4">
            Study Complete!
          </h1>

          <p className="text-xl text-gray-300 text-center mb-8">
            Thank you for participating in our movie recommendation study.
          </p>

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <div className="bg-gray-800/50 rounded-xl p-4 text-center border border-gray-700">
              <div className="text-3xl font-bold text-purple-400">{totalRatings}</div>
              <div className="text-sm text-gray-400 mt-1">Movies Rated</div>
            </div>
            <div className="bg-gray-800/50 rounded-xl p-4 text-center border border-gray-700">
              <div className="text-3xl font-bold text-purple-400">{cyclesCompleted}</div>
              <div className="text-sm text-gray-400 mt-1">Cycles Completed</div>
            </div>
          </div>

          {/* Instructions */}
          <div className="bg-purple-500/10 border border-purple-500/30 rounded-xl p-6 mb-6">
            <h2 className="text-lg font-semibold text-white mb-3">Final Step</h2>
            <p className="text-gray-300 leading-relaxed">
              To complete your participation in this thesis study, please fill out the final found below.

            </p>
          </div>

          {/* Session ID */}
          <div className="bg-gray-800/50 rounded-xl p-4 mb-6 border border-gray-700">
            <label className="block text-sm text-gray-400 mb-2">Your Session ID (Required for Questionnaire)</label>
            <div className="flex items-center gap-2">
              <code className="flex-1 bg-gray-950 rounded-lg p-3 text-purple-300 font-mono text-sm border border-gray-800 overflow-hidden text-ellipsis">
                {sessionId}
              </code>
              <button
                onClick={handleCopy}
                className={`px-4 py-3 rounded-lg font-medium transition-all duration-200 ${copied
                  ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                  : 'bg-purple-500/20 text-purple-400 hover:bg-purple-500/30 border border-purple-500/50'
                  }`}
              >
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>

          {/* Google Form Button */}
          <a
            href={googleFormUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full bg-gradient-to-r from-purple-600 to-purple-500 hover:from-purple-700 hover:to-purple-600 text-white text-center font-semibold py-4 rounded-xl transition-all transform hover:scale-[1.02] shadow-lg mb-4"
          >
            Open Questionnaire
          </a>

          {/* Reset Option */}
          <button
            onClick={() => {
              if (window.confirm('Are you sure you want to reset your session? This will clear all progress.')) {
                resetSession();
                window.location.reload();
              }
            }}
            className="w-full text-gray-400 hover:text-gray-300 text-sm py-2 transition-colors"
          >
            Reset Session
          </button>
        </div>

        {/* Footer Note */}
        <p className="text-center text-gray-500 text-sm mt-6">
          After completing the questionnaire, you may close this window.
        </p>
      </div>
    </div>
  );
}

import { Monitor } from 'lucide-react';

export function MobileRestriction() {
    return (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-gray-950 p-6 text-center text-white">
            <div className="mb-6 rounded-full bg-gray-900 p-6">
                <Monitor className="h-12 w-12 text-purple-500" />
            </div>
            <h1 className="mb-4 text-2xl font-bold">Desktop Required</h1>
            <p className="max-w-md text-gray-400">
                To ensure the best experience for this study, please access this application on a computer or laptop.
            </p>
        </div>
    );
}

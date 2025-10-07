"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardNav from './DashboardNav'; // Import the new Navigation

const DashboardHeader = ({ onLogout, username }) => {
    return (
        <header className="w-full p-4 bg-gray-900/80 backdrop-blur-lg flex justify-between items-center">
             <div className="flex items-center gap-4">
                 <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-lg flex items-center justify-center font-bold text-xl">⚡</div>
                 <h1 className="text-xl font-bold text-white">
                    Welcome, <span className="text-cyan-400">{username}</span>!
                 </h1>
            </div>
            <button
                onClick={onLogout}
                className="bg-red-600 hover:bg-red-700 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
            >
                Logout
            </button>
        </header>
    );
};

export default function DashboardLayout({ children }) {
    const router = useRouter();
    const [user, setUser] = useState(null);

    useEffect(() => {
        const ensureAuth = () => {
            let token = null;
            try { token = localStorage.getItem('accessToken'); } catch {}
            if (!token && typeof document !== 'undefined') {
                const cookie = document.cookie.split('; ').find(c => c.startsWith('accessToken='));
                if (cookie) token = decodeURIComponent(cookie.split('=')[1]);
            }
            if (!token) {
                router.push('/');
                return;
            }
            const [username] = token.split(':');
            setUser({ username });
        };
        ensureAuth();
    }, [router]);

    const handleLogout = () => {
        try { localStorage.removeItem('accessToken'); } catch {}
        try { document.cookie = 'accessToken=; path=/; max-age=0'; } catch {}
        router.push('/');
    };

    if (!user) {
        return <div className="bg-[#0D0E12] min-h-screen flex items-center justify-center text-white"><p>Verifying session...</p></div>;
    }

    return (
        <div className="bg-[#0D0E12] min-h-screen text-gray-200">
            {/* The Header and Nav are now stacked vertically on top */}
            <DashboardHeader onLogout={handleLogout} username={user.username} />
            <DashboardNav />

            {/* The main content area simply takes up the rest of the space */}
            <main className="p-4 sm:p-6 md:p-8">
                {children}
            </main>
        </div>
    );
}

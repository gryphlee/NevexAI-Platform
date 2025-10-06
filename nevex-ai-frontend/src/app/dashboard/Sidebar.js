"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navLinks = [
    { name: 'Overview', href: '/dashboard' },
    { name: 'Analytics Hub', href: '/dashboard/analytics' },
    { name: 'Resource Manager', href: '/dashboard/resources' },
    { name: 'User Management', href: '/dashboard/users' },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        // This locks the sidebar to the left side of the screen
        <aside className="fixed top-0 left-0 h-full w-64 bg-gray-900/50 p-6 border-r border-cyan-400/20 z-20">
            <div className="flex items-center gap-4 mb-10">
                 <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-purple-500 rounded-lg flex items-center justify-center font-bold text-xl">⚡</div>
                 <h1 className="text-lg font-bold text-white">
                    <span className="text-cyan-400">NEVEX</span> AI
                 </h1>
            </div>
            <nav className="flex flex-col space-y-2">
                {navLinks.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                        <Link
                            key={link.name}
                            href={link.href}
                            className={`px-4 py-2 rounded-lg transition-colors text-sm font-medium ${
                                isActive
                                    ? 'bg-cyan-500/20 text-cyan-300'
                                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                            }`}
                        >
                            {link.name}
                        </Link>
                    );
                })}
            </nav>
        </aside>
    );
}

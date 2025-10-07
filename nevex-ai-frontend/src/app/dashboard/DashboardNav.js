"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navLinks = [
    { name: 'Overview', href: '/dashboard' },
    { name: 'Analytics Hub', href: '/dashboard/analytics' },
    { name: 'Risk Predictor', href: '/dashboard/predictor' }, // <-- ADD THIS
    { name: 'Resource Manager', href: '/dashboard/resources' },
    { name: 'User Management', href: '/dashboard/users' },
    { name: 'Database Admin', href: '/dashboard/database' },
];

export default function DashboardNav() {
    const pathname = usePathname();

    return (
        <div className="w-full bg-gray-900/30 border-b border-cyan-400/20 px-4 sm:px-6 md:px-8">
            <nav className="flex space-x-4">
                {navLinks.map((link) => {
                    const isActive = pathname === link.href;
                    return (
                        <Link
                            key={link.name}
                            href={link.href}
                            className={`px-3 py-3 text-sm font-medium transition-colors ${
                                isActive
                                    ? 'border-b-2 border-cyan-400 text-cyan-300'
                                    : 'text-gray-400 hover:text-white'
                            }`}
                        >
                            {link.name}
                        </Link>
                    );
                })}
            </nav>
        </div>
    );
}
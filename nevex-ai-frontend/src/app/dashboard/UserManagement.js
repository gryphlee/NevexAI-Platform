"use client";

import { useEffect, useState } from 'react';

export default function UserManagement() {
    const [users, setUsers] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);
    const [formError, setFormError] = useState('');
    const [successMessage, setSuccessMessage] = useState('');

    const fetchUsers = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/users');
            if (!response.ok) {
                throw new Error("Failed to fetch users.");
            }
            const data = await response.json();
            setUsers(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleCreateUser = async (event) => {
        event.preventDefault();
        setFormError('');
        setSuccessMessage('');
        const formData = new FormData(event.target);
        const newUser = Object.fromEntries(formData.entries());
        if (!newUser.username || !newUser.password || !newUser.role) {
            setFormError("All fields are required.");
            return;
        }
        try {
            const response = await fetch('http://127.0.0.1:8000/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify(newUser),
            });
            const result = await response.json();
            if (!response.ok) { throw new Error(result.detail || "Failed to create user."); }
            setSuccessMessage(result.message);
            event.target.reset();
            fetchUsers();
        } catch (err) {
            setFormError(err.message);
        }
    };

    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
            {/* User List Card */}
            <div className="lg:col-span-2 bg-gray-900/50 border border-purple-400/30 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4 text-purple-300">Manage Users</h3>
                {isLoading && <p className="text-gray-400">Loading users...</p>}
                {error && <p className="text-red-500">{error}</p>}
                {!isLoading && !error && (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left text-sm">
                            <thead className="border-b border-purple-400/30 text-gray-300">
                                <tr>
                                    <th className="p-3">Username</th>
                                    <th className="p-3">Role</th>
                                    <th className="p-3">Linked Student ID</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map((user) => (
                                    <tr key={user.username} className="border-b border-gray-800 hover:bg-gray-800/50">
                                        <td className="p-3 font-medium">{user.username}</td>
                                        <td className="p-3">{user.role}</td>
                                        <td className="p-3 text-gray-400">{user.student_id}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            {/* Create User Form Card */}
            <div className="bg-gray-900/50 border border-purple-400/30 rounded-lg p-6 h-fit">
                <h3 className="text-xl font-bold mb-4 text-purple-300">Create New User</h3>
                <form onSubmit={handleCreateUser} className="space-y-4">
                    <div>
                        <label className="block text-gray-400 text-sm mb-2" htmlFor="username">Username</label>
                        <input className="w-full bg-gray-800 rounded p-2 border border-gray-700 focus:outline-none focus:border-purple-500 transition-colors" type="text" name="username" id="username" />
                    </div>
                    <div>
                        <label className="block text-gray-400 text-sm mb-2" htmlFor="password">Password</label>
                        <input className="w-full bg-gray-800 rounded p-2 border border-gray-700 focus:outline-none focus:border-purple-500 transition-colors" type="password" name="password" id="password" />
                    </div>
                    <div>
                        <label className="block text-gray-400 text-sm mb-2" htmlFor="role">Role</label>
                        <select className="w-full bg-gray-800 rounded p-2 border border-gray-700 focus:outline-none focus:border-purple-500 transition-colors" name="role" id="role" defaultValue="Teacher">
                            <option value="Admin">Admin</option>
                            <option value="Teacher">Teacher</option>
                            <option value="Parent">Parent</option>
                        </select>
                    </div>
                    <button type="submit" className="w-full bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded transition-colors">
                        Create User
                    </button>
                    {formError && <p className="text-red-500 text-sm mt-2 text-center">{formError}</p>}
                    {successMessage && <p className="text-green-500 text-sm mt-2 text-center">{successMessage}</p>}
                </form>
            </div>
        </div>
    );
}
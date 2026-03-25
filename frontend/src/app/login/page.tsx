'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const { login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (searchParams.get('registered')) {
      setSuccess("Account created successfully! Please login.");
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Fetch user profile to get complete user data
      const profileRes = await fetch(`${API_BASE_URL}/api/users/profile`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      });
      
      const profileData = await profileRes.json();
      
      login(data.access_token, {
        email: profileData.email,
        user_id: profileData.user_id
      });
      
    } catch (err: any) {
      setError(err.message || "Invalid credentials");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="neural-pattern" />
      <div className="glass-card p-8 sm:p-12 max-w-md w-full relative z-10">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center mx-auto mb-4 border border-purple-500/30">
            <i className="bi bi-shield-lock-fill text-3xl text-purple-400"></i>
          </div>
          <h1 className="text-3xl font-bold gradient-text-neural mb-2">Welcome Back</h1>
          <p className="text-gray-400">Continue your fitness journey</p>
        </div>

        {success && (
          <div className="bg-green-500/10 border border-green-500/50 text-green-400 p-4 rounded-lg mb-6 text-sm">
            {success}
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-lg mb-6 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
            <input 
              type="email" 
              value={email} 
              onChange={e => setEmail(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
              placeholder="your@email.com" 
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
              placeholder="••••••••" 
              required
            />
          </div>
          
          <button 
            type="submit" 
            disabled={isLoading}
            className="glow-button w-full py-4 font-bold text-lg disabled:opacity-50"
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>

          <div className="text-center text-sm text-gray-400">
            Don't have an account? {' '}
            <Link href="/register" className="text-purple-400 hover:text-purple-300 font-semibold transition-colors">
              Register here
            </Link>
          </div>

          <Link href="/" className="block text-center text-sm text-gray-500 hover:text-white transition-colors">
            <i className="bi bi-arrow-left mr-2"></i> Back to Home
          </Link>
        </form>
      </div>
    </div>
  );
}

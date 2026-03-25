'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    weight_kg: 70,
    height_cm: 175,
    body_type: 'mesomorph',
    fitness_goals: ['strength']
  });
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'weight_kg' || name === 'height_cm' ? parseFloat(value) : value
    }));
  };

  const handleGoalChange = (goal: string) => {
    setFormData(prev => {
      const goals = prev.fitness_goals.includes(goal)
        ? prev.fitness_goals.filter(g => g !== goal)
        : [...prev.fitness_goals, goal];
      return { ...prev, fitness_goals: goals };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          weight_kg: formData.weight_kg,
          height_cm: formData.height_cm,
          body_type: formData.body_type,
          fitness_goals: formData.fitness_goals
        })
      });

      const data = await res.json();

      if (!res.ok) {
        // Handle validation errors from FastAPI (422)
        if (res.status === 422) {
          const detail = data.detail;
          if (Array.isArray(detail)) {
            setError(detail.map((d: any) => `${d.loc[d.loc.length - 1]}: ${d.msg}`).join(', '));
          } else {
            setError(detail || "Validation Error");
          }
        } else {
          throw new Error(data.detail || 'Registration failed');
        }
        return;
      }

      // Registration successful, redirect to login
      router.push('/login?registered=true');
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="neural-pattern" />
      <div className="glass-card p-8 sm:p-12 max-w-xl w-full relative z-10 my-12">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-full bg-purple-500/20 flex items-center justify-center mx-auto mb-4 border border-purple-500/30">
            <i className="bi bi-person-plus-fill text-3xl text-purple-400"></i>
          </div>
          <h1 className="text-3xl font-bold gradient-text-neural mb-2">Create Account</h1>
          <p className="text-gray-400">Join the future of fitness</p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-lg mb-6 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
              <input 
                type="email" 
                name="email"
                value={formData.email} 
                onChange={handleChange}
                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
              <input 
                type="password" 
                name="password"
                value={formData.password} 
                onChange={handleChange}
                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
                placeholder="••••••••"
                required
              />
              <p className="text-[10px] text-gray-500 mt-1">Min 8 chars, 1 uppercase, 1 number</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Confirm Password</label>
              <input 
                type="password" 
                name="confirmPassword"
                value={formData.confirmPassword} 
                onChange={handleChange}
                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
                placeholder="••••••••"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Weight (kg)</label>
              <input 
                type="number" 
                name="weight_kg"
                value={formData.weight_kg} 
                onChange={handleChange}
                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Height (cm)</label>
              <input 
                type="number" 
                name="height_cm"
                value={formData.height_cm} 
                onChange={handleChange}
                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
                required
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">Body Type</label>
              <select 
                name="body_type"
                value={formData.body_type}
                onChange={handleChange}
                className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white appearance-none focus:ring-2 focus:ring-purple-500 outline-none transition-all"
              >
                <option value="ectomorph" className="bg-[#0a0e27]">Ectomorph (Lean/Thin)</option>
                <option value="mesomorph" className="bg-[#0a0e27]">Mesomorph (Muscular/Athletic)</option>
                <option value="endomorph" className="bg-[#0a0e27]">Endomorph (Sturdy/Fuller)</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">Fitness Goals</label>
              <div className="flex flex-wrap gap-2">
                {['weight_loss', 'muscle_gain', 'strength', 'endurance', 'flexibility'].map(goal => (
                  <button
                    key={goal}
                    type="button"
                    onClick={() => handleGoalChange(goal)}
                    className={`px-4 py-2 rounded-full text-xs font-semibold transition-all ${
                      formData.fitness_goals.includes(goal)
                        ? 'bg-purple-500 text-white border-transparent'
                        : 'bg-white/5 text-gray-400 border border-white/10 hover:border-white/30'
                    }`}
                  >
                    {goal.replace('_', ' ').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="glow-button w-full py-4 text-lg font-bold disabled:opacity-50"
          >
            {isLoading ? 'Creating Account...' : 'Register Now'}
          </button>

          <div className="text-center text-sm text-gray-400">
            Already have an account? {' '}
            <Link href="/login" className="text-purple-400 hover:text-purple-300 font-semibold transition-colors">
              Login here
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

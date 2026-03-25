'use client';

import React, { useState, useEffect } from 'react';
import { 
  UserProfile, UserStatistics, NotificationPreferences,
  getProfile, updateProfile, getStatistics,
  updatePreferences, 
  getPreferences 
} from '@/lib/api-user';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function ProfilePage() {
  const { user, logout, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<UserStatistics | null>(null);
  const [prefs, setPrefs] = useState<NotificationPreferences | null>(null);
  const [editing, setEditing] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState<Partial<UserProfile>>({});

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    } else if (user) {
      loadData();
    }
  }, [user, authLoading, router]);

  async function loadData() {
    setLoading(true);
    try {
      const [p, s, r] = await Promise.all([
        getProfile(),
        getStatistics(),
        getPreferences()
      ]);
      setProfile(p);
      setFormData(p);
      setStats(s);
      setPrefs(r);
    } catch (err) {
      console.error(err);
      setMessage("Failed to load profile data.");
    } finally {
      setLoading(false);
    }
  }

  async function handleProfileUpdate(e: React.FormEvent) {
    e.preventDefault();
    try {
      const updated = await updateProfile({
        weight_kg: Number(formData.weight_kg),
        height_cm: Number(formData.height_cm),
        body_type: formData.body_type,
        fitness_goals: formData.fitness_goals
      });
      setProfile(updated);
      setEditing(false);
      setMessage("Profile updated successfully!");
      setTimeout(() => setMessage(null), 3000);
    } catch (err: any) {
      setMessage(err.message);
    }
  }

  async function handlePrefToggle(key: keyof NotificationPreferences) {
    if (!prefs) return;
    try {
      const updated = await updatePreferences({ [key]: !prefs[key] });
      setPrefs(updated);
    } catch (err: any) {
      console.error(err);
    }
  }

  if (authLoading || (loading && !profile)) {
    return (
      <div className="min-h-screen bg-[#0a0e27] flex items-center justify-center">
        <div className="spinner w-12 h-12" />
      </div>
    );
  }

  if (!profile) return <div className="p-8 text-center text-red-500">{message || "Failed to load profile"}</div>;

  return (
    <div className="min-h-screen p-4 sm:p-8 relative">
      <div className="neural-pattern" />
      <div className="max-w-4xl mx-auto space-y-8 relative z-10">
        
        {/* Header */}
        <div className="glass-card p-6 sm:p-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-gray-400 hover:text-white transition-colors">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </Link>
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white">{profile.email}</h1>
              <p className="text-gray-400 text-sm italic">Member since {new Date(profile.created_at).toLocaleDateString()}</p>
            </div>
          </div>
          <div className="flex gap-3">
             <button 
                onClick={() => setEditing(!editing)}
                className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm font-medium text-gray-300 hover:text-white transition-all capitalize"
              >
                {editing ? 'Cancel' : 'Edit Profile'}
              </button>
              <button 
                onClick={() => logout()}
                className="px-4 py-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-sm font-medium text-red-400 hover:text-red-300 transition-all"
              >
                Logout
              </button>
          </div>
        </div>

        {message && (
          <div className="bg-blue-500/10 border border-blue-500/50 text-blue-400 p-4 rounded-lg animate-fade-in transition-all">
            {message}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Profile Details */}
          <div className="glass-card p-6 sm:p-8">
            <h2 className="text-xl font-bold mb-6 gradient-text-neural">Physical Profile</h2>
            {editing ? (
              <form onSubmit={handleProfileUpdate} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Weight (kg)</label>
                  <input 
                    type="number" 
                    value={formData.weight_kg || ''} 
                    onChange={e => setFormData({...formData, weight_kg: parseFloat(e.target.value)})}
                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Height (cm)</label>
                  <input 
                    type="number" 
                    value={formData.height_cm || ''} 
                    onChange={e => setFormData({...formData, height_cm: parseFloat(e.target.value)})}
                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-2">Body Type</label>
                  <select 
                    value={formData.body_type || ''} 
                    onChange={e => setFormData({...formData, body_type: e.target.value})}
                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white appearance-none focus:ring-2 focus:ring-purple-500 outline-none transition-all"
                  >
                    <option value="ectomorph" className="bg-[#0a0e27]">Ectomorph</option>
                    <option value="mesomorph" className="bg-[#0a0e27]">Mesomorph</option>
                    <option value="endomorph" className="bg-[#0a0e27]">Endomorph</option>
                  </select>
                </div>
                <button 
                  type="submit" 
                  className="glow-button w-full py-3 font-bold"
                >
                  Save Changes
                </button>
              </form>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between border-b border-white/5 pb-3">
                  <span className="text-gray-500">Weight</span>
                  <span className="text-white font-medium">{profile.weight_kg ? `${profile.weight_kg} kg` : '-'}</span>
                </div>
                <div className="flex justify-between border-b border-white/5 pb-3">
                  <span className="text-gray-500">Height</span>
                  <span className="text-white font-medium">{profile.height_cm ? `${profile.height_cm} cm` : '-'}</span>
                </div>
                <div className="flex justify-between border-b border-white/5 pb-3">
                  <span className="text-gray-500">Body Type</span>
                  <span className="text-white font-medium capitalize">{profile.body_type || '-'}</span>
                </div>
                <div className="flex justify-between pt-2">
                  <span className="text-gray-500">Fitness Goals</span>
                  <div className="flex flex-wrap justify-end gap-2 max-w-[60%]">
                    {profile.fitness_goals?.map(goal => (
                      <span key={goal} className="px-2 py-1 rounded-md bg-purple-500/20 text-purple-400 text-xs font-semibold border border-purple-500/30">
                        {goal.replace('_', ' ').toUpperCase()}
                      </span>
                    )) || '-'}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Stats & Preferences */}
          <div className="space-y-8">
             <div className="glass-card p-6 sm:p-8">
                <h2 className="text-xl font-bold mb-6 gradient-text-neural">Your Progress</h2>
                {stats ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white/5 border border-white/10 p-4 rounded-xl text-center group hover:bg-white/10 transition-all">
                      <div className="text-2xl font-black text-purple-400 group-hover:scale-110 transition-transform">{stats.current_streak}</div>
                      <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mt-1">Current Streak</div>
                    </div>
                    <div className="bg-white/5 border border-white/10 p-4 rounded-xl text-center group hover:bg-white/10 transition-all">
                      <div className="text-2xl font-black text-blue-400 group-hover:scale-110 transition-transform">{stats.total_workouts}</div>
                      <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mt-1">Workouts</div>
                    </div>
                    <div className="bg-white/5 border border-white/10 p-4 rounded-xl text-center group hover:bg-white/10 transition-all">
                      <div className="text-2xl font-black text-pink-400 group-hover:scale-110 transition-transform">{stats.total_reps}</div>
                      <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mt-1">Total Reps</div>
                    </div>
                    <div className="bg-white/5 border border-white/10 p-4 rounded-xl text-center group hover:bg-white/10 transition-all">
                      <div className="text-2xl font-black text-cyan-400 group-hover:scale-110 transition-transform">{Math.round(stats.average_form_score)}%</div>
                      <div className="text-[10px] uppercase tracking-widest text-gray-500 font-bold mt-1">Avg Form</div>
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 italic text-center">No progress data available yet.</p>
                )}
             </div>

             <div className="glass-card p-6 sm:p-8">
                <h2 className="text-xl font-bold mb-6 gradient-text-neural">Notifications</h2>
                {prefs ? (
                  <div className="space-y-5">
                    <div className="flex items-center justify-between group">
                      <span className="text-gray-400 group-hover:text-white transition-colors">Email Updates</span>
                      <button 
                        onClick={() => handlePrefToggle('email_notifications')}
                        className={`w-12 h-6 flex items-center rounded-full transition-all duration-300 ${prefs.email_notifications ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-white/10'}`}
                      >
                         <div className={`w-5 h-5 bg-white rounded-full shadow-lg transform transition-transform duration-300 ${prefs.email_notifications ? 'translate-x-6' : 'translate-x-1'}`} />
                      </button>
                    </div>
                    <div className="flex items-center justify-between group">
                      <span className="text-gray-400 group-hover:text-white transition-colors">Form Alerts</span>
                      <button 
                        onClick={() => handlePrefToggle('push_notifications')}
                        className={`w-12 h-6 flex items-center rounded-full transition-all duration-300 ${prefs.push_notifications ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-white/10'}`}
                      >
                         <div className={`w-5 h-5 bg-white rounded-full shadow-lg transform transition-transform duration-300 ${prefs.push_notifications ? 'translate-x-6' : 'translate-x-1'}`} />
                      </button>
                    </div>
                    <div className="flex items-center justify-between group">
                      <span className="text-gray-400 group-hover:text-white transition-colors">Workout Reminders</span>
                      <button 
                        onClick={() => handlePrefToggle('workout_residues')}
                        className={`w-12 h-6 flex items-center rounded-full transition-all duration-300 ${prefs.workout_residues ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-white/10'}`}
                      >
                         <div className={`w-5 h-5 bg-white rounded-full shadow-lg transform transition-transform duration-300 ${prefs.workout_residues ? 'translate-x-6' : 'translate-x-1'}`} />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex justify-center py-4">
                    <div className="spinner w-6 h-6 border-2" />
                  </div>
                )}
             </div>
          </div>

        </div>
      </div>
    </div>
  );
}

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { sendMessage, ChatMessage } from '@/lib/api-chat';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { useRouter } from 'next/navigation';

export default function ChatPage() {
  const { user, logout, isLoading: authLoading } = useAuth();
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: 'assistant', content: "Hello! I'm your AI Gym Coach. How can I help you with your fitness journey today?" }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: ChatMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendMessage(userMsg.content, messages);
      const aiMsg: ChatMessage = { role: 'assistant', content: response };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
      console.error(error);
      const errorMsg: ChatMessage = { role: 'assistant', content: "Sorry, I'm having trouble connecting right now." };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
  };

  if (authLoading || !user) {
    return (
      <div className="min-h-screen bg-[#0a0e27] flex items-center justify-center">
        <div className="spinner w-12 h-12" />
      </div>
    );
  }

  return (
    <>
      <div className="neural-pattern" />
      <div className="flex flex-col h-screen relative">
        {/* Header */}
        <header className="glass-card border-b border-white/10 p-4 sm:p-6 relative z-10">
          <div className="max-w-5xl mx-auto flex justify-between items-center">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-gray-400 hover:text-white transition-colors">
                <i className="bi bi-arrow-left text-2xl"></i>
              </Link>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold gradient-text-neural">AI Coach Chat</h1>
                <p className="text-xs sm:text-sm text-gray-400 hidden sm:block">Your personal fitness assistant</p>
              </div>
            </div>
            <button 
              onClick={handleLogout} 
              className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-sm font-medium text-gray-300 hover:text-white transition-all"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 relative z-10">
          <div className="max-w-4xl mx-auto space-y-6">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex gap-3 max-w-[85%] sm:max-w-[75%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  {/* Avatar */}
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                    msg.role === 'user' 
                      ? 'bg-gradient-to-br from-purple-500 to-pink-500' 
                      : 'bg-gradient-to-br from-cyan-500 to-blue-500'
                  }`}>
                    {msg.role === 'user' ? (
                      <i className="bi bi-person-fill text-xl text-white"></i>
                    ) : (
                      <i className="bi bi-robot text-xl text-white"></i>
                    )}
                  </div>
                  
                  {/* Message Bubble */}
                  <div className={`glass-card p-4 ${
                    msg.role === 'user' 
                      ? 'bg-gradient-to-br from-purple-500/20 to-pink-500/20 border-purple-500/30' 
                      : 'bg-white/5 border-white/10'
                  }`}>
                    <div className="text-white whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex gap-3 max-w-[75%]">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center flex-shrink-0">
                    <i className="bi bi-robot text-xl text-white"></i>
                  </div>
                  <div className="glass-card p-4 bg-white/5 border-white/10">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="glass-card border-t border-white/10 p-4 sm:p-6 relative z-10">
          <form onSubmit={handleSend} className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about workouts, form, nutrition, or motivation..."
                className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="glow-button px-6 py-3 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <span className="hidden sm:inline">Send</span>
                <i className="bi bi-send-fill text-lg"></i>
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-3 text-center">
              AI responses are generated and may not always be accurate. Consult professionals for medical advice.
            </p>
          </form>
        </div>
      </div>
    </>
  );
}

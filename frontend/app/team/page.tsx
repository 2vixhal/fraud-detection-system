'use client';

import { useEffect, useState } from 'react';
import { Shield, ArrowLeft, Code2, Layout, BrainCircuit, Users, GraduationCap } from 'lucide-react';
import Link from 'next/link';

const team = [
  {
    name: 'Vishal Suthar',
    role: 'Backend Developer',
    icon: <Code2 className="w-6 h-6" />,
    color: 'from-blue-500 to-cyan-500',
    border: 'border-blue-500/30',
    glow: 'shadow-blue-500/20',
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
    description: 'FastAPI, Database Architecture & System Integration',
  },
  {
    name: 'Harsh Nayan',
    role: 'Frontend Developer',
    icon: <Layout className="w-6 h-6" />,
    color: 'from-purple-500 to-pink-500',
    border: 'border-purple-500/30',
    glow: 'shadow-purple-500/20',
    bg: 'bg-purple-500/10',
    text: 'text-purple-400',
    description: 'Next.js, React & UI/UX Design',
  },
  {
    name: 'Devansh Singh',
    role: 'ML Expert',
    icon: <BrainCircuit className="w-6 h-6" />,
    color: 'from-emerald-500 to-teal-500',
    border: 'border-emerald-500/30',
    glow: 'shadow-emerald-500/20',
    bg: 'bg-emerald-500/10',
    text: 'text-emerald-400',
    description: 'XGBoost, Quantum SVM & Ensemble Models',
  },
  {
    name: 'Anuj Kumar',
    role: 'Team Member',
    icon: <Users className="w-6 h-6" />,
    color: 'from-amber-500 to-orange-500',
    border: 'border-amber-500/30',
    glow: 'shadow-amber-500/20',
    bg: 'bg-amber-500/10',
    text: 'text-amber-400',
    description: 'Research, Testing & Documentation',
  },
];

export default function TeamPage() {
  const [darkMode, setDarkMode] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem('darkMode');
    if (saved === 'true') {
      setDarkMode(true);
      document.documentElement.classList.add('dark');
    }
  }, []);

  if (!mounted) return null;

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-slate-950 dark:to-indigo-950 transition-colors duration-500">
      {/* Back Navigation */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl bg-white/70 dark:bg-gray-900/70 border-b border-border/50">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link
            href="/"
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-blue-500" />
            <span className="text-sm font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
              FraudShield AI
            </span>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-16 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 shadow-xl shadow-blue-500/25 mb-6">
            <Users className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl md:text-5xl font-black mb-3 bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 dark:from-white dark:via-blue-200 dark:to-indigo-200 bg-clip-text text-transparent">
            Meet the Team
          </h1>
          <p className="text-muted-foreground max-w-lg mx-auto">
            The people behind the Quantum-Classical Hybrid Fraud Detection System
          </p>
        </div>

        {/* Team Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
          {team.map((member, idx) => (
            <div
              key={member.name}
              className={`group relative rounded-2xl border ${member.border} bg-card p-6 shadow-lg ${member.glow} hover:shadow-xl transition-all duration-500 animate-slide-up`}
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              {/* Gradient accent line */}
              <div className={`absolute top-0 left-6 right-6 h-1 rounded-b-full bg-gradient-to-r ${member.color} opacity-60 group-hover:opacity-100 transition-opacity`} />

              <div className="flex items-start gap-4 mt-2">
                <div className={`shrink-0 w-14 h-14 rounded-xl ${member.bg} flex items-center justify-center ${member.text} group-hover:scale-110 transition-transform duration-300`}>
                  {member.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-xl font-bold text-foreground">{member.name}</h3>
                  <p className={`text-sm font-semibold ${member.text} mt-0.5`}>{member.role}</p>
                  <p className="text-xs text-muted-foreground mt-2 leading-relaxed">{member.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Guidance Section */}
        <div className="relative rounded-2xl border border-indigo-500/20 bg-gradient-to-br from-indigo-500/5 via-purple-500/5 to-blue-500/5 p-8 text-center shadow-lg shadow-indigo-500/10 animate-fade-in">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
          </div>

          <div className="mt-4">
            <p className="text-xs uppercase tracking-widest text-muted-foreground font-semibold mb-3">
              Under the Guidance of
            </p>
            <h2 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
              Ms. Sushma A Shirke
            </h2>
            <p className="text-sm text-muted-foreground mt-2">Project Guide & Mentor</p>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 pb-6 space-y-2">
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <Shield className="w-3.5 h-3.5" />
            <span>FraudShield AI v2.0</span>
            <span className="text-border">|</span>
            <span>Quantum-Classical Hybrid ML</span>
            <span className="text-border">|</span>
            <span>BE Project 2026</span>
          </div>
        </div>
      </div>
    </main>
  );
}

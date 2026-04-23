'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { predictFraud, type TransactionInput, type PredictionResponse } from '@/lib/api';
import {
  AlertCircle, CreditCard, TrendingUp, Shield, Clock,
  Sun, Moon, Zap, Brain, Cpu, Activity, ChevronRight,
  Globe, MapPin, User, DollarSign, ShoppingBag, Briefcase
} from 'lucide-react';

const MERCHANTS = [
  'Walmart', 'Amazon', 'Target', 'Costco', 'Shell', 'Chevron',
  'Starbucks', "McDonald's", 'Subway', 'Best Buy', 'Home Depot',
  'Apple Store', 'Nike', 'Uber', 'Netflix', 'Spotify',
  'Zara', 'IKEA', 'Whole Foods', 'Unknown'
];

const CATEGORIES = [
  { value: 'grocery_pos', label: 'Grocery Store' },
  { value: 'gas_transport', label: 'Gas & Transportation' },
  { value: 'shopping_net', label: 'Online Shopping' },
  { value: 'shopping_pos', label: 'In-Store Shopping' },
  { value: 'food_dining', label: 'Food & Dining' },
  { value: 'entertainment', label: 'Entertainment' },
  { value: 'personal_care', label: 'Personal Care' },
  { value: 'health_fitness', label: 'Health & Fitness' },
  { value: 'travel', label: 'Travel' },
  { value: 'misc_pos', label: 'Miscellaneous (In-Store)' },
  { value: 'misc_net', label: 'Miscellaneous (Online)' },
  { value: 'home', label: 'Home & Garden' },
];

const JOBS = [
  'Student', 'Engineer', 'Teacher', 'Healthcare', 'Sales',
  'Retail', 'Manager', 'Technician', 'Driver',
  'Consultant', 'Self-employed', 'Other'
];

const COUNTRIES = [
  'United States', 'India', 'United Kingdom', 'Canada',
  'Australia', 'Germany', 'France', 'Japan',
  'Brazil', 'Mexico', 'Singapore', 'UAE'
];

interface CityOption {
  city: string;
  state: string;
  country: string;
}

const CITIES: CityOption[] = [
  { city: 'New York', state: 'NY', country: 'United States' },
  { city: 'Los Angeles', state: 'CA', country: 'United States' },
  { city: 'Chicago', state: 'IL', country: 'United States' },
  { city: 'Houston', state: 'TX', country: 'United States' },
  { city: 'Phoenix', state: 'AZ', country: 'United States' },
  { city: 'Philadelphia', state: 'PA', country: 'United States' },
  { city: 'San Antonio', state: 'TX', country: 'United States' },
  { city: 'San Diego', state: 'CA', country: 'United States' },
  { city: 'Dallas', state: 'TX', country: 'United States' },
  { city: 'San Jose', state: 'CA', country: 'United States' },
  { city: 'Austin', state: 'TX', country: 'United States' },
  { city: 'San Francisco', state: 'CA', country: 'United States' },
  { city: 'Seattle', state: 'WA', country: 'United States' },
  { city: 'Denver', state: 'CO', country: 'United States' },
  { city: 'Boston', state: 'MA', country: 'United States' },
  { city: 'Miami', state: 'FL', country: 'United States' },
  { city: 'Atlanta', state: 'GA', country: 'United States' },
  { city: 'Detroit', state: 'MI', country: 'United States' },
  { city: 'Las Vegas', state: 'NV', country: 'United States' },
  { city: 'Portland', state: 'OR', country: 'United States' },
  { city: 'Nashville', state: 'TN', country: 'United States' },
  { city: 'Baltimore', state: 'MD', country: 'United States' },
  { city: 'Sacramento', state: 'CA', country: 'United States' },
  { city: 'Kansas City', state: 'MO', country: 'United States' },
  { city: 'Salt Lake City', state: 'UT', country: 'United States' },
  { city: 'Tampa', state: 'FL', country: 'United States' },
  { city: 'Orlando', state: 'FL', country: 'United States' },
  { city: 'Pittsburgh', state: 'PA', country: 'United States' },
  { city: 'Minneapolis', state: 'MN', country: 'United States' },
  { city: 'New Orleans', state: 'LA', country: 'United States' },
  { city: 'Mumbai', state: 'IN', country: 'India' },
  { city: 'Delhi', state: 'IN', country: 'India' },
  { city: 'Bangalore', state: 'IN', country: 'India' },
  { city: 'London', state: 'UK', country: 'United Kingdom' },
  { city: 'Toronto', state: 'CA', country: 'Canada' },
  { city: 'Sydney', state: 'AU', country: 'Australia' },
  { city: 'Tokyo', state: 'JP', country: 'Japan' },
  { city: 'Berlin', state: 'DE', country: 'Germany' },
  { city: 'Paris', state: 'FR', country: 'France' },
  { city: 'Dubai', state: 'AE', country: 'UAE' },
  { city: 'Singapore', state: 'SG', country: 'Singapore' },
  { city: 'Mexico City', state: 'MX', country: 'Mexico' },
  { city: 'São Paulo', state: 'BR', country: 'Brazil' },
];

interface PresetTransaction {
  id: string;
  name: string;
  description: string;
  expected_risk: string;
  data: Partial<TransactionInput>;
}

export default function Home() {
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'form' | 'presets'>('form');
  const [presets, setPresets] = useState<PresetTransaction[]>([]);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [country, setCountry] = useState('United States');
  const [customCity, setCustomCity] = useState('');
  const [transactionCountry, setTransactionCountry] = useState('United States');
  const [transactionCustomCity, setTransactionCustomCity] = useState('');

  const [formData, setFormData] = useState<TransactionInput>({
    amount: 0,
    merchant: '',
    category: '',
    date: new Date().toISOString().split('T')[0],
    time: new Date().toTimeString().slice(0, 5),
    age: 25,
    gender: 'M',
    job: '',
    customer_city: '',
    customer_state: '',
    transaction_city: '',
    transaction_state: '',
  });

  useEffect(() => {
    const saved = localStorage.getItem('darkMode');
    if (saved === 'true') {
      setDarkMode(true);
      document.documentElement.classList.add('dark');
    }
    fetchPresets();
  }, []);

  const toggleDarkMode = () => {
    const next = !darkMode;
    setDarkMode(next);
    localStorage.setItem('darkMode', String(next));
    if (next) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const fetchPresets = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/presets`);
      const data = await res.json();
      setPresets(data.presets || []);
    } catch {
      setPresets([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    setAnalysisStep(1);

    const steps = [1, 2, 3, 4];
    for (const step of steps) {
      setAnalysisStep(step);
      await new Promise(r => setTimeout(r, step === 3 ? 1500 : 800));
    }

    try {
      const response = await predictFraud(formData);
      setResult(response);
      setAnalysisStep(5);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to connect to backend. Make sure the server is running on port 8000.');
      setAnalysisStep(0);
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (preset: PresetTransaction) => {
    const d = preset.data;
    setFormData({
      amount: d.amount || 0,
      merchant: d.merchant || '',
      category: d.category || '',
      date: d.date || new Date().toISOString().split('T')[0],
      time: d.time || '12:00',
      age: d.age || 25,
      gender: (d.gender as 'M' | 'F') || 'M',
      job: d.job || '',
      customer_city: d.customer_city || '',
      customer_state: d.customer_state || '',
      transaction_city: d.transaction_city || '',
      transaction_state: d.transaction_state || '',
    });
    setResult(null);
    setError(null);
    setActiveTab('form');
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'LOW': return 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10';
      case 'MEDIUM': return 'text-amber-400 border-amber-500/50 bg-amber-500/10';
      case 'HIGH': return 'text-orange-400 border-orange-500/50 bg-orange-500/10';
      case 'CRITICAL': return 'text-red-400 border-red-500/50 bg-red-500/10';
      default: return 'text-gray-400 border-gray-500/50 bg-gray-500/10';
    }
  };

  const getRiskBgGradient = (level: string) => {
    switch (level) {
      case 'LOW': return 'from-emerald-500/20 to-green-500/10';
      case 'MEDIUM': return 'from-amber-500/20 to-yellow-500/10';
      case 'HIGH': return 'from-orange-500/20 to-red-500/10';
      case 'CRITICAL': return 'from-red-500/30 to-rose-500/20';
      default: return 'from-gray-500/20 to-gray-500/10';
    }
  };

  const getScoreColor = (score: number) => {
    if (score < 25) return 'text-emerald-500';
    if (score < 55) return 'text-amber-500';
    if (score < 80) return 'text-orange-500';
    return 'text-red-500';
  };

  const getModelIcon = (name: string) => {
    switch (name) {
      case 'classical': return <Cpu className="w-4 h-4" />;
      case 'quantum': return <Zap className="w-4 h-4" />;
      case 'ensemble': return <Brain className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  const getModelLabel = (name: string) => {
    switch (name) {
      case 'classical': return 'XGBoost (Classical)';
      case 'quantum': return 'QSVM (Quantum)';
      case 'ensemble': return 'Hybrid Ensemble';
      default: return name;
    }
  };

  const analysisSteps = [
    { label: 'Preprocessing features...', icon: <Cpu className="w-4 h-4" /> },
    { label: 'Running XGBoost classifier...', icon: <Brain className="w-4 h-4" /> },
    { label: 'Computing quantum kernel (QSVM)...', icon: <Zap className="w-4 h-4" /> },
    { label: 'Combining ensemble predictions...', icon: <Activity className="w-4 h-4" /> },
  ];

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-950 dark:via-slate-950 dark:to-indigo-950 transition-colors duration-500">
      {/* Top Navigation Bar */}
      <nav className="sticky top-0 z-50 glass-effect border-b border-border/50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Shield className="w-8 h-8 text-blue-500" />
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse" />
            </div>
            <div>
              <h1 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
                FraudShield AI
              </h1>
              <p className="text-[10px] text-muted-foreground font-medium tracking-wider uppercase">
                Quantum-Classical Hybrid Detection
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 text-xs text-muted-foreground">
              <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                System Online
              </div>
            </div>
            <Button
              variant="outline"
              size="icon"
              onClick={toggleDarkMode}
              className="rounded-full w-9 h-9 border-border/50"
            >
              {darkMode ? <Sun className="w-4 h-4 text-yellow-500" /> : <Moon className="w-4 h-4 text-slate-700" />}
            </Button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto p-4 md:p-6">
        {/* Hero Section */}
        <div className="text-center mb-8 pt-4">
          <h2 className="text-3xl md:text-4xl font-bold mb-3 bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 dark:from-white dark:via-blue-200 dark:to-indigo-200 bg-clip-text text-transparent">
            Real-Time Fraud Detection
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-sm md:text-base">
            Powered by hybrid quantum-classical machine learning. Enter transaction details
            to get instant fraud risk analysis using XGBoost and Quantum SVM ensemble.
          </p>
          <div className="flex items-center justify-center gap-6 mt-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-blue-500" />
              <span>XGBoost Classical</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Zap className="w-3.5 h-3.5 text-purple-500" />
              <span>Quantum SVM (Qiskit)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Brain className="w-3.5 h-3.5 text-indigo-500" />
              <span>Weighted Ensemble</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Left Panel - Input (3 cols) */}
          <div className="lg:col-span-3 space-y-4">
            {/* Tab Switcher */}
            <div className="flex gap-2 p-1 rounded-xl bg-muted/50">
              <button
                onClick={() => setActiveTab('form')}
                className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                  activeTab === 'form'
                    ? 'bg-background shadow-sm text-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <CreditCard className="w-4 h-4 inline mr-2" />
                Transaction Form
              </button>
              <button
                onClick={() => setActiveTab('presets')}
                className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-all ${
                  activeTab === 'presets'
                    ? 'bg-background shadow-sm text-foreground'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <Zap className="w-4 h-4 inline mr-2" />
                Test Scenarios ({presets.length})
              </button>
            </div>

            {activeTab === 'presets' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 animate-fade-in">
                {presets.map((preset) => (
                  <Card
                    key={preset.id}
                    className="cursor-pointer hover:shadow-lg hover:border-primary/50 transition-all duration-300 group"
                    onClick={() => loadPreset(preset)}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h4 className="font-semibold text-sm group-hover:text-primary transition-colors">
                            {preset.name}
                          </h4>
                          <p className="text-xs text-muted-foreground mt-1">
                            {preset.description}
                          </p>
                          <div className="mt-2">
                            <span className={`text-xs font-mono px-2 py-0.5 rounded-full ${
                              preset.expected_risk.includes('LOW') ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-400' :
                              preset.expected_risk.includes('MEDIUM') ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-400' :
                              preset.expected_risk.includes('HIGH') ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/50 dark:text-orange-400' :
                              'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-400'
                            }`}>
                              {preset.expected_risk}
                            </span>
                          </div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                      </div>
                    </CardContent>
                  </Card>
                ))}
                {presets.length === 0 && (
                  <div className="col-span-2 text-center py-8 text-muted-foreground">
                    <p className="text-sm">Start the backend server to load test scenarios</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'form' && (
              <Card className="shadow-xl border-border/50 animate-fade-in">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <CreditCard className="w-5 h-5 text-primary" />
                    Transaction Details
                  </CardTitle>
                  <CardDescription>
                    Enter the transaction information to analyze for potential fraud
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-5">
                    {/* Amount & Merchant Row */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="amount" className="flex items-center gap-1.5 mb-1.5">
                          <DollarSign className="w-3.5 h-3.5 text-muted-foreground" />
                          Amount (USD)
                        </Label>
                        <Input
                          id="amount"
                          type="number"
                          step="0.01"
                          min="0.01"
                          placeholder="0.00"
                          value={formData.amount || ''}
                          onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                          className="text-lg font-semibold"
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="merchant" className="flex items-center gap-1.5 mb-1.5">
                          <ShoppingBag className="w-3.5 h-3.5 text-muted-foreground" />
                          Merchant
                        </Label>
                        <Select value={formData.merchant} onValueChange={(v) => setFormData({ ...formData, merchant: v })}>
                          <SelectTrigger><SelectValue placeholder="Select merchant" /></SelectTrigger>
                          <SelectContent>
                            {MERCHANTS.map((m) => (
                              <SelectItem key={m} value={m}>{m}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {/* Category */}
                    <div>
                      <Label htmlFor="category" className="mb-1.5 block">Category</Label>
                      <Select value={formData.category} onValueChange={(v) => setFormData({ ...formData, category: v })}>
                        <SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger>
                        <SelectContent>
                          {CATEGORIES.map((c) => (
                            <SelectItem key={c.value} value={c.value}>{c.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {/* Date & Time */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="date" className="flex items-center gap-1.5 mb-1.5">
                          <Clock className="w-3.5 h-3.5 text-muted-foreground" />
                          Date
                        </Label>
                        <Input
                          id="date" type="date" value={formData.date}
                          onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="time" className="mb-1.5 block">Time</Label>
                        <Input
                          id="time" type="time" value={formData.time}
                          onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                          required
                        />
                      </div>
                    </div>

                    {/* Customer Info */}
                    <div className="grid grid-cols-3 gap-4">
                      <div>
                        <Label htmlFor="age" className="flex items-center gap-1.5 mb-1.5">
                          <User className="w-3.5 h-3.5 text-muted-foreground" />
                          Age
                        </Label>
                        <Input
                          id="age" type="number" min="18" max="100"
                          value={formData.age}
                          onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) || 18 })}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor="gender" className="mb-1.5 block">Gender</Label>
                        <Select value={formData.gender} onValueChange={(v: any) => setFormData({ ...formData, gender: v })}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="M">Male</SelectItem>
                            <SelectItem value="F">Female</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label htmlFor="job" className="flex items-center gap-1.5 mb-1.5">
                          <Briefcase className="w-3.5 h-3.5 text-muted-foreground" />
                          Occupation
                        </Label>
                        <Select value={formData.job} onValueChange={(v) => setFormData({ ...formData, job: v })}>
                          <SelectTrigger><SelectValue placeholder="Job" /></SelectTrigger>
                          <SelectContent>
                            {JOBS.map((j) => (
                              <SelectItem key={j} value={j}>{j}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {/* Customer Location */}
                    <div className="p-4 rounded-lg bg-muted/30 space-y-3">
                      <Label className="flex items-center gap-1.5 text-sm font-semibold">
                        <MapPin className="w-3.5 h-3.5 text-blue-500" />
                        Customer Home Location
                      </Label>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label className="text-xs text-muted-foreground mb-1 block">Country</Label>
                          <Select value={country} onValueChange={(v) => setCountry(v)}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                              {COUNTRIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label className="text-xs text-muted-foreground mb-1 block">City</Label>
                          <Select value={formData.customer_city} onValueChange={(v) => {
                            const loc = CITIES.find(c => c.city === v);
                            setFormData({ ...formData, customer_city: v, customer_state: loc?.state || '' });
                          }}>
                            <SelectTrigger><SelectValue placeholder="Select city" /></SelectTrigger>
                            <SelectContent>
                              {CITIES.map((c) => (
                                <SelectItem key={`${c.city}-${c.state}`} value={c.city}>
                                  {c.city}, {c.state}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div>
                        <Label className="text-xs text-muted-foreground mb-1 block">Or type custom city name</Label>
                        <Input
                          placeholder="Enter city name (optional)"
                          value={customCity}
                          onChange={(e) => {
                            setCustomCity(e.target.value);
                            if (e.target.value) {
                              setFormData({ ...formData, customer_city: e.target.value, customer_state: country === 'United States' ? 'US' : country.slice(0,2).toUpperCase() });
                            }
                          }}
                          className="text-sm"
                        />
                      </div>
                    </div>

                    {/* Transaction Location */}
                    <div className="p-4 rounded-lg bg-muted/30 space-y-3">
                      <Label className="flex items-center gap-1.5 text-sm font-semibold">
                        <Globe className="w-3.5 h-3.5 text-purple-500" />
                        Transaction Location
                      </Label>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label className="text-xs text-muted-foreground mb-1 block">Country</Label>
                          <Select value={transactionCountry} onValueChange={(v) => setTransactionCountry(v)}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                              {COUNTRIES.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label className="text-xs text-muted-foreground mb-1 block">City</Label>
                          <Select value={formData.transaction_city} onValueChange={(v) => {
                            const loc = CITIES.find(c => c.city === v);
                            setFormData({ ...formData, transaction_city: v, transaction_state: loc?.state || '' });
                          }}>
                            <SelectTrigger><SelectValue placeholder="Select city" /></SelectTrigger>
                            <SelectContent>
                              {CITIES.map((c) => (
                                <SelectItem key={`t-${c.city}-${c.state}`} value={c.city}>
                                  {c.city}, {c.state}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div>
                        <Label className="text-xs text-muted-foreground mb-1 block">Or type custom city name</Label>
                        <Input
                          placeholder="Enter city name (optional)"
                          value={transactionCustomCity}
                          onChange={(e) => {
                            setTransactionCustomCity(e.target.value);
                            if (e.target.value) {
                              setFormData({ ...formData, transaction_city: e.target.value, transaction_state: transactionCountry === 'United States' ? 'US' : transactionCountry.slice(0,2).toUpperCase() });
                            }
                          }}
                          className="text-sm"
                        />
                      </div>
                    </div>

                    {/* Submit */}
                    <Button
                      type="submit"
                      className="w-full h-12 text-base font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg shadow-blue-500/25 transition-all duration-300"
                      size="lg"
                      disabled={loading}
                    >
                      {loading ? (
                        <div className="flex items-center gap-2">
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Analyzing Transaction...
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <Shield className="w-5 h-5" />
                          Analyze for Fraud
                        </div>
                      )}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Right Panel - Results (2 cols) */}
          <div className="lg:col-span-2 space-y-4">
            <Card className="shadow-xl border-border/50 min-h-[600px]">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <TrendingUp className="w-5 h-5 text-primary" />
                  Analysis Results
                </CardTitle>
                <CardDescription>
                  AI-powered hybrid quantum-classical fraud analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Loading Animation */}
                {loading && (
                  <div className="space-y-4 animate-fade-in">
                    <div className="text-center py-4">
                      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center animate-pulse-glow">
                        <Zap className="w-8 h-8 text-white" />
                      </div>
                      <p className="text-sm font-medium text-muted-foreground">Running Analysis Pipeline</p>
                    </div>
                    <div className="space-y-3">
                      {analysisSteps.map((step, idx) => (
                        <div
                          key={idx}
                          className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-500 ${
                            analysisStep > idx + 1
                              ? 'bg-emerald-500/10 border border-emerald-500/30'
                              : analysisStep === idx + 1
                              ? 'bg-blue-500/10 border border-blue-500/30'
                              : 'bg-muted/30 border border-transparent'
                          }`}
                        >
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center transition-colors ${
                            analysisStep > idx + 1
                              ? 'bg-emerald-500 text-white'
                              : analysisStep === idx + 1
                              ? 'bg-blue-500 text-white animate-pulse'
                              : 'bg-muted text-muted-foreground'
                          }`}>
                            {analysisStep > idx + 1 ? '✓' : step.icon}
                          </div>
                          <span className={`text-sm ${
                            analysisStep > idx + 1 ? 'text-emerald-600 dark:text-emerald-400' :
                            analysisStep === idx + 1 ? 'text-blue-600 dark:text-blue-400 font-medium' :
                            'text-muted-foreground'
                          }`}>
                            {step.label}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Error */}
                {error && (
                  <div className="bg-red-500/10 border border-red-500/30 text-red-600 dark:text-red-400 p-4 rounded-lg animate-fade-in">
                    <div className="flex items-center gap-2 mb-1">
                      <AlertCircle className="w-4 h-4" />
                      <span className="font-semibold text-sm">Error</span>
                    </div>
                    <p className="text-sm">{error}</p>
                  </div>
                )}

                {/* Empty State */}
                {!result && !error && !loading && (
                  <div className="text-center py-16 text-muted-foreground animate-fade-in">
                    <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-muted/50 flex items-center justify-center">
                      <Shield className="w-10 h-10 opacity-30" />
                    </div>
                    <p className="text-sm mb-1">No analysis yet</p>
                    <p className="text-xs">Enter transaction details or pick a test scenario</p>
                  </div>
                )}

                {/* Results */}
                {result && !loading && (
                  <div className="space-y-5 animate-slide-up">
                    {/* Risk Score Banner */}
                    <div className={`text-center p-6 rounded-xl border-2 bg-gradient-to-br ${getRiskBgGradient(result.risk_level)} ${getRiskColor(result.risk_level)}`}>
                      <p className="text-xs uppercase tracking-wider font-semibold mb-2 opacity-80">Fraud Risk Level</p>
                      <div className={`text-5xl font-black mb-1 ${getScoreColor(result.ensemble_score)}`}>
                        {result.ensemble_score.toFixed(1)}%
                      </div>
                      <div className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${getRiskColor(result.risk_level)}`}>
                        {result.risk_level}
                      </div>
                    </div>

                    {/* Score Bar */}
                    <div className="relative h-3 bg-muted rounded-full overflow-hidden">
                      <div
                        className={`absolute top-0 left-0 h-full rounded-full transition-all duration-1000 ${
                          result.ensemble_score < 25 ? 'bg-emerald-500' :
                          result.ensemble_score < 55 ? 'bg-amber-500' :
                          result.ensemble_score < 80 ? 'bg-orange-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(result.ensemble_score, 100)}%` }}
                      />
                    </div>

                    {/* Model Predictions */}
                    <div>
                      <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
                        <Activity className="w-4 h-4 text-primary" />
                        Model Predictions
                      </h4>
                      <div className="space-y-2">
                        {Object.entries(result.models).map(([name, pred]) => (
                          <div key={name} className="flex items-center justify-between p-3 rounded-lg bg-muted/30 border border-border/50 hover:bg-muted/50 transition-colors">
                            <div className="flex items-center gap-2">
                              <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${
                                name === 'classical' ? 'bg-blue-500/10 text-blue-500' :
                                name === 'quantum' ? 'bg-purple-500/10 text-purple-500' :
                                'bg-indigo-500/10 text-indigo-500'
                              }`}>
                                {getModelIcon(name)}
                              </div>
                              <div>
                                <span className="text-sm font-medium">{getModelLabel(name)}</span>
                                {pred.processing_time && (
                                  <span className="text-[10px] text-muted-foreground ml-2">
                                    {pred.processing_time.toFixed(2)}s
                                  </span>
                                )}
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className={`font-bold text-sm ${getScoreColor(pred.score)}`}>
                                {pred.score.toFixed(1)}%
                              </span>
                              <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                                pred.decision === 'FRAUD'
                                  ? 'bg-red-500/10 text-red-500'
                                  : 'bg-emerald-500/10 text-emerald-500'
                              }`}>
                                {pred.decision}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Risk Factors */}
                    {result.risk_factors.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-sm mb-3 flex items-center gap-2">
                          <AlertCircle className="w-4 h-4 text-primary" />
                          Risk Factors ({result.risk_factors.length})
                        </h4>
                        <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                          {result.risk_factors.map((factor, idx) => (
                            <div key={idx} className="p-3 rounded-lg bg-muted/30 border border-border/50">
                              <div className="flex items-start gap-2">
                                <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold shrink-0 mt-0.5 ${
                                  factor.level === 'CRITICAL' ? 'bg-red-500/20 text-red-500' :
                                  factor.level === 'HIGH' ? 'bg-orange-500/20 text-orange-500' :
                                  factor.level === 'MEDIUM' ? 'bg-amber-500/20 text-amber-500' :
                                  'bg-emerald-500/20 text-emerald-500'
                                }`}>
                                  {factor.level}
                                </span>
                                <div>
                                  <p className="font-medium text-xs">{factor.factor}</p>
                                  <p className="text-[11px] text-muted-foreground mt-0.5">{factor.detail}</p>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Recommendation */}
                    <div className={`p-4 rounded-xl border ${
                      result.risk_level === 'LOW' ? 'bg-emerald-500/5 border-emerald-500/30' :
                      result.risk_level === 'MEDIUM' ? 'bg-amber-500/5 border-amber-500/30' :
                      result.risk_level === 'HIGH' ? 'bg-orange-500/5 border-orange-500/30' :
                      'bg-red-500/5 border-red-500/30'
                    }`}>
                      <h4 className="font-semibold text-sm mb-2 flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        Recommendation
                      </h4>
                      <p className="text-xs leading-relaxed whitespace-pre-line text-muted-foreground">
                        {result.recommendation}
                      </p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-10 pb-6 space-y-2">
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <Shield className="w-3.5 h-3.5" />
            <span>FraudShield AI v2.0</span>
            <span className="text-border">|</span>
            <span>Quantum-Classical Hybrid ML</span>
            <span className="text-border">|</span>
            <span>BE Project 2025</span>
          </div>
          <p className="text-[10px] text-muted-foreground">
            Built with Next.js, FastAPI, Qiskit, XGBoost, and Quantum SVM Ensemble
          </p>
        </div>
      </div>
    </main>
  );
}

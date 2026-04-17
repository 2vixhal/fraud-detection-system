'use client';

import { useState } from 'react';
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
import { AlertCircle, CreditCard, TrendingUp, Shield, Clock } from 'lucide-react';

const MERCHANTS = ['Walmart', 'Amazon', 'Target', 'Costco', 'Shell', 'Starbucks', 'McDonald\'s', 'Best Buy', 'Unknown'];
const CATEGORIES = [
  { value: 'grocery_pos', label: 'Grocery Store' },
  { value: 'gas_transport', label: 'Gas & Transportation' },
  { value: 'shopping_net', label: 'Online Shopping' },
  { value: 'shopping_pos', label: 'In-Store Shopping' },
  { value: 'food_dining', label: 'Food & Dining' },
  { value: 'entertainment', label: 'Entertainment' },
  { value: 'personal_care', label: 'Personal Care' },
  { value: 'travel', label: 'Travel' },
  { value: 'misc_pos', label: 'Miscellaneous' },
];

const JOBS = ['Engineer', 'Teacher', 'Sales', 'Healthcare', 'Retail', 'Manager', 'Student', 'Other'];
const US_CITIES = [
  { city: 'New York', state: 'NY' },
  { city: 'Los Angeles', state: 'CA' },
  { city: 'Chicago', state: 'IL' },
  { city: 'Houston', state: 'TX' },
  { city: 'Phoenix', state: 'AZ' },
  { city: 'Miami', state: 'FL' },
  { city: 'Seattle', state: 'WA' },
  { city: 'Boston', state: 'MA' },
];

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<TransactionInput>({
    amount: 0,
    merchant: '',
    category: '',
    date: new Date().toISOString().split('T')[0],
    time: new Date().toTimeString().slice(0, 5),
    age: 35,
    gender: 'M',
    job: '',
    customer_city: '',
    customer_state: '',
    transaction_city: '',
    transaction_state: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await predictFraud(formData);
      setResult(response);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to predict fraud. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const loadPreset = (preset: 'normal' | 'suspicious') => {
    if (preset === 'normal') {
      setFormData({
        amount: 45.50,
        merchant: 'Starbucks',
        category: 'food_dining',
        date: new Date().toISOString().split('T')[0],
        time: '08:30',
        age: 32,
        gender: 'F',
        job: 'Engineer',
        customer_city: 'New York',
        customer_state: 'NY',
        transaction_city: 'New York',
        transaction_state: 'NY',
      });
    } else {
      setFormData({
        amount: 4567.89,
        merchant: 'Unknown',
        category: 'shopping_net',
        date: new Date().toISOString().split('T')[0],
        time: '23:45',
        age: 28,
        gender: 'M',
        job: 'Sales',
        customer_city: 'New York',
        customer_state: 'NY',
        transaction_city: 'Los Angeles',
        transaction_state: 'CA',
      });
    }
    setResult(null);
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'LOW': return 'text-green-600 bg-green-50 border-green-200';
      case 'MEDIUM': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'HIGH': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'CRITICAL': return 'text-red-600 bg-red-50 border-red-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Shield className="w-12 h-12 text-blue-600" />
            <h1 className="text-4xl font-bold text-gray-900">Fraud Detection System</h1>
          </div>
          <p className="text-gray-600 text-lg">
            Quantum-Classical Hybrid ML for Real-Time Credit Card Fraud Detection
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel - Form */}
          <Card className="shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="w-6 h-6" />
                Transaction Details
              </CardTitle>
              <CardDescription>
                Enter transaction information to check for fraud
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Quick Presets */}
                <div className="flex gap-2 mb-4">
                  <Button type="button" variant="outline" size="sm" onClick={() => loadPreset('normal')}>
                    Normal Transaction
                  </Button>
                  <Button type="button" variant="outline" size="sm" onClick={() => loadPreset('suspicious')}>
                    Suspicious Transaction
                  </Button>
                </div>

                {/* Transaction Amount */}
                <div>
                  <Label htmlFor="amount">Amount ($)</Label>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                    required
                  />
                </div>

                {/* Merchant */}
                <div>
                  <Label htmlFor="merchant">Merchant</Label>
                  <Select value={formData.merchant} onValueChange={(v) => setFormData({ ...formData, merchant: v })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select merchant" />
                    </SelectTrigger>
                    <SelectContent>
                      {MERCHANTS.map((m) => (
                        <SelectItem key={m} value={m}>{m}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Category */}
                <div>
                  <Label htmlFor="category">Category</Label>
                  <Select value={formData.category} onValueChange={(v) => setFormData({ ...formData, category: v })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
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
                    <Label htmlFor="date">Date</Label>
                    <Input
                      id="date"
                      type="date"
                      value={formData.date}
                      onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="time">Time</Label>
                    <Input
                      id="time"
                      type="time"
                      value={formData.time}
                      onChange={(e) => setFormData({ ...formData, time: e.target.value })}
                      required
                    />
                  </div>
                </div>

                {/* Customer Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="age">Age</Label>
                    <Input
                      id="age"
                      type="number"
                      value={formData.age}
                      onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) || 0 })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="gender">Gender</Label>
                    <Select value={formData.gender} onValueChange={(v: any) => setFormData({ ...formData, gender: v })}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="M">Male</SelectItem>
                        <SelectItem value="F">Female</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Job */}
                <div>
                  <Label htmlFor="job">Job</Label>
                  <Select value={formData.job} onValueChange={(v) => setFormData({ ...formData, job: v })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select job" />
                    </SelectTrigger>
                    <SelectContent>
                      {JOBS.map((j) => (
                        <SelectItem key={j} value={j}>{j}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Customer Location */}
                <div>
                  <Label>Customer Home Location</Label>
                  <div className="grid grid-cols-2 gap-2">
                    <Select value={formData.customer_city} onValueChange={(v) => {
                      const loc = US_CITIES.find(c => c.city === v);
                      setFormData({ ...formData, customer_city: v, customer_state: loc?.state || '' });
                    }}>
                      <SelectTrigger>
                        <SelectValue placeholder="City" />
                      </SelectTrigger>
                      <SelectContent>
                        {US_CITIES.map((c) => (
                          <SelectItem key={c.city} value={c.city}>{c.city}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Input value={formData.customer_state} readOnly placeholder="State" />
                  </div>
                </div>

                {/* Transaction Location */}
                <div>
                  <Label>Transaction Location</Label>
                  <div className="grid grid-cols-2 gap-2">
                    <Select value={formData.transaction_city} onValueChange={(v) => {
                      const loc = US_CITIES.find(c => c.city === v);
                      setFormData({ ...formData, transaction_city: v, transaction_state: loc?.state || '' });
                    }}>
                      <SelectTrigger>
                        <SelectValue placeholder="City" />
                      </SelectTrigger>
                      <SelectContent>
                        {US_CITIES.map((c) => (
                          <SelectItem key={c.city} value={c.city}>{c.city}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Input value={formData.transaction_state} readOnly placeholder="State" />
                  </div>
                </div>

                {/* Submit Button */}
                <Button type="submit" className="w-full" size="lg" disabled={loading}>
                  {loading ? (
                    <>
                      <Clock className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-4 h-4 mr-2" />
                      Check for Fraud
                    </>
                  )}
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Right Panel - Results */}
          <Card className="shadow-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-6 h-6" />
                Prediction Results
              </CardTitle>
              <CardDescription>
                AI-powered fraud analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-md mb-4">
                  <p className="font-semibold">Error</p>
                  <p className="text-sm">{error}</p>
                </div>
              )}

              {!result && !error && (
                <div className="text-center py-12 text-gray-400">
                  <Shield className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p>Enter transaction details and click "Check for Fraud" to see results</p>
                </div>
              )}

              {result && (
                <div className="space-y-6">
                  {/* Risk Score */}
                  <div className={`text-center p-6 rounded-lg border-2 ${getRiskColor(result.risk_level)}`}>
                    <h3 className="text-lg font-semibold mb-2">{result.risk_level} RISK</h3>
                    <div className="text-5xl font-bold mb-2">{result.ensemble_score.toFixed(1)}%</div>
                    <p className="text-sm opacity-80">Fraud Probability</p>
                  </div>

                  {/* Model Predictions */}
                  <div>
                    <h4 className="font-semibold mb-3">Model Predictions</h4>
                    <div className="space-y-2">
                      {Object.entries(result.models).map(([name, pred]) => (
                        <div key={name} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                          <span className="font-medium capitalize">{name}</span>
                          <div className="text-right">
                            <span className="font-bold">{pred.score.toFixed(1)}%</span>
                            <span className={`ml-2 text-xs px-2 py-1 rounded ${pred.decision === 'FRAUD' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
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
                      <h4 className="font-semibold mb-3">Risk Factors</h4>
                      <div className="space-y-2">
                        {result.risk_factors.map((factor, idx) => (
                          <div key={idx} className="p-3 bg-gray-50 rounded">
                            <div className="flex items-start gap-2">
                              <span className={`text-xs px-2 py-1 rounded font-semibold ${
                                factor.level === 'HIGH' ? 'bg-red-100 text-red-700' :
                                factor.level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-green-100 text-green-700'
                              }`}>
                                {factor.level}
                              </span>
                              <div className="flex-1">
                                <p className="font-medium text-sm">{factor.factor}</p>
                                <p className="text-xs text-gray-600 mt-1">{factor.detail}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommendation */}
                  <div className="bg-blue-50 border border-blue-200 p-4 rounded-md">
                    <h4 className="font-semibold mb-2">Recommendation</h4>
                    <p className="text-sm whitespace-pre-line">{result.recommendation}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 text-gray-600 text-sm">
          <p>Built with Next.js, FastAPI, Qiskit ML, and XGBoost</p>
          <p className="mt-1">Quantum-Classical Hybrid Machine Learning • BE Project 2024</p>
        </div>
      </div>
    </main>
  );
}

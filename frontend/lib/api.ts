import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

export interface TransactionInput {
  amount: number;
  merchant: string;
  category: string;
  date: string;
  time: string;
  age: number;
  gender: 'M' | 'F';
  job: string;
  customer_city: string;
  customer_state: string;
  transaction_city: string;
  transaction_state: string;
  country?: string;
  custom_city?: string;
}

export interface ModelPrediction {
  score: number;
  decision: string;
  processing_time?: number;
}

export interface RiskFactor {
  level: string;
  factor: string;
  detail: string;
}

export interface PredictionResponse {
  ensemble_score: number;
  risk_level: string;
  recommendation: string;
  models: {
    classical: ModelPrediction;
    quantum: ModelPrediction;
    ensemble: ModelPrediction;
  };
  risk_factors: RiskFactor[];
  feature_values: Record<string, number>;
  analysis_time?: number;
}

export const predictFraud = async (transaction: TransactionInput): Promise<PredictionResponse> => {
  const response = await api.post<PredictionResponse>('/api/predict/transaction', transaction);
  return response.data;
};

export const getPresets = async () => {
  const response = await api.get('/api/presets');
  return response.data;
};

export const getMerchants = async () => {
  const response = await api.get('/api/options/merchants');
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get('/api/options/categories');
  return response.data;
};

export const getJobs = async () => {
  const response = await api.get('/api/options/jobs');
  return response.data;
};

export default api;

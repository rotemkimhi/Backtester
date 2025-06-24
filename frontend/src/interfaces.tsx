
export interface Metrics {
  totalReturn: number;
  winRate: number;
  numTrades: number;
  maxDrawdown: number;
}
export interface EquityPoint {
  timestamp: string;
  value: number;
}
export interface BacktestResult {
  metrics: Metrics;
  equity: EquityPoint[];
  error?: string;
}
export interface Strategy {
  id: string;
  name: string;
}
export interface SavedStrategiesProps {
  strategies: Strategy[];
  strategyName: string;
  setStrategyName: (name: string) => void;
  onSave: () => void;
  onDelete: (name: string) => void;
}
export interface MessageAlertProps {
  message: string;
  error: boolean;
}
import { AnimatePresence, motion } from "framer-motion";
import type { BacktestResult, Strategy } from "../interfaces";
import StrategyFileLoader from "./StrategyFileLoader";
import EquityChart from "./EquityChart";
import MetricsGrid from "./MetricsGrid";
import MessageAlert from "./MessageAlert";

interface Props {
  file: File | null;
  message: string;
  loading: boolean;
  result: BacktestResult | null;
  onFileChange: (file: File | null) => void;
  onBacktest: () => void;
  selectedStrategy: Strategy | null;
  setSelectedStrategy: (s: Strategy | null) => void;
}

export function MainCard({
  file,
  message,
  loading,
  result,
  onFileChange,
  onBacktest,
  selectedStrategy,
  setSelectedStrategy,
}: Props) {
  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 50, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.8, type: "spring" }}
    >
      <div className="flex items-center gap-3 mb-8">
        <span className="headline">
          Strategy Backtester
        </span>
      </div>
      <p className="subtitle">
        Upload any CSV and get instant, robust backtest analytics.
      </p>
      <StrategyFileLoader
        file={file}
        loading={loading}
        onFileChange={onFileChange}
        onBacktest={onBacktest}
        selectedStrategy={selectedStrategy}
        setSelectedStrategy={setSelectedStrategy}
      />
      <MessageAlert
        message={
          result
            ? result.error
              ? result.error
              : "Backtest successful!"
            : message
        }
        error={!!result?.error}
      />
      <AnimatePresence>
        {result && !result.error && (
          <motion.div
            className="w-full mt-6"
            initial={{ opacity: 0, y: 60 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.7 }}
          >
            <MetricsGrid metrics={result.metrics} />
            <EquityChart data={result.equity} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
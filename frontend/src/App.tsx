import { useState } from "react";
import axios from "axios";
import { MainCard } from "./components/MainCard";
import type { BacktestResult, Strategy } from "./interfaces";
import "./App.css";

export default function App() {
  const [file, setFile] = useState<File | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<Strategy | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (f: File | null) => {
    setFile(f);
    setMessage("");
    setResult(null);
  };

  const handleBacktest = async () => {
    if (!file || !selectedStrategy) return;
    setLoading(true);
    setMessage("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("strategy_id", selectedStrategy.id);

    try {
      const res = await axios.post<BacktestResult>(
        "http://localhost:8000/backtest",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setResult(res.data);
      setMessage("Backtest successful!");
    } catch (error) {
      let errorMsg = "Error during backtest. Please check your file.";
      if (axios.isAxiosError(error)) {
        errorMsg =
          error.response?.data?.error ||
          error.response?.data?.detail ||
          error.message ||
          errorMsg;
      } else if (error instanceof Error) {
        errorMsg = error.message;
      }
      setMessage(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-bg">
      <MainCard
        file={file}
        message={message}
        loading={loading}
        result={result}
        onFileChange={handleFileChange}
        onBacktest={handleBacktest}
        selectedStrategy={selectedStrategy}
        setSelectedStrategy={setSelectedStrategy}
      />
      <div className="footer">
        © {new Date().getFullYear()} Koumach
      </div>
    </div>
  );
}

import { useState } from "react";
import axios from "axios";
import { UploadIcon } from "@radix-ui/react-icons";
import type { Strategy } from "../interfaces";

interface Props {
  file: File | null;
  loading: boolean;
  onFileChange: (file: File | null) => void;
  onBacktest: () => void;
  selectedStrategy: Strategy | null;
  setSelectedStrategy: (s: Strategy | null) => void;
}

export default function StrategyFileLoader({
  file,
  loading,
  onFileChange,
  onBacktest,
  selectedStrategy,
  setSelectedStrategy,
}: Props) {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [dropdownLoading, setDropdownLoading] = useState(false);

  async function fetchStrategies() {
    setDropdownLoading(true);
    try {
      const res = await axios.get("/backend/strategies");
      // Debug: log the data you actually receive
      console.log("Fetched strategies:", res.data);
      // Defensive: make sure it's an array
      setStrategies(Array.isArray(res.data) ? res.data : []);
    } catch (err) {
      console.error("Error fetching strategies:", err);
      setStrategies([]);
    } finally {
      setDropdownLoading(false);
    }
  }

  const handleDropdownToggle = async () => {
    if (!showDropdown) {
      setShowDropdown(true);
      if (strategies.length === 0) {
        await fetchStrategies();
      }
    } else {
      setShowDropdown(false);
    }
  };

  const handleSelectStrategy = (strategy: Strategy) => {
    setSelectedStrategy(strategy);
    setShowDropdown(false);
  };

  return (
    <div className="relative w-full flex flex-col items-center">
      <div className="flex gap-3 mb-4">
        {/* Change File Button */}
        <label className="upload-label flex-1 flex justify-center">
          <UploadIcon />
          <span>{file ? "Change File" : "Upload CSV"}</span>
          <input
            type="file"
            accept=".csv"
            className="hidden"
            onChange={e => onFileChange(e.target.files?.[0] || null)}
            disabled={loading}
          />
        </label>

        {/* Load Strategy Button */}
        <button
          className="upload-label flex-1 flex justify-center bg-gradient-to-r from-green-600 to-teal-400 hover:from-green-700 hover:to-teal-500 text-white"
          onClick={handleDropdownToggle}
          type="button"
          disabled={loading}
        >
          <svg className="inline mr-2" width={18} height={18} viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" />
            <path d="M7 10l3 3 3-3" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Load Strategy
        </button>
      </div>

      {/* File and Strategy indicators */}
      <div className="flex gap-6 items-center mb-2">
        {file && <span className="text-green-400 text-sm flex items-center gap-1">✔ <span>{file.name}</span></span>}
        {selectedStrategy && (
          <span className="text-indigo-300 text-sm flex items-center gap-1">
            ✔ <span>{selectedStrategy.name}</span>
          </span>
        )}
      </div>

      {/* Strategy Dropdown */}
      {showDropdown && (
        <div className="absolute z-40 mt-2 left-1/2 -translate-x-1/2 w-72 bg-gray-900 border border-gray-700 rounded-xl shadow-lg animate-fadeIn min-h-[56px] flex flex-col">
          {/* DEBUG: show what strategies contains */}
          <pre className="text-xs text-gray-500 p-1 overflow-x-auto">
            {/* {JSON.stringify(strategies, null, 2)} */}
          </pre>
          {(dropdownLoading || !Array.isArray(strategies) || strategies.length === 0) && (
            <div className="p-4 text-center text-gray-400">
              {dropdownLoading
                ? "Loading..."
                : "No strategies found"}
            </div>
          )}
          {Array.isArray(strategies) && strategies.length > 0 && (
            <ul className="max-h-72 overflow-y-auto">
              {strategies.map((strategy) => (
                <li
                  key={strategy.id}
                  onClick={() => handleSelectStrategy(strategy)}
                  className={`cursor-pointer px-4 py-3 hover:bg-indigo-700 hover:text-white ${
                    selectedStrategy?.id === strategy.id
                      ? "bg-indigo-900 text-white"
                      : "text-indigo-300"
                  }`}
                >
                  {strategy.name}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Backtest Button */}
      <button
        className="backtest-btn mt-6"
        disabled={!file || !selectedStrategy || loading}
        onClick={onBacktest}
      >
        {loading ? (
          <span>
            <svg className="inline w-4 h-4 mr-2 animate-spin" viewBox="0 0 16 16" fill="none">
              <circle className="opacity-25" cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="2" />
              <path className="opacity-75" fill="currentColor" d="M15 8A7 7 0 1 1 8 1v2a5 5 0 1 0 5 5h2z" />
            </svg>
            Processing...
          </span>
        ) : "Backtest"}
      </button>
    </div>
  );
}

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

# Import your strategy functions
from strategies.strategy import backtest_strategy
from strategies.ml_tree import ml_tree
from parseCSV import clean_dataframe
from strategies.ml_tree_w_short import ml_tree_short
from strategies.ml_mlp import ml_mlp
from strategies.ml_xboost import ml_xgboost

app = Flask(__name__)
CORS(app)

@app.route("/backtest", methods=["POST"])
def backtest():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        df = pd.read_csv(file)
        df = df.dropna()
        df = clean_dataframe(df)  # Assuming clean_dataframe is defined in parseCSV.py

        # Get selected strategy ID from form data (if provided)
        strategy_id = request.form.get("strategy_id", "ml_mlp")
        print("Selected strategy_id:", strategy_id)  # Debug print

        # Route to the selected strategy function
        if strategy_id == "ml_mlp":
            results = ml_mlp(df)
        elif strategy_id == "ml_tree":
            results = ml_tree(df)
        elif strategy_id == "ml_tree_short":
            results = ml_tree_short(df)
        elif strategy_id == "ml_xgboost":
            results = ml_xgboost(df)
        elif strategy_id == "backtest_strategy":
            results = backtest_strategy(df)
        else:
            return jsonify({"error": f"Unknown strategy: {strategy_id}"}), 400

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/backend/strategies", methods=["GET"])
def list_strategies():
    strategy_map = {
        "ml_mlp.py": ("ml_mlp", "MLP Neural Net"),
        "ml_tree.py": ("ml_tree", "Decision Tree"),
        "ml_tree_w_short.py": ("ml_tree_short", "Tree With Short"),
        "ml_xboost.py": ("ml_xgboost", "XGBoost"),
        "strategy.py": ("backtest_strategy", "Classic Backtest"),
    }
    strategies_dir = os.path.join(os.path.dirname(__file__), "strategies")
    files = [
        f for f in os.listdir(strategies_dir)
        if f.endswith(".py") and not f.startswith("__")
    ]
    strategies = []
    for fname in files:
        if fname in strategy_map:
            id_, name = strategy_map[fname]
            strategies.append({"id": id_, "name": name})
    # Only return strategies found in the map!
    return jsonify(strategies)

if __name__ == "__main__":
    app.run(debug=True, port=8000)

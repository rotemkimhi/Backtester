def ml_mlp(
    df, 
    confidence_threshold=0.35,
    initial_balance=1000,
    stop_mult=0.9,
    plot=False
):
    import pandas as pd
    import numpy as np
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler

    df = df.copy()
    # === ORIGINAL FEATURE ENGINEERING ===
    df['SMA10'] = df['close'].rolling(10).mean()
    df['SMA30'] = df['close'].rolling(30).mean()
    df['SMA_ratio'] = df['SMA10'] / df['SMA30']
    df['SMA_cross'] = (df['SMA10'] > df['SMA30']).astype(int)
    df['return_1d'] = df['close'].pct_change()
    df['return_5d'] = df['close'].pct_change(5)
    df['return_10d'] = df['close'].pct_change(10)
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR14'] = tr.rolling(14).mean()
    df['volatility_5d'] = df['return_1d'].rolling(5).std()
    df['volatility_10d'] = df['return_1d'].rolling(10).std()
    df['vol_avg_5d'] = df['volume'].rolling(5).mean()
    df['close_vs_SMA10'] = df['close'] / df['SMA10']
    df['close_vs_SMA30'] = df['close'] / df['SMA30']
    df['SMA10_slope'] = df['SMA10'].diff()
    df['SMA30_slope'] = df['SMA30'].diff()
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    RS = gain / (loss + 1e-6)
    df['RSI14'] = 100 - (100 / (1 + RS))
    # === NEW FEATURES ===
    # MACD
    df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = df['ema12'] - df['ema26']
    df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_diff'] = df['MACD'] - df['MACD_signal']
    # Bollinger Bands
    df['BB_MA20'] = df['close'].rolling(20).mean()
    df['BB_std20'] = df['close'].rolling(20).std()
    df['BB_upper'] = df['BB_MA20'] + 2 * df['BB_std20']
    df['BB_lower'] = df['BB_MA20'] - 2 * df['BB_std20']
    df['BB_pct'] = (df['close'] - df['BB_lower']) / (df['BB_upper'] - df['BB_lower'] + 1e-9)
    # Distance from 30d high/low
    df['30d_high'] = df['close'].rolling(30).max()
    df['30d_low'] = df['close'].rolling(30).min()
    df['close_vs_high30'] = df['close'] / df['30d_high']
    df['close_vs_low30'] = df['close'] / df['30d_low']
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    df = df.dropna().reset_index(drop=True)

    features = [
        'SMA10', 'SMA30', 'SMA_ratio', 'SMA_cross',
        'return_1d', 'return_5d', 'return_10d',
        'ATR14', 'volatility_5d', 'volatility_10d',
        'vol_avg_5d',
        'close_vs_SMA10', 'close_vs_SMA30',
        'SMA10_slope', 'SMA30_slope',
        'RSI14',
        'MACD', 'MACD_signal', 'MACD_diff',
        'BB_pct', 'close_vs_high30', 'close_vs_low30'
    ]
    X = df[features]
    y = df['target']
    split = int(0.8 * len(df))
    X_train, X_test = X.iloc[:split], X.iloc[split:]
    y_train, y_test = y.iloc[:split], y.iloc[split:]
    df_test = df.iloc[split:].copy().reset_index(drop=True)

    # === SCALE FEATURES ===
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # === TUNED MLP ===
    model = MLPClassifier(
        hidden_layer_sizes=(64, 32, 16),
        max_iter=2000,
        random_state=42,
        alpha=0.001,
        learning_rate_init=0.001,
        early_stopping=True,
        n_iter_no_change=20,
        validation_fraction=0.1
    )
    model.fit(X_train_scaled, y_train)
    proba_up = model.predict_proba(X_test_scaled)[:,1]
    df_test['proba_up'] = proba_up

    df_test['position'] = (df_test['proba_up'] > confidence_threshold).astype(int)
    df_test['returns'] = df_test['close'].pct_change().shift(-1)
    pos = df_test['position'].values
    timestamps = df_test['timestamp'].values
    closes = df_test['close'].values
    lows = df_test['low'].values
    atrs = df_test['ATR14'].values
    trades = []
    balance = initial_balance
    equity_curve = [balance]
    i = 1
    while i < len(pos):
        if pos[i-1] == 0 and pos[i] == 1:
            entry_idx = i
            entry_price = closes[entry_idx]
            atr = atrs[entry_idx]
            stop_loss = entry_price - stop_mult * atr
            j = entry_idx + 1
            exit_idx = None
            exit_reason = None
            while j < len(pos):
                if lows[j] < stop_loss:
                    exit_idx = j
                    exit_price = stop_loss
                    exit_reason = "stop_loss"
                    break
                if pos[j-1] == 1 and pos[j] == 0:
                    exit_idx = j
                    exit_price = closes[exit_idx]
                    exit_reason = "ml_exit"
                    break
                j += 1
            if exit_idx is None:
                exit_idx = len(pos) - 1
                exit_price = closes[exit_idx]
                exit_reason = "eod"
            pct_change = (exit_price - entry_price) / entry_price
            balance *= (1 + pct_change)
            trades.append({
                "entry_time": str(timestamps[entry_idx]),
                "entry_price": entry_price,
                "exit_time": str(timestamps[exit_idx]),
                "exit_price": exit_price,
                "pct_change": pct_change,
                "reason": exit_reason
            })
            for k in range(i, exit_idx + 1):
                equity_curve.append(balance)
            i = exit_idx + 1
        else:
            equity_curve.append(balance)
            i += 1
    while len(equity_curve) < len(df_test):
        equity_curve.append(balance)
    total_return = 100 * (equity_curve[-1] / initial_balance - 1)
    peak = pd.Series(equity_curve).cummax()
    drawdown = (pd.Series(equity_curve) - peak) / peak
    max_drawdown = drawdown.min() * 100
    num_trades = len(trades)
    win_rate = (sum(1 for t in trades if t['pct_change'] > 0) / num_trades) if num_trades > 0 else 0
    equity = [
        {"timestamp": str(row['timestamp']), "value": eq}
        for (_, row), eq in zip(df_test.iterrows(), equity_curve)
    ]
    if plot:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(12,6))
        plt.plot(df_test['timestamp'], equity_curve[:len(df_test)], label="MLPClassifier Improved")
        plt.plot(df_test['timestamp'], initial_balance * (1 + df_test['returns'].fillna(0)).cumprod(), label="Buy & Hold", alpha=0.4)
        plt.legend()
        plt.title("Improved MLP Strategy vs Buy & Hold")
        plt.show()
    return {
        "metrics": {
            "totalReturn": round(total_return, 2),
            "winRate": round(win_rate * 100, 2),
            "numTrades": int(num_trades),
            "maxDrawdown": round(max_drawdown, 2),
        },
        "equity": equity,
        "trades": trades
    }

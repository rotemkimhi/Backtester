import pandas as pd
import numpy as np

def calculate_sma(df, period):
    return df['close'].rolling(window=period).mean()

def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr

def backtest_strategy(df, initial_balance=1000, stop_mult=2, take_mult=2):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    if not df['timestamp'].is_monotonic_increasing:
        df = df.iloc[::-1].reset_index(drop=True)

    df['SMA10'] = calculate_sma(df, 10)
    df['SMA30'] = calculate_sma(df, 30)
    df['ATR'] = calculate_atr(df, 14)
    df = df.dropna(subset=['SMA10', 'SMA30', 'ATR']).reset_index(drop=True)

    balance = initial_balance
    in_position = False
    entry_price = 0
    stop_loss = 0
    take_profit = 0
    equity_curve = []
    trades = []

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i-1]
        equity_curve.append(balance)

        if not in_position:
            if prev_row['SMA10'] <= prev_row['SMA30'] and row['SMA10'] > row['SMA30']:
                entry_price = row['close']
                stop_loss = entry_price - stop_mult * row['ATR']
                take_profit = entry_price + take_mult * row['ATR']
                in_position = True
                trades.append({"entry_time": row['timestamp'], "entry_price": entry_price})
        else:
            hit_stop = row['low'] <= stop_loss
            hit_take = row['high'] >= take_profit
            cross_down = row['SMA10'] < row['SMA30']

            exit_price = None
            reason = None

            if hit_stop and hit_take:
                exit_price = stop_loss  # assume stop hit first
                reason = "stop_loss_and_take_profit"
            elif hit_stop:
                exit_price = stop_loss
                reason = "stop_loss"
            elif hit_take:
                exit_price = take_profit
                reason = "take_profit"
            elif cross_down:
                exit_price = row['close']
                reason = "sma_cross_down"

            if exit_price is not None:
                pct_change = (exit_price - entry_price) / entry_price
                balance *= (1 + pct_change)
                in_position = False
                trades[-1].update({"exit_time": row['timestamp'], "exit_price": exit_price, "pct_change": pct_change, "reason": reason})
                equity_curve[-1] = balance

    if in_position:
        final_exit = df.iloc[-1]
        exit_price = final_exit['close']
        pct_change = (exit_price - entry_price) / entry_price
        balance *= (1 + pct_change)
        trades[-1].update({"exit_time": final_exit['timestamp'], "exit_price": exit_price, "pct_change": pct_change, "reason": "end_of_data"})
        equity_curve[-1] = balance

    while len(equity_curve) < len(df):
        equity_curve.append(balance)

    df['equity_curve'] = equity_curve

    total_return = (balance - initial_balance) / initial_balance * 100
    peak = pd.Series(equity_curve).cummax()
    drawdown = (pd.Series(equity_curve) - peak) / peak
    max_drawdown = drawdown.min() * 100
    num_trades = len(trades)
    wins = sum([1 for t in trades if t.get('pct_change', 0) > 0])
    win_rate = wins / num_trades if num_trades else 0

    return {
        "metrics": {
            "totalReturn": round(total_return, 2),
            "winRate": round(win_rate * 100, 2),
            "numTrades": int(num_trades),
            "maxDrawdown": round(max_drawdown, 2),
        },
        "equity": [
            {"timestamp": str(row['timestamp']), "value": eq}
            for (_, row), eq in zip(df.iterrows(), equity_curve)
        ],
        "trades": trades
    }
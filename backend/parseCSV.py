import pandas as pd

def clean_dataframe(df):
    df.columns = [col.lower() for col in df.columns]
    for col in df.select_dtypes(include=['object']):
        df[col] = df[col].astype(str).str.replace('$', '', regex=False)
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
    return df

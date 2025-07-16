import json
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def calculate_credit_scores(data):
    """
    Calculates credit scores for each wallet and generates a distribution graph.

    Args:
        data (list): A list of dictionaries, where each dictionary represents a transaction.

    Returns:
        pandas.DataFrame: A DataFrame with wallet addresses and their corresponding credit scores.
    """

    # Create a DataFrame from the JSON data
    df = pd.DataFrame(data)

    # Convert timestamp to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    # Feature Engineering: Convert amount to float to handle very large numbers
    df['amount'] = df['actionData'].apply(lambda x: float(x.get('amount', 0)))

    # --- Feature Calculations ---
    wallet_features = df.groupby('userWallet').agg(
        total_transactions=('txHash', 'count'),
        total_volume=('amount', 'sum'),
        avg_transaction_volume=('amount', 'mean'),
        unique_assets=('actionData', lambda x: x.apply(lambda y: y.get('assetSymbol')).nunique()),
        transaction_frequency=('timestamp', lambda x: (x.max() - x.min()).total_seconds() / len(x) if len(x) > 1 else 0),
        liquidation_events=('action', lambda x: (x == 'liquidationcall').sum())
    ).reset_index()

    action_counts = df.groupby(['userWallet', 'action']).size().unstack(fill_value=0)
    wallet_features = pd.merge(wallet_features, action_counts, on='userWallet', how='left')
    wallet_features = wallet_features.fillna(0)

    # --- Scoring Logic ---
    weights = {
        'total_transactions': 0.15,
        'total_volume': 0.20,
        'avg_transaction_volume': 0.15,
        'unique_assets': 0.10,
        'transaction_frequency': -0.10,
        'liquidationcall': -0.30,
        'deposit': 0.10,
        'borrow': 0.05,
        'repay': 0.10,
        'redeemunderlying': 0.05,
    }

    scaler = MinMaxScaler()
    for feature in weights.keys():
        if feature in wallet_features.columns:
            wallet_features[feature + '_norm'] = scaler.fit_transform(wallet_features[[feature]])

    wallet_features['credit_score'] = 0
    for feature, weight in weights.items():
        if feature in wallet_features.columns:
            wallet_features['credit_score'] += wallet_features[feature + '_norm'] * weight

    scaler_score = MinMaxScaler(feature_range=(0, 1000))
    wallet_features['credit_score'] = scaler_score.fit_transform(wallet_features[['credit_score']])

    return wallet_features[['userWallet', 'credit_score']]

def plot_score_distribution(scores_df):
    """
    Plots and saves a histogram of the credit score distribution.
    """
    plt.style.use('ggplot')
    plt.figure(figsize=(10, 6))
    plt.hist(scores_df['credit_score'], bins=10, range=(0, 1000), color='skyblue', edgecolor='black')
    plt.title('Wallet Credit Score Distribution')
    plt.xlabel('Credit Score Range')
    plt.ylabel('Number of Wallets')
    plt.xticks(range(0, 1001, 100))
    plt.grid(axis='y', alpha=0.75)

    # Save the plot to a file
    plt.savefig('score_distribution.png')
    print("\nGraph 'score_distribution.png' has been saved to the root directory.")


if __name__ == '__main__':
    # Load data
    try:
        with open('/Users/prakashroy/zeru/python_code/data/user-wallet-transactions.json', 'r') as f:
            transactions = json.load(f)
    except FileNotFoundError:
        print("Error: 'data/user-transactions.json' not found. Make sure the file is in the 'data' directory.")
        exit()


    # Calculate scores
    wallet_scores = calculate_credit_scores(transactions)

    # Print results
    print("--- Wallet Credit Scores ---")
    print(wallet_scores)

    # Save scores to CSV
    wallet_scores.to_csv('wallet_scores.csv', index=False)
    print("\nScores saved to 'wallet_scores.csv'.")

    # Generate and save the distribution plot
    plot_score_distribution(wallet_scores)
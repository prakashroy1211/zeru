# Aave V2 Wallet Credit Scoring

This project develops a credit scoring model that assigns a score between 0 and 1000 to each wallet on the Aave V2 protocol. The scoring is based solely on a wallet's historical transaction behavior. Higher scores indicate reliable and responsible usage, while lower scores may reflect risky, bot-like, or exploitative behavior.

## Methodology

The credit scoring model is designed to be transparent and extensible. It uses a feature-engineering approach to extract meaningful behavioral signals from raw transaction data.

### 1. Data Source

The model is built using a sample of 100,000 transaction-level records from the Aave V2 protocol on the Polygon network. Each record corresponds to a wallet interacting with the protocol through one of the following actions:

* `deposit`
* `borrow`
* `repay`
* `redeemunderlying`
* `liquidationcall`

### 2. Feature Engineering

To capture the nuances of a wallet's on-chain behavior, the following features are engineered from the raw data:

* **Total Transactions**: The total number of interactions a wallet has had with the protocol.
* **Total Volume**: The cumulative USD value of all transactions.
* **Average Transaction Volume**: The average USD value per transaction.
* **Unique Assets**: The number of different crypto-assets a wallet has supplied or borrowed.
* **Transaction Frequency**: The average time between a wallet's transactions.
* **Liquidation Events**: A count of how many times a wallet's position has been liquidated.
* **Action Counts**: The total count for each specific action type (e.g., number of deposits, number of borrows).

### 3. Scoring Logic

A weighted scoring system is used to calculate a credit score for each wallet. Features are first normalized to a common scale (0 to 1) and then aggregated using weights that reflect their importance in assessing creditworthiness. The final score is then scaled to the 0-1000 range.

**Feature Weights:**

| Feature | Weight | Rationale |
| :--- | :--- | :--- |
| **Positive Indicators** | | |
| Total Volume | +0.20 | High volume suggests significant financial capacity and trust. |
| Total Transactions | +0.15 | High activity indicates strong engagement with the protocol. |
| Average Transaction Volume| +0.15 | Larger, less frequent transactions can indicate more thoughtful user behavior. |
| Repay Actions | +0.10 | Frequent repayments are a strong signal of creditworthiness. |
| Deposit Actions | +0.10 | Consistent deposits show a healthy financial standing. |
| Unique Assets | +0.10 | A diverse portfolio can indicate a more sophisticated user. |
| **Negative Indicators** | | |
| Liquidation Events | -0.30 | **The strongest negative signal.** Indicates poor debt management and high risk. |
| Transaction Frequency | -0.10 | Very high frequency (low time between transactions) is penalized to flag potential bot activity. |


### 4. Architecture and Processing Flow

The entire process is contained within a single Python script (`scorer.py`) and follows these steps:

1.  **Load Data**: The script loads the raw transaction data from the `user-transactions.json` file.
2.  **Feature Engineering**: It processes the data to compute the behavioral features for each unique wallet.
3.  **Normalization**: All engineered features are scaled to a 0-1 range using a Min-Max scaler to ensure fair weighting.
4.  **Scoring**: A weighted sum of the normalized features is calculated to generate a raw score.
5.  **Scaling**: The final score is scaled to fit the 0-1000 range.
6.  **Output**: The final wallet addresses and their credit scores are saved to `wallet_scores.csv`, and a distribution graph is saved as `score_distribution.png`.

## How to Run the Project

### 1. Setup Environment

First, create and activate a Python virtual environment.

```bash
# Create the environment
python3 -m venv venv

# Activate it (on macOS/Linux)
source venv/bin/activate
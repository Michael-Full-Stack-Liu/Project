# Seattle Alpha Terminal (Dashboard) Guide

This document explains how to launch the quantitative trading dashboard and provides a detailed breakdown of its interface and functionalities.

## 🚀 How to Open the Dashboard

1. **Install Dependencies** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the Database**:
   The dashboard requires local data to display real-time metrics. Run the data fetcher to populate the local SQLite database (`app_database.db`):
   ```bash
   python data_fetcher.py
   ```

3. **Start the Application**:
   You can start the terminal using the main entry script:
   ```bash
   python main.py
   ```
   *Alternatively, you can run it directly via Streamlit: `streamlit run app.py`*

4. **Access the Interface**:
   Once the server starts, open your browser and navigate to:
   👉 **http://localhost:8501**


---


## 🖥️ Dashboard Interface Breakdown

Our high-density UI is divided into strategic quadrants, designed specifically for rapid operator reading and trade execution.

### 1. System Status Bar (Global Top)
- **Purpose**: Provides immediate situational awareness.
- **Details**: Displays the live connection status to aviation weather APIs (METAR) and Polymarket. It also shows the current model version, your backtested MAE (Mean Absolute Error), and the current server timestamp.

### 2. Market Implied vs AI Forecast (Top-Left Panel)
- **Purpose**: To discover pricing inefficiencies and identify arbitrage opportunities.
- **Details**:
  - **Probability Layering**: Displays the market's implied probabilities (solid blue bars) overlaid with the AI model's Gaussian probability distribution (cyan dashed line).
  - **Alpha Edge**: Automatically calculates and highlights the absolute "Edge" (+X.X%) for specific temperature brackets where the retail market is acting irrationally compared to the model's forecast.
  - **KPIs**: Summarizes the Model Target vs. Market Consensus and the estimated Expected Value (EV) per share.

### 3. Simulated Portfolio & PnL (Bottom-Left Panel)
- **Purpose**: To manage risk, visualize asset allocation, and track profitability.
- **Details**:
  - **Waterfall Chart**: Dynamically maps realized gains, losses, and net Unrealized PnL.
  - **Allocation Donut**: A heat-map visualization ensuring capital distribution stays within safety limits.
  - **Position Ledger**: A real-time updating table showing your current holdings, entry prices, mark-to-market prices, and per-asset ROI without needing page reloads.

### 4. AI Diagnostic Radar (Top-Right Panel)
- **Purpose**: To build trust in the model by showing *what* it is seeing and *why* it is predicting a specific number.
- **Details**:
  - **Primary Forecast & Confidence**: Shows the exact predicted temperature alongside a gauge indicating the neural network's activation certainty.
  - **Telemetry Grid**: A live dashboard of 8 physical measurements (Temp, Dew Point, Wind, Pressure, etc.) complete with rate-of-change deltas relative to previous hours.
  - **Decision Matrix**: A horizontal bar chart providing interpretability. It surfaces the specific features (e.g., LSTM Temporal Memory, Surface Pressure Trends) driving the current prediction, colored by positive or negative impact.

### 5. Trade Recommendation & Execution (Bottom-Right Panel)
- **Purpose**: Translating data into immediate, statistically sound financial actions.
- **Details**:
  - **Action Block**: Synthesizes the exact Recommended Action (e.g., BUY "Seattle 58-60°F") based on the highest edge.
  - **Kelly Sizing**: Calculates the optimal statistical fraction of your bankroll to stake, dynamically managing exposure risk.
  - **Hot Execution**: A direct "EXECUTE ON POLYMARKET" button that deep-links you straight to the correct smart contract for immediate order routing.

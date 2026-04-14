import pandas as pd
import numpy as np
import lightgbm as lgb
import pickle
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from datetime import datetime

class TimeSeriesLSTM(nn.Module):
    def __init__(self, input_size, hidden_layer_size=32, output_size=1):
        super(TimeSeriesLSTM, self).__init__()
        self.hidden_layer_size = hidden_layer_size
        self.lstm = nn.LSTM(input_size, hidden_layer_size, batch_first=True)
        self.linear = nn.Linear(hidden_layer_size, output_size)

    def forward(self, input_seq):
        lstm_out, _ = self.lstm(input_seq)
        predictions = self.linear(lstm_out[:, -1, :])
        return predictions

def train_models():
    data = pd.read_csv("train/processed_training_data.csv")
    data['local_date'] = pd.to_datetime(data['local_date'])
    data = data.sort_values('local_date')
    
    # Feature columns
    feature_cols = [c for c in data.columns if c not in ['local_date', 'target_max_temp']]
    X = data[feature_cols].fillna(0).values
    y = data['target_max_temp'].values
    
    # Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.15, shuffle=False)
    
    print("Training LSTM...")
    # Prepare data for LSTM (batch, seq, features)
    # Using window size 1 for simplicity of this demo, since data is just rows
    X_train_ts = torch.tensor(X_train, dtype=torch.float32).unsqueeze(1)
    y_train_ts = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    
    lstm_model = TimeSeriesLSTM(input_size=X_train.shape[1])
    loss_function = nn.MSELoss()
    optimizer = torch.optim.Adam(lstm_model.parameters(), lr=0.01)
    
    epochs = 50
    for i in range(epochs):
        optimizer.zero_grad()
        y_pred = lstm_model(X_train_ts)
        loss = loss_function(y_pred, y_train_ts)
        loss.backward()
        optimizer.step()
    
    X_test_ts = torch.tensor(X_test, dtype=torch.float32).unsqueeze(1)
    
    with torch.no_grad():
        lstm_train_preds = lstm_model(X_train_ts).numpy().flatten()
        lstm_test_preds = lstm_model(X_test_ts).numpy().flatten()
    
    lstm_mae = mean_absolute_error(y_test, lstm_test_preds)
    print(f"LSTM Test MAE: {lstm_mae:.4f}")
    
    print("Training LGBM for Stacking...")
    # Stacking: train LGBM on original features + LSTM predictions
    X_train_meta = np.column_stack((X_train, lstm_train_preds))
    X_test_meta = np.column_stack((X_test, lstm_test_preds))
    
    lgb_model = lgb.LGBMRegressor(n_estimators=100, random_state=42)
    lgb_model.fit(X_train_meta, y_train)
    
    lgb_test_preds = lgb_model.predict(X_test_meta)
    
    final_mae = mean_absolute_error(y_test, lgb_test_preds)
    print(f"Final Stacked Test MAE: {final_mae:.4f}")
    
    # Save models
    torch.save(lstm_model.state_dict(), "train/model_lstm.pth")
    with open("train/model_lgb.pkl", "wb") as f:
        pickle.dump(lgb_model, f)
    with open("train/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
        
    print("Models and scaler saved in train/ directory.")

if __name__ == "__main__":
    train_models()

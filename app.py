from flask import Flask, render_template, jsonify
from strategy import QuantSystem
from backtest import Backtester
import pandas as pd
import numpy as np

app = Flask(__name__)

# Cache para resultados
cached_results = {}

def get_strategy_results(ticker="SPY"):
    if ticker in cached_results:
        return cached_results[ticker]
    
    system = QuantSystem(ticker=ticker, start_date="2020-01-01")
    signals = system.generate_signals()
    bt = Backtester(signals)
    results = bt.run()
    metrics = bt.performance_metrics()
    
    # Preparar datos para JSON
    # Solo enviamos los últimos 500 días para mejorar rendimiento en el frontend
    plot_df = results.tail(1000).copy()
    
    data = {
        "dates": plot_df.index.strftime('%Y-%m-%d').tolist(),
        "equity_curve": plot_df['Cum_Strategy'].tolist(),
        "benchmark": plot_df['Cum_Market'].tolist(),
        "volatility": (plot_df['GARCH_Vol_Ann'] * 100).tolist(),
        "signals": plot_df['Signal'].tolist(),
        "metrics": {
            "cagr": f"{metrics['CAGR']:.2%}",
            "sharpe": f"{metrics['Sharpe']:.2f}",
            "max_dd": f"{metrics['MaxDD']:.2%}",
            "beta": f"{metrics['Beta']:.2f}"
        },
        "current_signal": "BUY" if plot_df['Signal'].iloc[-1] == 1 else "HOLD/SELL",
        "ticker": ticker
    }
    
    cached_results[ticker] = data
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
@app.route('/api/data/<ticker>')
def get_data(ticker="SPY"):
    try:
        data = get_strategy_results(ticker)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)

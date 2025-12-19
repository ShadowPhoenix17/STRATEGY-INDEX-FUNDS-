import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from strategy import QuantSystem

class Backtester:
    def __init__(self, signals):
        self.df = signals.copy()

    def run(self):
        """Ejecuta la simulación de retornos."""
        # Retornos diarios del activo
        self.df['Market_Returns'] = self.df['Close'].pct_change()
        
        # El retorno de la estrategia es la exposición de ayer por el retorno de hoy
        # (Se asume que la señal se genera al cierre de ayer para ejecutar hoy al cierre o similar simplificación)
        self.df['Strategy_Returns'] = self.df['Strategy_Exposure'].shift(1) * self.df['Market_Returns']
        
        # Eliminar NaNs iniciales
        self.df = self.df.dropna(subset=['Strategy_Returns'])
        
        # Retornos acumulados
        self.df['Cum_Market'] = (1 + self.df['Market_Returns']).cumprod()
        self.df['Cum_Strategy'] = (1 + self.df['Strategy_Returns']).cumprod()
        
        return self.df

    def performance_metrics(self):
        """Calcula métricas clave de rendimiento."""
        returns = self.df['Strategy_Returns']
        market_returns = self.df['Market_Returns']
        
        # Sharpe Ratio (asumiendo tasa libre de riesgo 0 para simplificar)
        sharpe = np.sqrt(252) * returns.mean() / returns.std()
        
        # Max Drawdown
        cum_returns = self.df['Cum_Strategy']
        running_max = cum_returns.cummax()
        drawdown = (cum_returns - running_max) / running_max
        max_dd = drawdown.min()
        
        # Beta vs Market
        covariance = returns.cov(market_returns)
        variance = market_returns.var()
        beta = covariance / variance
        
        # CAGR
        days = (self.df.index[-1] - self.df.index[0]).days
        years = days / 365.25
        total_return = cum_returns.iloc[-1] - 1
        cagr = (1 + total_return) ** (1/years) - 1

        print(f"\n--- Métricas de Rendimiento ({self.df.index[0].date()} a {self.df.index[-1].date()}) ---")
        print(f"CAGR: {cagr:.2%}")
        print(f"Sharpe Ratio: {sharpe:.2f}")
        print(f"Max Drawdown: {max_dd:.2%}")
        print(f"Beta vs Market: {beta:.2f}")
        
        return {
            "CAGR": cagr,
            "Sharpe": sharpe,
            "MaxDD": max_dd,
            "Beta": beta
        }

    def plot_results(self):
        """Visualiza la curva de equidad."""
        plt.figure(figsize=(12, 7))
        plt.plot(self.df['Cum_Market'], label='Benchmark (Buy & Hold)', color='gray', alpha=0.6)
        plt.plot(self.df['Cum_Strategy'], label='Quant Strategy', color='blue', linewidth=2)
        plt.yscale('log')
        plt.title('Equity Curve: Quant Strategy vs Benchmark')
        plt.legend()
        plt.grid(True, which="both", ls="-", alpha=0.2)
        plt.savefig('performance.png')
        print("Gráfico de rendimiento guardado como 'performance.png'")
        plt.show()

if __name__ == "__main__":
    # Inicializar sistema
    system = QuantSystem(ticker="SPY", start_date="2015-01-01")
    signals = system.generate_signals()
    
    # Ejecutar backtest
    bt = Backtester(signals)
    results = bt.run()
    metrics = bt.performance_metrics()
    bt.plot_results()

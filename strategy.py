import yfinance as yf
import pandas as pd
import numpy as np
from arch import arch_model
import matplotlib.pyplot as plt

class QuantSystem:
    def __init__(self, ticker="SPY", start_date="2010-01-01"):
        self.ticker = ticker
        self.start_date = start_date
        self.data = None
        self.signals = None

    def fetch_data(self):
        """Descarga datos históricos del ETF."""
        print(f"Descargando datos para {self.ticker}...")
        self.data = yf.download(self.ticker, start=self.start_date)
        # Asegurar que el índice sea de tipo Datetime y quitar timezone si existe
        self.data.index = pd.to_datetime(self.data.index).tz_localize(None)
        # Manejar multi-index si yfinance devuelve eso (versiones nuevas)
        if isinstance(self.data.columns, pd.MultiIndex):
            self.data.columns = self.data.columns.get_level_values(0)
        return self.data

    def calculate_indicators(self):
        """Calcula MA50, MA200 y Momentum trimestral."""
        if self.data is None:
            self.fetch_data()
        
        df = self.data.copy()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['MA200'] = df['Close'].rolling(window=200).mean()
        
        # Momentum trimestral (63 días hábiles aprox)
        df['Momentum'] = df['Close'] / df['Close'].shift(63) - 1
        
        self.data = df
        return df

    def estimate_volatility(self):
        """Estima volatilidad futura usando GARCH(1,1)."""
        if self.data is None:
            self.calculate_indicators()
            
        # Calcular retornos logarítmicos
        returns = 100 * self.data['Close'].pct_change().dropna()
        
        # Ajustar modelo GARCH(1,1)
        # Usamos una ventana rodante para evitar look-ahead bias o simplemente los datos hasta la fecha
        # Para simplificar en esta fase, calculamos la volatilidad condicional en toda la serie
        model = arch_model(returns, vol='Garch', p=1, q=1, dist='Normal')
        res = model.fit(disp='off')
        
        # Volatilidad anualizada (condicional)
        cond_vol = res.conditional_volatility
        # Re-indexar para que coincida con el dataframe original
        self.data['GARCH_Vol'] = cond_vol / 100 # Volatilidad diaria
        self.data['GARCH_Vol_Ann'] = self.data['GARCH_Vol'] * np.sqrt(252)
        
        return self.data

    def generate_signals(self):
        """Genera señales de compra/venta y tamaño de posición."""
        if self.data is None:
            self.calculate_indicators()
        elif 'MA200' not in self.data.columns:
            self.calculate_indicators()
        if 'GARCH_Vol' not in self.data.columns:
            self.estimate_volatility()
            
        df = self.data.copy()
        
        # Condición 1: MA50 > MA200
        # Condición 2: Momentum > 0
        df['Signal'] = np.where((df['MA50'] > df['MA200']) & (df['Momentum'] > 0), 1, 0)
        
        # Ajustar tamaño según volatilidad (Inverse Volatility Scaling)
        # Supongamos un objetivo de volatilidad del 15% anual
        target_vol = 0.15
        df['Pos_Size'] = target_vol / df['GARCH_Vol_Ann'].replace(0, np.nan)
        df['Pos_Size'] = df['Pos_Size'].fillna(0).clip(0, 1.5) # Max 150% apalancamiento si se desea, o clip a 1
        
        # Señal final combinada
        df['Strategy_Exposure'] = df['Signal'] * df['Pos_Size']
        
        # Stop-loss dinámico (±2 sigma histórico)
        # Calculamos la banda de stop loss basada en el precio de cierre y la volatilidad GARCH
        df['Stop_Loss'] = df['Close'] * (1 - 2 * df['GARCH_Vol'])
        
        self.signals = df
        return df

if __name__ == "__main__":
    system = QuantSystem(ticker="SPY")
    data = system.fetch_data()
    data = system.calculate_indicators()
    data = system.estimate_volatility()
    signals = system.generate_signals()
    
    print(signals.tail(10)[['Close', 'MA50', 'MA200', 'Momentum', 'Signal', 'Strategy_Exposure']])
    
    # Plotting simple
    plt.figure(figsize=(12, 6))
    plt.plot(signals['Close'], label='SPY Close', alpha=0.5)
    plt.plot(signals['MA50'], label='MA50')
    plt.plot(signals['MA200'], label='MA200')
    plt.title("SPY Strategy Indicators")
    plt.legend()
    plt.show()

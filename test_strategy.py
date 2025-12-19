import unittest
import pandas as pd
import numpy as np
from strategy import QuantSystem

class TestQuantSystem(unittest.TestCase):
    def setUp(self):
        # Generar datos sintéticos para testear
        dates = pd.date_range(start="2020-01-01", periods=300, freq='D')
        self.data = pd.DataFrame({
            'Open': np.linspace(100, 200, 300),
            'High': np.linspace(105, 205, 300),
            'Low': np.linspace(95, 195, 300),
            'Close': np.linspace(100, 200, 300),
            'Volume': 1000
        }, index=dates)
        
        self.system = QuantSystem(ticker="TEST")
        self.system.data = self.data

    def test_calculation_indicators(self):
        self.system.calculate_indicators()
        self.assertIn('MA50', self.system.data.columns)
        self.assertIn('MA200', self.system.data.columns)
        self.assertIn('Momentum', self.system.data.columns)

    def test_signal_generation(self):
        # En una tendencia puramente alcista como la de arriba:
        # MA50 será > MA200 y Momentum será > 0
        self.system.calculate_indicators()
        # Mock de volatilidad para no correr GARCH en test si no es necesario
        self.system.data['GARCH_Vol'] = 0.01
        self.system.data['GARCH_Vol_Ann'] = 0.15
        
        signals = self.system.generate_signals()
        last_signal = signals['Signal'].iloc[-1]
        self.assertEqual(last_signal, 1) # Debería ser BUY

if __name__ == '__main__':
    unittest.main()

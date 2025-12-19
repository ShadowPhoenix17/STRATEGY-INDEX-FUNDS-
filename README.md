# Sistema Quant para Fondos Indexados

Sistema de inversión cuantitativa diseñado para ETFs de mercado amplio (S&P 500, Nasdaq-100). Implementa una estrategia de seguimiento de tendencia de largo plazo con refinamiento de momentum y gestión de riesgo basada en volatilidad estocástica (GARCH).

## Características

- **趋势 (Tendencia):** Cruce de medias móviles (MA50/MA200).
- **Momentum:** Filtro de momentum trimestral para evitar señales falsas en mercados laterales.
- **Volatilidad:** Ajuste dinámico de la exposición basado en predicciones GARCH(1,1).
- **Riesgo:** Stop-loss dinámico a ±2σ de la volatilidad histórica.
- **Rebalanceo:** Ejecución mensual para mantener costos bajos.

## Estructura del Proyecto

- `strategy.py`: Lógica central de indicadores y señales.
- `backtest.py`: Motor de simulación y métricas.
- `app.py`: Servidor para el dashboard de visualización.
- `dashboard/`: Interfaz de usuario premium.

## Uso

1. Instalar dependencias: `pip install yfinance arch pandas numpy matplotlib plotly flask`
2. Ejecutar backtest: `python backtest.py`
3. Ver dashboard: `python app.py`

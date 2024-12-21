# Adding financial market data provided by QuantConnect
from AlgorithmImports import *

class MomentumStrategy(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2016, 1, 1)  # Start of the backtest
        self.SetEndDate(2024, 11, 25)  # End of the backtest
        self.SetCash(1000000)  # Initial capital in dollars
        self.spy = self.AddEquity("SPXL", Resolution.Daily).Symbol  # Adding the SPXL ETF
        self.Portfolio.MarginCallModel = MarginCallModel.Null  # Disabling margin calls
        self.UniverseSettings.Leverage = 1  # No additional global leverage

        self.Schedule.On(self.DateRules.EveryDay(), self.TimeRules.At(15, 58), self.Rebalance)

        self.state = 0

        # Main chart: Price evolution and moving averages
        price_chart = Chart("Price Evolution")
        self.AddChart(price_chart)
        price_chart.AddSeries(Series("SPXL Closing Price", SeriesType.Line, '$', color=Color.Green))
        price_chart.AddSeries(Series("Long-Term Average", SeriesType.Line, '$', color=Color.Blue))
        price_chart.AddSeries(Series("Short-Term Average", SeriesType.Line, '$', color=Color.Orange))

        # Secondary chart: Signals and volatility
        signal_chart = Chart("Signals and Volatility")
        self.AddChart(signal_chart)
        signal_chart.AddSeries(Series(name="Buy Signal", type=SeriesType.Scatter, unit='$', color=Color.DarkGreen, symbol=ScatterMarkerSymbol.TRIANGLE))
        signal_chart.AddSeries(Series(name="Sell Signal", type=SeriesType.Scatter, unit='$', color=Color.DarkRed, symbol=ScatterMarkerSymbol.TRIANGLE_DOWN))
        signal_chart.AddSeries(Series("Upper Volatility", SeriesType.Line, '$', color=Color.Gray))
        signal_chart.AddSeries(Series("Lower Volatility", SeriesType.Line, '$', color=Color.Gray))

        self.volatility_period = 27  # Window used to calculate volatility
        self.rolling_window = RollingWindow[float](self.volatility_period)

    def Rebalance(self):
        history = self.History(self.spy, self.volatility_period + 1, Resolution.Daily)
        if history.empty or history.isnull().values.any():
            self.Debug("No historical data available.")
            return

        self.data = history['close'].unstack(level=0)
        for i in range(len(self.data)):
            self.rolling_window.Add(self.data.iloc[i])

        # Calculate long-term and short-term averages
        long_term_mean = self.data.mean().item() * (self.data.std().item() * np.sqrt(252 / len(self.data)))
        short_term_mean = self.data[:5].mean().item() * (self.data[:5].std().item() * np.sqrt(252 / len(self.data[:5])))

        # Update charts
        self.Plot("Price Evolution", "SPXL Closing Price", self.data.iloc[-1])
        self.Plot("Price Evolution", "Long-Term Average", long_term_mean)
        self.Plot("Price Evolution", "Short-Term Average", short_term_mean)

        # Calculate and display volatility bounds
        if self.rolling_window.IsReady:
            returns = [self.rolling_window[i] / self.rolling_window[i + 1] - 1 for i in range(self.volatility_period - 1)]
            volatility = np.std(returns) * 500
            upper_bar = 100 + volatility / 2
            lower_bar = 100 - volatility / 2

            # Add volatility zone for clarity
            for i in range(len(returns)):
                self.Plot("Signals and Volatility", "Upper Volatility", upper_bar)
                self.Plot("Signals and Volatility", "Lower Volatility", lower_bar)

        # Check volatility and liquidate if too high
        if (self.data.std().item() * np.sqrt(252 / len(self.data))) > 22.5:
            self.Debug("Volatility too high. Liquidating positions.")
            self.Liquidate()
            return

        # Logic for buy and sell signals
        self.previous_state = self.state
        if short_term_mean < long_term_mean and self.state != 1:
            self.state = 1
        elif short_term_mean > long_term_mean and self.state != -1:
            self.state = -1

        # Update signals and execute trades
        if self.previous_state != self.state:
            self.Trade()

    def Trade(self):
        if self.state == 1:
            self.Plot("Signals and Volatility", "Buy Signal", self.data.iloc[-1])
            self.Liquidate()
            self.SetHoldings("SPXL", 1.0)  # Maximum allocation for a total leverage of 3x

        if self.state == -1:
            self.Plot("Signals and Volatility", "Sell Signal", self.data.iloc[-1])
            self.Liquidate()

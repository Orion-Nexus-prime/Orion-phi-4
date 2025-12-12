"""
Tests for trading components
"""
import pytest
from src.trading.portfolio_manager import PortfolioManager, Position
from src.trading.risk_manager import RiskManager
from src.trading.strategies.quantum_mean_reversion import QuantumMeanReversionStrategy
from src.trading.strategies.neuro_synthetic import NeuroSyntheticStrategy
from src.trading.strategies.dark_pool_predictor import DarkPoolPredictorStrategy
from src.trading.strategies.volatility_arbitrage import VolatilityArbitrageStrategy


class TestPortfolioManager:
    """Test Portfolio Manager"""
    
    def test_initialization(self):
        """Test portfolio manager initialization"""
        portfolio = PortfolioManager(initial_capital=100000)
        assert portfolio.initial_capital == 100000
        assert portfolio.cash == 100000
        assert len(portfolio.positions) == 0
    
    def test_open_position(self):
        """Test opening a position"""
        portfolio = PortfolioManager(initial_capital=100000)
        
        result = portfolio.open_position(
            symbol='BTC/USDT',
            side='long',
            quantity=1.0,
            price=50000
        )
        
        assert result['success'] is True
        assert 'BTC/USDT' in portfolio.positions
        assert portfolio.cash == 50000
    
    def test_close_position(self):
        """Test closing a position"""
        portfolio = PortfolioManager(initial_capital=100000)
        
        # Open position
        portfolio.open_position('BTC/USDT', 'long', 1.0, 50000)
        
        # Close position with profit
        result = portfolio.close_position('BTC/USDT', 52000)
        
        assert result['success'] is True
        assert result['pnl'] == 2000
        assert 'BTC/USDT' not in portfolio.positions
    
    def test_portfolio_value(self):
        """Test portfolio value calculation"""
        portfolio = PortfolioManager(initial_capital=100000)
        
        # Open position
        portfolio.open_position('BTC/USDT', 'long', 1.0, 50000)
        
        # Update price
        portfolio.update_position_price('BTC/USDT', 51000)
        
        # Total value should be cash + position value
        expected_value = 50000 + 51000  # cash + position
        assert portfolio.get_total_value() == expected_value


class TestRiskManager:
    """Test Risk Manager"""
    
    def test_initialization(self):
        """Test risk manager initialization"""
        risk_mgr = RiskManager()
        assert risk_mgr.max_portfolio_risk == 0.02
        assert risk_mgr.max_position_risk == 0.01
    
    def test_position_size_calculation(self):
        """Test position size calculation"""
        risk_mgr = RiskManager()
        
        position_size = risk_mgr.calculate_position_size(
            capital=100000,
            entry_price=50000,
            stop_loss_price=49000
        )
        
        # Should risk 1% of capital ($1000)
        # Risk per unit = 50000 - 49000 = 1000
        # Position size = 1000 / 1000 = 1.0
        assert position_size == 1.0
    
    def test_stop_loss_calculation(self):
        """Test stop loss calculation"""
        risk_mgr = RiskManager()
        
        # Buy side
        stop_loss = risk_mgr.calculate_stop_loss(50000, 'buy')
        assert stop_loss == 50000 * 0.95  # 5% below entry
        
        # Sell side
        stop_loss = risk_mgr.calculate_stop_loss(50000, 'sell')
        assert stop_loss == 50000 * 1.05  # 5% above entry
    
    def test_position_risk_check(self):
        """Test position risk checking"""
        risk_mgr = RiskManager()
        
        # Position within limits
        result = risk_mgr.check_position_risk(
            position_value=10000,
            portfolio_value=100000,
            current_drawdown=0.05
        )
        
        assert result['approved'] is True
        assert result['concentration'] == 0.1
        
        # Position exceeds concentration limit
        result = risk_mgr.check_position_risk(
            position_value=25000,
            portfolio_value=100000,
            current_drawdown=0.05
        )
        
        assert result['approved'] is False


class TestQuantumMeanReversion:
    """Test Quantum Mean Reversion Strategy"""
    
    def test_initialization(self):
        """Test strategy initialization"""
        strategy = QuantumMeanReversionStrategy()
        assert strategy.lookback_period == 20
        assert strategy.std_threshold == 2.0
    
    def test_analysis(self):
        """Test strategy analysis"""
        strategy = QuantumMeanReversionStrategy()
        
        # Create trending up data
        prices = list(range(100, 120)) + [119, 118, 117, 116, 115]
        
        market_data = {
            'prices': prices,
            'volumes': [1000] * len(prices)
        }
        
        result = strategy.analyze(market_data)
        
        assert result['success'] is True
        assert 'signal' in result
        assert 'z_score' in result


class TestNeuroSynthetic:
    """Test Neuro Synthetic Strategy"""
    
    def test_initialization(self):
        """Test strategy initialization"""
        strategy = NeuroSyntheticStrategy()
        assert strategy.sequence_length == 50
        assert len(strategy.hidden_layers) == 3
    
    def test_analysis(self):
        """Test strategy analysis"""
        strategy = NeuroSyntheticStrategy()
        
        prices = [100 + i * 0.5 for i in range(60)]
        
        market_data = {
            'prices': prices,
            'volumes': [1000] * len(prices)
        }
        
        result = strategy.analyze(market_data)
        
        assert result['success'] is True
        assert 'signal' in result
        assert 'prediction_scores' in result


class TestDarkPoolPredictor:
    """Test Dark Pool Predictor Strategy"""
    
    def test_initialization(self):
        """Test strategy initialization"""
        strategy = DarkPoolPredictorStrategy()
        assert strategy.detection_threshold == 0.7
    
    def test_analysis(self):
        """Test strategy analysis"""
        strategy = DarkPoolPredictorStrategy()
        
        # Simulate dark pool: high volume, low price change
        prices = [100] * 15 + [101, 100.5, 100.2, 100.8, 100.5]
        volumes = [1000] * 15 + [5000, 4500, 4800, 5200, 4900]  # Volume spike
        
        market_data = {
            'prices': prices,
            'volumes': volumes
        }
        
        result = strategy.analyze(market_data)
        
        assert result['success'] is True
        assert 'signal' in result
        assert 'dark_pool_score' in result


class TestVolatilityArbitrage:
    """Test Volatility Arbitrage Strategy"""
    
    def test_initialization(self):
        """Test strategy initialization"""
        strategy = VolatilityArbitrageStrategy()
        assert strategy.historical_vol_window == 30
    
    def test_analysis(self):
        """Test strategy analysis"""
        strategy = VolatilityArbitrageStrategy()
        
        # Create data with changing volatility
        import numpy as np
        prices = list(100 + np.cumsum(np.random.randn(40) * 2))
        
        market_data = {
            'prices': prices,
            'volumes': [1000] * len(prices)
        }
        
        result = strategy.analyze(market_data)
        
        assert result['success'] is True
        assert 'signal' in result
        assert 'historical_vol' in result
        assert 'implied_vol' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

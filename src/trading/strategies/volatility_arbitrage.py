"""
Volatility Arbitrage v4 - Exploits volatility mispricings
"""
import numpy as np
from typing import Any, Dict, List, Optional
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class VolatilityArbitrageStrategy:
    """
    Strategy that exploits differences between implied and realized volatility
    Trades when volatility is mispriced
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = get_logger(__name__)
        self.config = config or {}
        
        # Strategy parameters
        self.implied_vol_threshold = get_config(
            'trading', 'strategies.volatility_arbitrage.implied_vol_threshold', 0.15
        )
        self.historical_vol_window = get_config(
            'trading', 'strategies.volatility_arbitrage.historical_vol_window', 30
        )
        
        self.logger.info("Volatility Arbitrage Strategy v4 initialized")
    
    def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data for volatility arbitrage opportunities
        
        Args:
            market_data: Market data with prices
            
        Returns:
            Trading signal
        """
        try:
            prices = market_data.get('prices', [])
            
            if len(prices) < self.historical_vol_window:
                return {
                    'success': False,
                    'error': 'Insufficient data',
                    'signal': 'hold'
                }
            
            # Calculate historical volatility
            historical_vol = self._calculate_historical_volatility(prices)
            
            # Estimate implied volatility (in real system, get from options)
            implied_vol = self._estimate_implied_volatility(prices, historical_vol)
            
            # Calculate volatility spread
            vol_spread = implied_vol - historical_vol
            
            # Detect volatility regime
            vol_regime = self._detect_volatility_regime(prices)
            
            # Generate signal
            signal = self._generate_signal(
                vol_spread, historical_vol, implied_vol, vol_regime, prices[-1]
            )
            
            return {
                'success': True,
                'signal': signal['action'],
                'confidence': signal['confidence'],
                'entry_price': signal.get('entry_price'),
                'stop_loss': signal.get('stop_loss'),
                'take_profit': signal.get('take_profit'),
                'rationale': signal.get('rationale'),
                'historical_vol': float(historical_vol),
                'implied_vol': float(implied_vol),
                'vol_spread': float(vol_spread),
                'vol_regime': vol_regime,
                'strategy': 'volatility_arbitrage'
            }
            
        except Exception as e:
            self.logger.error(f"Error in strategy analysis: {e}")
            return {
                'success': False,
                'error': str(e),
                'signal': 'hold'
            }
    
    def _calculate_historical_volatility(self, prices: List[float]) -> float:
        """
        Calculate historical volatility
        
        Args:
            prices: Price history
            
        Returns:
            Annualized volatility
        """
        prices_array = np.array(prices[-self.historical_vol_window:])
        
        # Calculate log returns
        log_returns = np.log(prices_array[1:] / prices_array[:-1])
        
        # Calculate standard deviation
        vol = np.std(log_returns)
        
        # Annualize (assuming daily data, 252 trading days)
        annualized_vol = vol * np.sqrt(252)
        
        return float(annualized_vol)
    
    def _estimate_implied_volatility(
        self,
        prices: List[float],
        historical_vol: float
    ) -> float:
        """
        Estimate implied volatility
        In production, this would come from options data
        
        Args:
            prices: Price history
            historical_vol: Historical volatility
            
        Returns:
            Estimated implied volatility
        """
        # For demonstration, add random component to historical vol
        # In reality, parse from options market
        
        prices_array = np.array(prices[-10:])
        recent_vol = np.std(np.diff(prices_array) / prices_array[:-1]) * np.sqrt(252)
        
        # Implied vol tends to be higher than realized (volatility risk premium)
        implied_vol = historical_vol * 1.2 + np.random.normal(0, 0.05)
        
        # Also factor in recent volatility changes
        implied_vol = (implied_vol * 0.7 + recent_vol * 0.3)
        
        return float(max(implied_vol, 0.05))  # Minimum 5%
    
    def _detect_volatility_regime(self, prices: List[float]) -> str:
        """
        Detect current volatility regime
        
        Args:
            prices: Price history
            
        Returns:
            Regime ('low_vol', 'normal', 'high_vol')
        """
        # Calculate recent volatility
        recent_prices = np.array(prices[-20:])
        returns = np.diff(recent_prices) / recent_prices[:-1]
        recent_vol = np.std(returns) * np.sqrt(252)
        
        # Calculate longer-term volatility
        long_prices = np.array(prices[-self.historical_vol_window:])
        long_returns = np.diff(long_prices) / long_prices[:-1]
        long_vol = np.std(long_returns) * np.sqrt(252)
        
        # Classify regime
        if recent_vol < long_vol * 0.7:
            return 'low_vol'
        elif recent_vol > long_vol * 1.3:
            return 'high_vol'
        else:
            return 'normal'
    
    def _generate_signal(
        self,
        vol_spread: float,
        historical_vol: float,
        implied_vol: float,
        vol_regime: str,
        current_price: float
    ) -> Dict[str, Any]:
        """
        Generate trading signal based on volatility analysis
        
        Args:
            vol_spread: Implied - Historical volatility
            historical_vol: Historical volatility
            implied_vol: Implied volatility
            vol_regime: Volatility regime
            current_price: Current price
            
        Returns:
            Trading signal
        """
        # Volatility arbitrage strategies:
        # 1. Sell volatility (short straddle) when implied > historical
        # 2. Buy volatility (long straddle) when implied < historical
        
        if vol_spread > self.implied_vol_threshold:
            # Implied vol is significantly higher than realized
            # Sell volatility (range-bound trading)
            return {
                'action': 'sell',
                'confidence': min(abs(vol_spread) / 0.5, 1.0),
                'entry_price': current_price,
                'stop_loss': current_price * (1 + historical_vol * 0.5),
                'take_profit': current_price * (1 - historical_vol * 0.3),
                'rationale': f'Implied vol ({implied_vol:.2%}) > Historical vol ({historical_vol:.2%}), sell overpriced volatility'
            }
        
        elif vol_spread < -self.implied_vol_threshold:
            # Implied vol is significantly lower than realized
            # Buy volatility (expect breakout)
            return {
                'action': 'buy',
                'confidence': min(abs(vol_spread) / 0.5, 1.0),
                'entry_price': current_price,
                'stop_loss': current_price * (1 - historical_vol * 0.5),
                'take_profit': current_price * (1 + historical_vol * 0.3),
                'rationale': f'Implied vol ({implied_vol:.2%}) < Historical vol ({historical_vol:.2%}), buy underpriced volatility'
            }
        
        elif vol_regime == 'low_vol':
            # Low volatility regime - expect mean reversion or breakout
            return {
                'action': 'buy',
                'confidence': 0.6,
                'entry_price': current_price,
                'stop_loss': current_price * 0.97,
                'take_profit': current_price * 1.05,
                'rationale': 'Low volatility regime, positioning for potential breakout'
            }
        
        else:
            # No clear arbitrage opportunity
            return {
                'action': 'hold',
                'confidence': 0.5,
                'rationale': 'No significant volatility mispricing detected'
            }
    
    def _calculate_volatility_smile(self, prices: List[float]) -> Dict[str, float]:
        """
        Calculate volatility smile (different vols for different strikes)
        Simplified version for demonstration
        
        Args:
            prices: Price history
            
        Returns:
            Volatility smile data
        """
        current_price = prices[-1]
        base_vol = self._calculate_historical_volatility(prices)
        
        # Volatility smile: higher vol for out-of-money options
        smile = {
            'atm': base_vol,  # At-the-money
            'otm_call': base_vol * 1.1,  # Out-of-money call
            'otm_put': base_vol * 1.15,  # Out-of-money put
            'itm_call': base_vol * 0.95,  # In-the-money call
            'itm_put': base_vol * 0.95   # In-the-money put
        }
        
        return smile
    
    def _calculate_vega(self, implied_vol: float, time_to_expiry: float = 30) -> float:
        """
        Calculate option vega (sensitivity to volatility)
        
        Args:
            implied_vol: Implied volatility
            time_to_expiry: Days to expiration
            
        Returns:
            Vega value
        """
        # Simplified vega calculation
        # In reality, use Black-Scholes
        time_factor = np.sqrt(time_to_expiry / 365)
        vega = 0.4 * time_factor
        
        return float(vega)
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get current strategy parameters"""
        return {
            'implied_vol_threshold': self.implied_vol_threshold,
            'historical_vol_window': self.historical_vol_window
        }

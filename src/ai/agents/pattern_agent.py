"""
DarkHunter Analytics Agent - Pattern recognition and market analysis
"""
import numpy as np
from typing import Any, Dict, List
from src.ai.agents.base_agent import BaseAgent, AgentType, AgentStatus


class PatternAnalyticsAgent(BaseAgent):
    """Agent for detecting patterns and anomalies in market data"""
    
    def __init__(self, agent_id: str = "pattern_analytics", config: Dict[str, Any] = None):
        super().__init__(agent_id, AgentType.PATTERN_ANALYTICS, config)
        self.pattern_threshold = config.get('threshold', 0.7) if config else 0.7
        self.known_patterns = self._initialize_patterns()
        
    def _initialize_patterns(self) -> Dict[str, Any]:
        """Initialize known pattern templates"""
        return {
            'head_shoulders': {'confidence': 0.0, 'detected': False},
            'double_top': {'confidence': 0.0, 'detected': False},
            'double_bottom': {'confidence': 0.0, 'detected': False},
            'triangle': {'confidence': 0.0, 'detected': False},
            'flag': {'confidence': 0.0, 'detected': False}
        }
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data for pattern detection"""
        try:
            self.status = AgentStatus.PROCESSING
            
            prices = data.get('prices', [])
            volumes = data.get('volumes', [])
            
            # Detect patterns
            patterns = self._detect_patterns(prices)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(prices, volumes)
            
            # Calculate dark pool activity score
            dark_pool_score = self._analyze_dark_pool_activity(volumes)
            
            self.status = AgentStatus.IDLE
            return {
                'success': True,
                'patterns': patterns,
                'anomalies': anomalies,
                'dark_pool_score': dark_pool_score,
                'agent': self.agent_id
            }
        except Exception as e:
            await self._handle_error(e)
            return {'success': False, 'error': str(e)}
    
    async def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data for patterns"""
        try:
            prices = market_data.get('prices', [])
            volumes = market_data.get('volumes', [])
            
            if not prices:
                return {'success': False, 'error': 'No price data'}
            
            # Comprehensive pattern analysis
            patterns = self._detect_patterns(prices)
            trend = self._detect_trend(prices)
            support_resistance = self._find_support_resistance(prices)
            
            # Generate trading signal
            signal = self._generate_signal(patterns, trend)
            
            return {
                'success': True,
                'patterns': patterns,
                'trend': trend,
                'support_resistance': support_resistance,
                'signal': signal,
                'confidence': self._calculate_pattern_confidence(patterns)
            }
        except Exception as e:
            await self._handle_error(e)
            return {'success': False, 'error': str(e)}
    
    def _detect_patterns(self, prices: List[float]) -> Dict[str, Any]:
        """Detect chart patterns"""
        if len(prices) < 10:
            return self.known_patterns.copy()
        
        prices_array = np.array(prices[-50:])  # Last 50 prices
        patterns = {}
        
        # Head and shoulders detection
        patterns['head_shoulders'] = self._detect_head_shoulders(prices_array)
        
        # Double top/bottom detection
        patterns['double_top'] = self._detect_double_top(prices_array)
        patterns['double_bottom'] = self._detect_double_bottom(prices_array)
        
        # Triangle pattern
        patterns['triangle'] = self._detect_triangle(prices_array)
        
        # Flag pattern
        patterns['flag'] = self._detect_flag(prices_array)
        
        return patterns
    
    def _detect_head_shoulders(self, prices: np.ndarray) -> Dict[str, Any]:
        """Detect head and shoulders pattern"""
        if len(prices) < 15:
            return {'confidence': 0.0, 'detected': False}
        
        # Simplified detection using peak analysis
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(prices, distance=5)
        
        if len(peaks) >= 3:
            # Check if middle peak is highest
            if peaks[1] > peaks[0] and peaks[1] > peaks[2]:
                confidence = 0.7
                return {'confidence': confidence, 'detected': True}
        
        return {'confidence': 0.0, 'detected': False}
    
    def _detect_double_top(self, prices: np.ndarray) -> Dict[str, Any]:
        """Detect double top pattern"""
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(prices, distance=5)
        
        if len(peaks) >= 2:
            # Check if two peaks are similar height
            peak_values = prices[peaks[-2:]]
            if np.abs(peak_values[0] - peak_values[1]) / peak_values[0] < 0.02:
                return {'confidence': 0.75, 'detected': True}
        
        return {'confidence': 0.0, 'detected': False}
    
    def _detect_double_bottom(self, prices: np.ndarray) -> Dict[str, Any]:
        """Detect double bottom pattern"""
        from scipy.signal import find_peaks
        troughs, _ = find_peaks(-prices, distance=5)
        
        if len(troughs) >= 2:
            # Check if two troughs are similar depth
            trough_values = prices[troughs[-2:]]
            if np.abs(trough_values[0] - trough_values[1]) / trough_values[0] < 0.02:
                return {'confidence': 0.75, 'detected': True}
        
        return {'confidence': 0.0, 'detected': False}
    
    def _detect_triangle(self, prices: np.ndarray) -> Dict[str, Any]:
        """Detect triangle pattern"""
        if len(prices) < 20:
            return {'confidence': 0.0, 'detected': False}
        
        # Simplified: check if volatility is decreasing
        early_vol = np.std(prices[:len(prices)//2])
        late_vol = np.std(prices[len(prices)//2:])
        
        if late_vol < early_vol * 0.7:
            return {'confidence': 0.65, 'detected': True}
        
        return {'confidence': 0.0, 'detected': False}
    
    def _detect_flag(self, prices: np.ndarray) -> Dict[str, Any]:
        """Detect flag pattern"""
        if len(prices) < 15:
            return {'confidence': 0.0, 'detected': False}
        
        # Check for strong move followed by consolidation
        first_third = prices[:len(prices)//3]
        last_third = prices[len(prices)//3:]
        
        move = abs(first_third[-1] - first_third[0]) / first_third[0]
        consolidation = np.std(last_third) / np.mean(last_third)
        
        if move > 0.05 and consolidation < 0.02:
            return {'confidence': 0.7, 'detected': True}
        
        return {'confidence': 0.0, 'detected': False}
    
    def _detect_anomalies(self, prices: List[float], volumes: List[float]) -> List[Dict[str, Any]]:
        """Detect anomalies in price and volume"""
        anomalies = []
        
        if len(prices) < 10:
            return anomalies
        
        prices_array = np.array(prices[-20:])
        
        # Price spike detection
        mean_price = np.mean(prices_array)
        std_price = np.std(prices_array)
        
        for i, price in enumerate(prices_array[-5:]):
            if abs(price - mean_price) > 2 * std_price:
                anomalies.append({
                    'type': 'price_spike',
                    'index': len(prices) - 5 + i,
                    'value': float(price),
                    'severity': float(abs(price - mean_price) / std_price)
                })
        
        return anomalies
    
    def _analyze_dark_pool_activity(self, volumes: List[float]) -> float:
        """Analyze potential dark pool activity"""
        if len(volumes) < 10:
            return 0.0
        
        volumes_array = np.array(volumes[-20:])
        mean_vol = np.mean(volumes_array)
        recent_vol = np.mean(volumes_array[-5:])
        
        # High recent volume compared to average suggests dark pool
        ratio = recent_vol / (mean_vol + 1e-10)
        score = float(min(ratio / 2.0, 1.0))
        
        return score
    
    def _detect_trend(self, prices: List[float]) -> str:
        """Detect overall trend"""
        if len(prices) < 10:
            return 'neutral'
        
        prices_array = np.array(prices[-20:])
        
        # Simple linear regression
        x = np.arange(len(prices_array))
        slope = np.polyfit(x, prices_array, 1)[0]
        
        if slope > 0.01:
            return 'uptrend'
        elif slope < -0.01:
            return 'downtrend'
        return 'neutral'
    
    def _find_support_resistance(self, prices: List[float]) -> Dict[str, float]:
        """Find support and resistance levels"""
        if len(prices) < 20:
            return {'support': 0.0, 'resistance': 0.0}
        
        prices_array = np.array(prices[-50:])
        
        from scipy.signal import find_peaks
        
        # Find peaks (resistance) and troughs (support)
        peaks, _ = find_peaks(prices_array, distance=5)
        troughs, _ = find_peaks(-prices_array, distance=5)
        
        resistance = float(np.mean(prices_array[peaks])) if len(peaks) > 0 else float(np.max(prices_array))
        support = float(np.mean(prices_array[troughs])) if len(troughs) > 0 else float(np.min(prices_array))
        
        return {'support': support, 'resistance': resistance}
    
    def _generate_signal(self, patterns: Dict[str, Any], trend: str) -> str:
        """Generate trading signal from patterns"""
        bullish_count = sum(1 for p in ['double_bottom'] if patterns.get(p, {}).get('detected', False))
        bearish_count = sum(1 for p in ['double_top', 'head_shoulders'] if patterns.get(p, {}).get('detected', False))
        
        if bullish_count > bearish_count and trend == 'uptrend':
            return 'buy'
        elif bearish_count > bullish_count and trend == 'downtrend':
            return 'sell'
        return 'hold'
    
    def _calculate_pattern_confidence(self, patterns: Dict[str, Any]) -> float:
        """Calculate overall confidence in pattern detection"""
        confidences = [p.get('confidence', 0.0) for p in patterns.values()]
        return float(np.mean(confidences)) if confidences else 0.0

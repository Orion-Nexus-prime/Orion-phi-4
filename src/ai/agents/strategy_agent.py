"""
Strategy Analyzer Agent - Evaluates and optimizes trading strategies
"""
import numpy as np
from typing import Any, Dict, List
from src.ai.agents.base_agent import BaseAgent, AgentType, AgentStatus


class StrategyAnalyzerAgent(BaseAgent):
    """Agent for analyzing and optimizing trading strategies"""
    
    def __init__(self, agent_id: str = "strategy_analyzer", config: Dict[str, Any] = None):
        super().__init__(agent_id, AgentType.STRATEGY_ANALYZER, config)
        self.strategy_weights = {
            'quantum_mean_reversion': 0.30,
            'neuro_synthetic': 0.25,
            'dark_pool_predictor': 0.25,
            'volatility_arbitrage': 0.20
        }
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process strategy analysis"""
        try:
            self.status = AgentStatus.PROCESSING
            
            strategy_signals = data.get('strategy_signals', {})
            
            # Evaluate each strategy
            evaluations = self._evaluate_strategies(strategy_signals)
            
            # Calculate combined signal
            combined_signal = self._calculate_combined_signal(evaluations)
            
            # Assess overall strategy health
            health = self._assess_strategy_health(evaluations)
            
            self.status = AgentStatus.IDLE
            return {
                'success': True,
                'evaluations': evaluations,
                'combined_signal': combined_signal,
                'health': health,
                'agent': self.agent_id
            }
        except Exception as e:
            await self._handle_error(e)
            return {'success': False, 'error': str(e)}
    
    async def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze which strategies to use"""
        try:
            # Analyze market conditions
            market_regime = self._detect_market_regime(market_data)
            
            # Adjust strategy weights based on regime
            optimal_weights = self._optimize_weights(market_regime)
            
            # Generate strategy recommendations
            recommendations = self._generate_recommendations(
                market_regime, optimal_weights
            )
            
            return {
                'success': True,
                'market_regime': market_regime,
                'optimal_weights': optimal_weights,
                'recommendations': recommendations
            }
        except Exception as e:
            await self._handle_error(e)
            return {'success': False, 'error': str(e)}
    
    def _evaluate_strategies(self, strategy_signals: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate individual strategy performance"""
        evaluations = {}
        
        for strategy_name, signal_data in strategy_signals.items():
            if not isinstance(signal_data, dict):
                continue
            
            confidence = signal_data.get('confidence', 0.5)
            signal = signal_data.get('signal', 'hold')
            
            # Evaluate strategy quality
            quality_score = self._calculate_quality_score(signal_data)
            
            evaluations[strategy_name] = {
                'confidence': confidence,
                'signal': signal,
                'quality_score': quality_score,
                'weight': self.strategy_weights.get(strategy_name, 0.25)
            }
        
        return evaluations
    
    def _calculate_quality_score(self, signal_data: Dict[str, Any]) -> float:
        """Calculate quality score for a strategy signal"""
        confidence = signal_data.get('confidence', 0.5)
        
        # Check for additional quality indicators
        has_stop_loss = 'stop_loss' in signal_data
        has_take_profit = 'take_profit' in signal_data
        has_rationale = 'rationale' in signal_data
        
        quality = confidence * 0.6
        quality += 0.1 if has_stop_loss else 0
        quality += 0.1 if has_take_profit else 0
        quality += 0.2 if has_rationale else 0
        
        return float(np.clip(quality, 0.0, 1.0))
    
    def _calculate_combined_signal(self, evaluations: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate weighted combined signal from all strategies"""
        buy_score = 0.0
        sell_score = 0.0
        hold_score = 0.0
        total_weight = 0.0
        
        for strategy_name, evaluation in evaluations.items():
            signal = evaluation['signal']
            weight = evaluation['weight']
            confidence = evaluation['confidence']
            
            weighted_score = weight * confidence
            total_weight += weight
            
            if signal == 'buy':
                buy_score += weighted_score
            elif signal == 'sell':
                sell_score += weighted_score
            else:
                hold_score += weighted_score
        
        # Normalize
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
            hold_score /= total_weight
        
        # Determine final signal
        max_score = max(buy_score, sell_score, hold_score)
        if max_score == buy_score and buy_score > 0.6:
            final_signal = 'buy'
        elif max_score == sell_score and sell_score > 0.6:
            final_signal = 'sell'
        else:
            final_signal = 'hold'
        
        return {
            'signal': final_signal,
            'buy_score': float(buy_score),
            'sell_score': float(sell_score),
            'hold_score': float(hold_score),
            'confidence': float(max_score)
        }
    
    def _assess_strategy_health(self, evaluations: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall health of strategy system"""
        if not evaluations:
            return {'status': 'unknown', 'score': 0.0}
        
        quality_scores = [e['quality_score'] for e in evaluations.values()]
        avg_quality = np.mean(quality_scores)
        
        # Check for conflicts
        signals = [e['signal'] for e in evaluations.values()]
        signal_agreement = signals.count(max(set(signals), key=signals.count)) / len(signals)
        
        # Overall health score
        health_score = (avg_quality * 0.6 + signal_agreement * 0.4)
        
        if health_score > 0.7:
            status = 'healthy'
        elif health_score > 0.5:
            status = 'moderate'
        else:
            status = 'unhealthy'
        
        return {
            'status': status,
            'score': float(health_score),
            'avg_quality': float(avg_quality),
            'signal_agreement': float(signal_agreement)
        }
    
    def _detect_market_regime(self, market_data: Dict[str, Any]) -> str:
        """Detect current market regime"""
        prices = market_data.get('prices', [])
        if len(prices) < 20:
            return 'unknown'
        
        prices_array = np.array(prices[-20:])
        
        # Calculate volatility
        returns = np.diff(prices_array) / prices_array[:-1]
        volatility = np.std(returns)
        
        # Calculate trend
        trend = np.polyfit(range(len(prices_array)), prices_array, 1)[0]
        
        # Classify regime
        if volatility > 0.03:  # High volatility
            if abs(trend) > 0.01:
                return 'volatile_trending'
            else:
                return 'volatile_ranging'
        else:  # Low volatility
            if abs(trend) > 0.01:
                return 'trending'
            else:
                return 'ranging'
    
    def _optimize_weights(self, market_regime: str) -> Dict[str, float]:
        """Optimize strategy weights for current market regime"""
        weights = self.strategy_weights.copy()
        
        if market_regime == 'ranging':
            # Mean reversion works well in ranging markets
            weights['quantum_mean_reversion'] = 0.40
            weights['neuro_synthetic'] = 0.20
            weights['dark_pool_predictor'] = 0.20
            weights['volatility_arbitrage'] = 0.20
            
        elif market_regime == 'trending':
            # Trend following and momentum strategies
            weights['quantum_mean_reversion'] = 0.20
            weights['neuro_synthetic'] = 0.35
            weights['dark_pool_predictor'] = 0.25
            weights['volatility_arbitrage'] = 0.20
            
        elif market_regime == 'volatile_ranging':
            # Volatility strategies
            weights['quantum_mean_reversion'] = 0.25
            weights['neuro_synthetic'] = 0.20
            weights['dark_pool_predictor'] = 0.20
            weights['volatility_arbitrage'] = 0.35
            
        elif market_regime == 'volatile_trending':
            # Balanced approach
            weights['quantum_mean_reversion'] = 0.25
            weights['neuro_synthetic'] = 0.30
            weights['dark_pool_predictor'] = 0.25
            weights['volatility_arbitrage'] = 0.20
        
        return weights
    
    def _generate_recommendations(
        self, 
        market_regime: str, 
        optimal_weights: Dict[str, float]
    ) -> List[str]:
        """Generate strategy recommendations"""
        recommendations = []
        
        recommendations.append(f"Market regime detected: {market_regime}")
        
        # Find highest weighted strategy
        best_strategy = max(optimal_weights.items(), key=lambda x: x[1])
        recommendations.append(
            f"Primary strategy: {best_strategy[0]} (weight: {best_strategy[1]:.2f})"
        )
        
        # Risk recommendations
        if 'volatile' in market_regime:
            recommendations.append("Reduce position sizes due to high volatility")
            recommendations.append("Widen stop losses")
        else:
            recommendations.append("Normal position sizing acceptable")
        
        return recommendations

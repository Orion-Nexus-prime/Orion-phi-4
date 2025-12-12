"""
Poker AI Logic Agent - Game theory and negotiation strategies
"""
import numpy as np
from typing import Any, Dict, List
from src.ai.agents.base_agent import BaseAgent, AgentType, AgentStatus


class PokerLogicAgent(BaseAgent):
    """Agent using game theory and poker logic for trading decisions"""
    
    def __init__(self, agent_id: str = "poker_logic", config: Dict[str, Any] = None):
        super().__init__(agent_id, AgentType.POKER_LOGIC, config)
        self.risk_appetite = config.get('risk_appetite', 0.5) if config else 0.5
        
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data using game theory"""
        try:
            self.status = AgentStatus.PROCESSING
            
            # Calculate game theory metrics
            nash_equilibrium = self._calculate_nash_equilibrium(data)
            bluff_score = self._calculate_bluff_score(data)
            expected_value = self._calculate_expected_value(data)
            
            # Determine optimal strategy
            strategy = self._determine_strategy(nash_equilibrium, bluff_score, expected_value)
            
            self.status = AgentStatus.IDLE
            return {
                'success': True,
                'nash_equilibrium': nash_equilibrium,
                'bluff_score': bluff_score,
                'expected_value': expected_value,
                'strategy': strategy,
                'agent': self.agent_id
            }
        except Exception as e:
            await self._handle_error(e)
            return {'success': False, 'error': str(e)}
    
    async def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market using poker/game theory principles"""
        try:
            prices = market_data.get('prices', [])
            if not prices:
                return {'success': False, 'error': 'No price data'}
            
            # Calculate hand strength (market position)
            hand_strength = self._calculate_hand_strength(prices)
            
            # Calculate pot odds (risk/reward)
            pot_odds = self._calculate_pot_odds(prices)
            
            # Determine if we should bluff (contrarian play)
            should_bluff = self._should_bluff(hand_strength, pot_odds)
            
            # Calculate position advantage
            position_advantage = self._calculate_position_advantage(prices)
            
            # Generate poker-style decision
            decision = self._make_poker_decision(
                hand_strength, pot_odds, should_bluff, position_advantage
            )
            
            return {
                'success': True,
                'hand_strength': hand_strength,
                'pot_odds': pot_odds,
                'should_bluff': should_bluff,
                'position_advantage': position_advantage,
                'decision': decision,
                'confidence': self._calculate_confidence(hand_strength, pot_odds)
            }
        except Exception as e:
            await self._handle_error(e)
            return {'success': False, 'error': str(e)}
    
    def _calculate_nash_equilibrium(self, data: Dict[str, Any]) -> float:
        """Calculate Nash equilibrium point"""
        # Simplified Nash equilibrium for two-player game
        # In trading: player vs market
        
        player_payoff = data.get('expected_return', 0.5)
        market_payoff = 1.0 - player_payoff
        
        # Nash equilibrium when neither can improve by changing strategy
        equilibrium = (player_payoff + market_payoff) / 2.0
        return float(equilibrium)
    
    def _calculate_bluff_score(self, data: Dict[str, Any]) -> float:
        """Calculate optimal bluffing frequency"""
        # In poker, optimal bluffing depends on pot odds and fold equity
        fold_equity = data.get('volatility', 0.5)
        pot_odds = data.get('risk_reward', 0.5)
        
        # Optimal bluff frequency based on game theory
        bluff_score = fold_equity / (fold_equity + pot_odds + 1e-10)
        return float(np.clip(bluff_score, 0.0, 1.0))
    
    def _calculate_expected_value(self, data: Dict[str, Any]) -> float:
        """Calculate expected value of action"""
        win_probability = data.get('win_probability', 0.5)
        win_amount = data.get('potential_gain', 1.0)
        lose_probability = 1.0 - win_probability
        lose_amount = data.get('potential_loss', 1.0)
        
        ev = (win_probability * win_amount) - (lose_probability * lose_amount)
        return float(ev)
    
    def _determine_strategy(self, nash: float, bluff: float, ev: float) -> str:
        """Determine optimal strategy based on metrics"""
        if ev > 0.5 and nash > 0.6:
            return 'aggressive'
        elif ev < -0.2 or nash < 0.4:
            return 'defensive'
        elif bluff > 0.7:
            return 'bluff'
        return 'balanced'
    
    def _calculate_hand_strength(self, prices: List[float]) -> float:
        """Calculate 'hand strength' from market position"""
        if len(prices) < 10:
            return 0.5
        
        prices_array = np.array(prices[-20:])
        
        # Calculate momentum as hand strength
        returns = np.diff(prices_array) / prices_array[:-1]
        momentum = np.mean(returns)
        
        # Normalize to 0-1 range (0 = weak, 1 = strong)
        strength = (momentum + 0.1) / 0.2  # Assuming typical returns in -10% to +10%
        return float(np.clip(strength, 0.0, 1.0))
    
    def _calculate_pot_odds(self, prices: List[float]) -> float:
        """Calculate pot odds (risk/reward ratio)"""
        if len(prices) < 2:
            return 0.5
        
        current_price = prices[-1]
        avg_price = np.mean(prices[-20:])
        
        # Potential gain vs potential loss
        upside = max(current_price - avg_price, 0) / current_price
        downside = max(avg_price - current_price, 0) / current_price
        
        if upside + downside == 0:
            return 0.5
        
        pot_odds = upside / (upside + downside)
        return float(pot_odds)
    
    def _should_bluff(self, hand_strength: float, pot_odds: float) -> bool:
        """Determine if we should make a contrarian (bluff) play"""
        # Bluff when hand is weak but pot odds are good
        # Or when hand is strong but market thinks we're weak
        
        bluff_threshold = 0.3
        
        if hand_strength < bluff_threshold and pot_odds > 0.6:
            # Weak hand, good odds - semi-bluff
            return True
        elif hand_strength > 0.7 and pot_odds < 0.4:
            # Strong hand disguised as weak - value bet
            return False
        
        # Random bluffing based on risk appetite
        return np.random.random() < (self.risk_appetite * 0.2)
    
    def _calculate_position_advantage(self, prices: List[float]) -> float:
        """Calculate position advantage (like table position in poker)"""
        if len(prices) < 10:
            return 0.5
        
        # Early position (disadvantage) vs late position (advantage)
        # In trading: being ahead of trend vs following trend
        
        prices_array = np.array(prices[-10:])
        trend = np.polyfit(range(len(prices_array)), prices_array, 1)[0]
        
        # Positive trend = good position
        position = (trend + 0.1) / 0.2
        return float(np.clip(position, 0.0, 1.0))
    
    def _make_poker_decision(
        self, 
        hand_strength: float, 
        pot_odds: float, 
        should_bluff: bool,
        position_advantage: float
    ) -> str:
        """Make final poker-style trading decision"""
        
        # Strong hand + good odds = bet/raise (buy)
        if hand_strength > 0.7 and pot_odds > 0.6:
            return 'aggressive_buy'
        
        # Good odds but weak hand = call (hold)
        elif pot_odds > 0.6 and hand_strength > 0.4:
            return 'conservative_buy'
        
        # Bluffing scenario
        elif should_bluff and position_advantage > 0.5:
            return 'bluff_buy'
        
        # Weak hand + bad odds = fold (sell)
        elif hand_strength < 0.3 and pot_odds < 0.4:
            return 'sell'
        
        # Everything else = check (hold)
        return 'hold'
    
    def _calculate_confidence(self, hand_strength: float, pot_odds: float) -> float:
        """Calculate confidence in decision"""
        # Confidence is high when both hand strength and pot odds align
        confidence = (hand_strength * pot_odds) ** 0.5
        return float(confidence)

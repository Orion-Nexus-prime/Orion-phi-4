"""
Quantum Orchestrator - Multi-AI Consensus Mechanism
"""
import asyncio
import numpy as np
from typing import Any, Dict, List, Optional
from datetime import datetime
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class QuantumOrchestrator:
    """
    Orchestrates multiple AI agents and reaches consensus on trading decisions
    Uses weighted voting and quantum-inspired consensus algorithms
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)
        self.consensus_threshold = get_config('system', 'orchestrator.consensus_threshold', 0.7)
        self.voting_method = get_config('system', 'orchestrator.voting_method', 'weighted')
        self.timeout = get_config('system', 'orchestrator.timeout_seconds', 10)
        
        # Agent priority weights
        self.agent_weights = {
            'quantum_finance': 0.25,
            'pattern_analytics': 0.25,
            'poker_logic': 0.20,
            'voice_ai': 0.05,
            'strategy_analyzer': 0.25
        }
        
        self.logger.info("Quantum Orchestrator initialized")
    
    async def orchestrate(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrate consensus from multiple agent results
        
        Args:
            agent_results: Dictionary of agent_id -> result
            
        Returns:
            Orchestrated consensus decision
        """
        self.logger.info("Orchestrating agent consensus...")
        
        # Filter valid results
        valid_results = self._filter_valid_results(agent_results)
        
        if not valid_results:
            return {
                'success': False,
                'error': 'No valid agent results',
                'consensus': 'hold',
                'confidence': 0.0
            }
        
        # Calculate consensus based on voting method
        if self.voting_method == 'weighted':
            consensus = self._weighted_consensus(valid_results)
        elif self.voting_method == 'majority':
            consensus = self._majority_consensus(valid_results)
        elif self.voting_method == 'quantum':
            consensus = self._quantum_consensus(valid_results)
        else:
            consensus = self._weighted_consensus(valid_results)
        
        # Add metadata
        consensus['timestamp'] = datetime.now().isoformat()
        consensus['agent_count'] = len(valid_results)
        consensus['voting_method'] = self.voting_method
        
        return consensus
    
    def _filter_valid_results(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Filter out invalid or error results"""
        valid = {}
        
        for agent_id, result in agent_results.items():
            if isinstance(result, dict) and result.get('success', False):
                valid[agent_id] = result
            else:
                self.logger.warning(f"Filtering out invalid result from {agent_id}")
        
        return valid
    
    def _weighted_consensus(self, valid_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate weighted consensus"""
        signal_scores = {'buy': 0.0, 'sell': 0.0, 'hold': 0.0}
        total_weight = 0.0
        
        for agent_id, result in valid_results.items():
            # Get agent weight
            weight = self.agent_weights.get(agent_id, 0.1)
            
            # Get signal and confidence
            signal = result.get('signal', 'hold')
            confidence = result.get('confidence', 0.5)
            
            # Calculate weighted score
            weighted_score = weight * confidence
            
            if signal in signal_scores:
                signal_scores[signal] += weighted_score
            
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            for signal in signal_scores:
                signal_scores[signal] /= total_weight
        
        # Determine consensus
        max_signal = max(signal_scores, key=signal_scores.get)
        max_score = signal_scores[max_signal]
        
        # Check if consensus threshold is met
        meets_threshold = max_score >= self.consensus_threshold
        
        return {
            'success': True,
            'consensus': max_signal,
            'confidence': float(max_score),
            'meets_threshold': meets_threshold,
            'signal_scores': {k: float(v) for k, v in signal_scores.items()},
            'method': 'weighted'
        }
    
    def _majority_consensus(self, valid_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate majority consensus (simple voting)"""
        signal_counts = {'buy': 0, 'sell': 0, 'hold': 0}
        
        for agent_id, result in valid_results.items():
            signal = result.get('signal', 'hold')
            if signal in signal_counts:
                signal_counts[signal] += 1
        
        # Determine majority
        total_votes = sum(signal_counts.values())
        max_signal = max(signal_counts, key=signal_counts.get)
        max_votes = signal_counts[max_signal]
        
        confidence = max_votes / total_votes if total_votes > 0 else 0.0
        meets_threshold = confidence >= self.consensus_threshold
        
        return {
            'success': True,
            'consensus': max_signal,
            'confidence': float(confidence),
            'meets_threshold': meets_threshold,
            'signal_counts': signal_counts,
            'method': 'majority'
        }
    
    def _quantum_consensus(self, valid_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate quantum-inspired consensus
        Uses quantum superposition and entanglement concepts
        """
        # Initialize quantum state vector for each signal
        states = {'buy': [], 'sell': [], 'hold': []}
        
        for agent_id, result in valid_results.items():
            signal = result.get('signal', 'hold')
            confidence = result.get('confidence', 0.5)
            weight = self.agent_weights.get(agent_id, 0.1)
            
            # Create quantum amplitude
            amplitude = np.sqrt(confidence * weight)
            
            if signal in states:
                states[signal].append(amplitude)
        
        # Calculate probability amplitudes
        probabilities = {}
        total_prob = 0.0
        
        for signal, amplitudes in states.items():
            if amplitudes:
                # Quantum superposition: sum of amplitudes
                superposition = sum(amplitudes)
                # Probability: square of amplitude
                prob = superposition ** 2
                probabilities[signal] = prob
                total_prob += prob
        
        # Normalize probabilities
        if total_prob > 0:
            for signal in probabilities:
                probabilities[signal] /= total_prob
        else:
            probabilities = {'buy': 0.33, 'sell': 0.33, 'hold': 0.34}
        
        # Quantum measurement (collapse to definite state)
        max_signal = max(probabilities, key=probabilities.get)
        max_prob = probabilities[max_signal]
        
        # Apply quantum entanglement factor (correlation between agents)
        entanglement_factor = self._calculate_entanglement(valid_results)
        adjusted_confidence = max_prob * entanglement_factor
        
        meets_threshold = adjusted_confidence >= self.consensus_threshold
        
        return {
            'success': True,
            'consensus': max_signal,
            'confidence': float(adjusted_confidence),
            'meets_threshold': meets_threshold,
            'probabilities': {k: float(v) for k, v in probabilities.items()},
            'entanglement_factor': float(entanglement_factor),
            'method': 'quantum'
        }
    
    def _calculate_entanglement(self, valid_results: Dict[str, Any]) -> float:
        """
        Calculate entanglement factor (correlation) between agents
        Higher correlation = stronger consensus
        """
        if len(valid_results) < 2:
            return 1.0
        
        signals = [r.get('signal', 'hold') for r in valid_results.values()]
        
        # Calculate agreement ratio
        most_common_signal = max(set(signals), key=signals.count)
        agreement_count = signals.count(most_common_signal)
        agreement_ratio = agreement_count / len(signals)
        
        # Entanglement increases with agreement
        entanglement = 0.5 + (agreement_ratio * 0.5)
        
        return entanglement
    
    async def resolve_conflicts(self, agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve conflicts when agents disagree
        
        Args:
            agent_results: Dictionary of agent results
            
        Returns:
            Conflict resolution result
        """
        self.logger.info("Resolving agent conflicts...")
        
        # Get consensus
        consensus = await self.orchestrate(agent_results)
        
        # If consensus is weak, apply conflict resolution
        if not consensus.get('meets_threshold', False):
            self.logger.warning("Weak consensus detected, applying conflict resolution")
            
            # Default to hold when uncertain
            consensus['consensus'] = 'hold'
            consensus['conflict_resolved'] = True
            consensus['resolution_method'] = 'default_to_hold'
        
        return consensus
    
    def update_agent_weights(self, agent_id: str, new_weight: float):
        """Update weight for specific agent"""
        if agent_id in self.agent_weights:
            old_weight = self.agent_weights[agent_id]
            self.agent_weights[agent_id] = new_weight
            self.logger.info(f"Updated weight for {agent_id}: {old_weight} -> {new_weight}")
            
            # Normalize weights to sum to 1.0
            total = sum(self.agent_weights.values())
            for aid in self.agent_weights:
                self.agent_weights[aid] /= total
    
    def get_weights(self) -> Dict[str, float]:
        """Get current agent weights"""
        return self.agent_weights.copy()
    
    async def adaptive_orchestrate(
        self, 
        agent_results: Dict[str, Any],
        market_regime: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Adaptive orchestration that adjusts based on market regime
        
        Args:
            agent_results: Dictionary of agent results
            market_regime: Optional market regime ('trending', 'ranging', etc.)
            
        Returns:
            Orchestrated result with adaptive weighting
        """
        # Adjust weights based on market regime
        if market_regime:
            original_weights = self.agent_weights.copy()
            self._adjust_weights_for_regime(market_regime)
        
        # Orchestrate with adjusted weights
        result = await self.orchestrate(agent_results)
        
        # Restore original weights
        if market_regime:
            self.agent_weights = original_weights
        
        return result
    
    def _adjust_weights_for_regime(self, market_regime: str):
        """Adjust agent weights based on market regime"""
        if market_regime == 'ranging':
            # Mean reversion and pattern detection more important
            self.agent_weights['quantum_finance'] = 0.30
            self.agent_weights['pattern_analytics'] = 0.30
            self.agent_weights['poker_logic'] = 0.15
            self.agent_weights['strategy_analyzer'] = 0.20
            
        elif market_regime == 'trending':
            # Momentum and strategy analysis more important
            self.agent_weights['quantum_finance'] = 0.20
            self.agent_weights['pattern_analytics'] = 0.20
            self.agent_weights['poker_logic'] = 0.20
            self.agent_weights['strategy_analyzer'] = 0.35
            
        elif 'volatile' in market_regime:
            # Risk management (poker logic) more important
            self.agent_weights['quantum_finance'] = 0.20
            self.agent_weights['pattern_analytics'] = 0.25
            self.agent_weights['poker_logic'] = 0.30
            self.agent_weights['strategy_analyzer'] = 0.20
        
        # Normalize
        total = sum(self.agent_weights.values())
        for agent_id in self.agent_weights:
            self.agent_weights[agent_id] /= total

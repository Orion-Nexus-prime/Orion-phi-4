"""
Orion Phi-4 Engine - Multi-Agent System Manager
"""
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.ai.agents.base_agent import BaseAgent, AgentType, AgentMessage, AgentStatus
from src.ai.agents.quantum_agent import QuantumFinanceAgent
from src.ai.agents.pattern_agent import PatternAnalyticsAgent
from src.ai.agents.poker_agent import PokerLogicAgent
from src.ai.agents.voice_agent import VoiceAIAgent
from src.ai.agents.strategy_agent import StrategyAnalyzerAgent
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class AgentManager:
    """Manages lifecycle of all agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = get_logger(f"{__name__}.AgentManager")
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.agent_id}")
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """Get all agents of a specific type"""
        return [a for a in self.agents.values() if a.agent_type == agent_type]
    
    async def start_all(self):
        """Start all registered agents"""
        tasks = [agent.start() for agent in self.agents.values()]
        await asyncio.gather(*tasks)
        self.logger.info("All agents started")
    
    async def stop_all(self):
        """Stop all registered agents"""
        tasks = [agent.stop() for agent in self.agents.values()]
        await asyncio.gather(*tasks)
        self.logger.info("All agents stopped")
    
    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            agent_id: agent.get_status() 
            for agent_id, agent in self.agents.items()
        }


class OrionPhi4Engine:
    """
    Main Multi-Agent AI System Engine
    Coordinates all agents and manages their interactions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = get_logger(__name__)
        self.agent_manager = AgentManager()
        self.running = False
        
        # Initialize agents
        self._initialize_agents()
        
        self.logger.info("Orion Phi-4 Engine initialized")
    
    def _initialize_agents(self):
        """Initialize all AI agents"""
        # Quantum Finance Agent
        if get_config('system', 'agents.quantum_finance.enabled', True):
            quantum_agent = QuantumFinanceAgent(config=self.config)
            self.agent_manager.register_agent(quantum_agent)
        
        # Pattern Analytics Agent
        if get_config('system', 'agents.pattern_analytics.enabled', True):
            pattern_agent = PatternAnalyticsAgent(config=self.config)
            self.agent_manager.register_agent(pattern_agent)
        
        # Poker Logic Agent
        if get_config('system', 'agents.poker_logic.enabled', True):
            poker_agent = PokerLogicAgent(config=self.config)
            self.agent_manager.register_agent(poker_agent)
        
        # Voice AI Agent
        if get_config('system', 'agents.voice_ai.enabled', False):
            voice_agent = VoiceAIAgent(config=self.config)
            self.agent_manager.register_agent(voice_agent)
        
        # Strategy Analyzer Agent
        if get_config('system', 'agents.strategy_analyzer.enabled', True):
            strategy_agent = StrategyAnalyzerAgent(config=self.config)
            self.agent_manager.register_agent(strategy_agent)
        
        self.logger.info(f"Initialized {len(self.agent_manager.agents)} agents")
    
    async def start(self):
        """Start the multi-agent system"""
        self.logger.info("Starting Orion Phi-4 Engine...")
        await self.agent_manager.start_all()
        self.running = True
        self.logger.info("Orion Phi-4 Engine started successfully")
    
    async def stop(self):
        """Stop the multi-agent system"""
        self.logger.info("Stopping Orion Phi-4 Engine...")
        self.running = False
        await self.agent_manager.stop_all()
        self.logger.info("Orion Phi-4 Engine stopped")
    
    async def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data using all agents
        
        Args:
            market_data: Market data to analyze
            
        Returns:
            Combined analysis from all agents
        """
        if not self.running:
            return {'error': 'Engine not running'}
        
        self.logger.info("Analyzing market data with all agents...")
        
        # Collect analyses from all agents
        agent_analyses = {}
        
        # Run all agent analyses concurrently
        tasks = []
        agent_ids = []
        
        for agent_id, agent in self.agent_manager.agents.items():
            if agent.status != AgentStatus.DISABLED:
                tasks.append(agent.analyze(market_data))
                agent_ids.append(agent_id)
        
        # Gather results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for agent_id, result in zip(agent_ids, results):
            if isinstance(result, Exception):
                self.logger.error(f"Agent {agent_id} error: {result}")
                agent_analyses[agent_id] = {'error': str(result)}
            else:
                agent_analyses[agent_id] = result
        
        # Combine analyses
        combined = self._combine_analyses(agent_analyses)
        
        return combined
    
    def _combine_analyses(self, agent_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Combine analyses from all agents into final decision"""
        # Count signals
        signals = {'buy': 0, 'sell': 0, 'hold': 0}
        confidences = []
        
        for agent_id, analysis in agent_analyses.items():
            if not analysis.get('success', False):
                continue
            
            signal = analysis.get('signal', 'hold')
            if signal in signals:
                signals[signal] += 1
            
            confidence = analysis.get('confidence', 0.5)
            confidences.append(confidence)
        
        # Determine consensus
        total_signals = sum(signals.values())
        if total_signals == 0:
            consensus_signal = 'hold'
            consensus_strength = 0.5
        else:
            max_signal = max(signals, key=signals.get)
            consensus_signal = max_signal
            consensus_strength = signals[max_signal] / total_signals
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
        
        return {
            'consensus_signal': consensus_signal,
            'consensus_strength': consensus_strength,
            'average_confidence': avg_confidence,
            'signal_distribution': signals,
            'agent_analyses': agent_analyses,
            'timestamp': datetime.now().isoformat()
        }
    
    async def process_data(self, data: Dict[str, Any], agent_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Process data with specific agents or all agents
        
        Args:
            data: Data to process
            agent_ids: Optional list of specific agent IDs to use
            
        Returns:
            Processing results
        """
        if not self.running:
            return {'error': 'Engine not running'}
        
        # Determine which agents to use
        if agent_ids:
            agents = [self.agent_manager.get_agent(aid) for aid in agent_ids]
            agents = [a for a in agents if a is not None]
        else:
            agents = list(self.agent_manager.agents.values())
        
        # Process with each agent
        results = {}
        for agent in agents:
            if agent.status != AgentStatus.DISABLED:
                try:
                    result = await agent.process(data)
                    results[agent.agent_id] = result
                except Exception as e:
                    self.logger.error(f"Error processing with agent {agent.agent_id}: {e}")
                    results[agent.agent_id] = {'error': str(e)}
        
        return results
    
    async def send_message(self, sender_id: str, receiver_id: str, message_type: str, content: Dict[str, Any]):
        """Send message between agents"""
        sender = self.agent_manager.get_agent(sender_id)
        receiver = self.agent_manager.get_agent(receiver_id)
        
        if not sender or not receiver:
            self.logger.error(f"Invalid sender or receiver: {sender_id} -> {receiver_id}")
            return
        
        message = AgentMessage(
            sender=sender_id,
            receiver=receiver_id,
            message_type=message_type,
            content=content,
            timestamp=datetime.now()
        )
        
        await receiver.send_message(message)
        self.logger.debug(f"Message sent: {message}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        return {
            'running': self.running,
            'agents': self.agent_manager.get_all_status(),
            'timestamp': datetime.now().isoformat()
        }
    
    async def health_check(self) -> bool:
        """Check system health"""
        if not self.running:
            return False
        
        # Check all agents
        health_checks = []
        for agent in self.agent_manager.agents.values():
            health_checks.append(await agent.health_check())
        
        # System is healthy if at least 50% of agents are healthy
        return sum(health_checks) / len(health_checks) >= 0.5 if health_checks else False

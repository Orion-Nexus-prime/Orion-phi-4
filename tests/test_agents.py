"""
Tests for AI agents
"""
import pytest
import asyncio
from src.ai.agents.quantum_agent import QuantumFinanceAgent
from src.ai.agents.pattern_agent import PatternAnalyticsAgent
from src.ai.agents.poker_agent import PokerLogicAgent
from src.ai.agents.strategy_agent import StrategyAnalyzerAgent
from src.ai.multi_agent_system import OrionPhi4Engine


class TestQuantumAgent:
    """Test Quantum Finance Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = QuantumFinanceAgent()
        assert agent.agent_id == "quantum_finance"
        assert agent.quantum_iterations == 100
    
    @pytest.mark.asyncio
    async def test_agent_analyze(self):
        """Test agent analysis"""
        agent = QuantumFinanceAgent()
        
        market_data = {
            'prices': [100, 101, 102, 103, 102, 101, 100, 99, 98, 99, 100] * 2
        }
        
        result = await agent.analyze(market_data)
        
        assert result['success'] is True
        assert 'prediction' in result
        assert 'signal' in result


class TestPatternAgent:
    """Test Pattern Analytics Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = PatternAnalyticsAgent()
        assert agent.agent_id == "pattern_analytics"
    
    @pytest.mark.asyncio
    async def test_agent_analyze(self):
        """Test agent analysis"""
        agent = PatternAnalyticsAgent()
        
        market_data = {
            'prices': [100, 101, 102, 103, 102, 101, 100, 99, 98, 99, 100] * 5,
            'volumes': [1000, 1100, 1200, 1150, 1000, 950, 900, 850, 900, 950, 1000] * 5
        }
        
        result = await agent.analyze(market_data)
        
        assert result['success'] is True
        assert 'patterns' in result
        assert 'trend' in result


class TestPokerAgent:
    """Test Poker Logic Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = PokerLogicAgent()
        assert agent.agent_id == "poker_logic"
    
    @pytest.mark.asyncio
    async def test_agent_analyze(self):
        """Test agent analysis"""
        agent = PokerLogicAgent()
        
        market_data = {
            'prices': [100, 101, 102, 103, 102, 101, 100, 99, 98, 99, 100] * 2
        }
        
        result = await agent.analyze(market_data)
        
        assert result['success'] is True
        assert 'hand_strength' in result
        assert 'decision' in result


class TestStrategyAgent:
    """Test Strategy Analyzer Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Test agent can be initialized"""
        agent = StrategyAnalyzerAgent()
        assert agent.agent_id == "strategy_analyzer"
    
    @pytest.mark.asyncio
    async def test_agent_analyze(self):
        """Test agent analysis"""
        agent = StrategyAnalyzerAgent()
        
        market_data = {
            'prices': [100, 101, 102, 103, 102, 101, 100, 99, 98, 99, 100] * 3
        }
        
        result = await agent.analyze(market_data)
        
        assert result['success'] is True
        assert 'market_regime' in result


class TestMultiAgentSystem:
    """Test Multi-Agent System"""
    
    @pytest.mark.asyncio
    async def test_engine_initialization(self):
        """Test engine can be initialized"""
        engine = OrionPhi4Engine()
        assert engine is not None
        assert len(engine.agent_manager.agents) > 0
    
    @pytest.mark.asyncio
    async def test_engine_start_stop(self):
        """Test engine start and stop"""
        engine = OrionPhi4Engine()
        
        await engine.start()
        assert engine.running is True
        
        await engine.stop()
        assert engine.running is False
    
    @pytest.mark.asyncio
    async def test_market_analysis(self):
        """Test market analysis with all agents"""
        engine = OrionPhi4Engine()
        await engine.start()
        
        market_data = {
            'prices': [100, 101, 102, 103, 102, 101, 100, 99, 98, 99, 100] * 5,
            'volumes': [1000, 1100, 1200, 1150, 1000, 950, 900, 850, 900, 950, 1000] * 5
        }
        
        result = await engine.analyze_market(market_data)
        
        assert 'consensus_signal' in result
        assert 'agent_analyses' in result
        
        await engine.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

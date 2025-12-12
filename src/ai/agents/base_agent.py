"""
Base Agent class for all AI agents in the Orion Phi-4 system
"""
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AgentType(Enum):
    """Types of agents in the system"""
    QUANTUM_FINANCE = "quantum_finance"
    PATTERN_ANALYTICS = "pattern_analytics"
    POKER_LOGIC = "poker_logic"
    VOICE_AI = "voice_ai"
    STRATEGY_ANALYZER = "strategy_analyzer"


class AgentStatus(Enum):
    """Agent status states"""
    IDLE = "idle"
    PROCESSING = "processing"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class AgentMessage:
    """Message format for agent communication"""
    sender: str
    receiver: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 1
    
    def __str__(self):
        return f"AgentMessage(from={self.sender}, to={self.receiver}, type={self.message_type})"


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.logger = get_logger(f"{__name__}.{agent_id}")
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        
    async def start(self):
        """Start the agent"""
        self._running = True
        self.status = AgentStatus.IDLE
        self.logger.info(f"Agent {self.agent_id} started")
        
    async def stop(self):
        """Stop the agent"""
        self._running = False
        self.status = AgentStatus.DISABLED
        self.logger.info(f"Agent {self.agent_id} stopped")
        
    async def send_message(self, message: AgentMessage):
        """Send a message to another agent"""
        await self.message_queue.put(message)
        
    async def receive_message(self) -> Optional[AgentMessage]:
        """Receive a message from the queue"""
        try:
            message = await asyncio.wait_for(self.message_queue.get(), timeout=0.1)
            return message
        except asyncio.TimeoutError:
            return None
            
    @abstractmethod
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process data and return results
        
        Args:
            data: Input data to process
            
        Returns:
            Processing results
        """
        pass
    
    @abstractmethod
    async def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data
        
        Args:
            market_data: Market data to analyze
            
        Returns:
            Analysis results
        """
        pass
    
    async def health_check(self) -> bool:
        """Check if agent is healthy"""
        return self._running and self.status != AgentStatus.ERROR
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type.value,
            'status': self.status.value,
            'running': self._running,
            'queue_size': self.message_queue.qsize()
        }
    
    async def _handle_error(self, error: Exception):
        """Handle errors in agent processing"""
        self.status = AgentStatus.ERROR
        self.logger.error(f"Error in agent {self.agent_id}: {error}", exc_info=True)

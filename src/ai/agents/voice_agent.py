"""
Voice AI Agent - Voice commands and alerting system
"""
from typing import Any, Dict
from src.ai.agents.base_agent import BaseAgent, AgentType, AgentStatus


class VoiceAIAgent(BaseAgent):
    """Agent for voice commands and audio alerts"""
    
    def __init__(self, agent_id: str = "voice_ai", config: Dict[str, Any] = None):
        super().__init__(agent_id, AgentType.VOICE_AI, config)
        self.voice_enabled = False
        self.tts_engine = None
        self._initialize_voice()
        
    def _initialize_voice(self):
        """Initialize voice synthesis (if available)"""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.voice_enabled = True
            self.logger.info("Voice synthesis initialized")
        except Exception as e:
            self.logger.warning(f"Voice synthesis not available: {e}")
            self.voice_enabled = False
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process voice commands or alerts"""
        try:
            self.status = AgentStatus.PROCESSING
            
            command_type = data.get('type', 'alert')
            message = data.get('message', '')
            
            if command_type == 'alert':
                result = await self._speak_alert(message)
            elif command_type == 'status':
                result = await self._speak_status(data)
            else:
                result = {'spoken': False, 'reason': 'Unknown command type'}
            
            self.status = AgentStatus.IDLE
            return {
                'success': True,
                'result': result,
                'agent': self.agent_id
            }
        except Exception as e:
            await self._handle_error(e)
            return {'success': False, 'error': str(e)}
    
    async def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data and generate voice alerts"""
        try:
            # Generate appropriate voice alerts based on market conditions
            alerts = []
            
            if 'signal' in market_data:
                signal = market_data['signal']
                if signal in ['buy', 'sell']:
                    alert_msg = f"Trading signal: {signal}"
                    alerts.append(alert_msg)
                    if self.voice_enabled:
                        await self._speak_alert(alert_msg)
            
            if 'risk_level' in market_data:
                risk = market_data['risk_level']
                if risk == 'high':
                    alert_msg = "Warning: High risk level detected"
                    alerts.append(alert_msg)
                    if self.voice_enabled:
                        await self._speak_alert(alert_msg)
            
            return {
                'success': True,
                'alerts': alerts,
                'voice_enabled': self.voice_enabled
            }
        except Exception as e:
            await self._handle_error(e)
            return {'success': False, 'error': str(e)}
    
    async def _speak_alert(self, message: str) -> Dict[str, Any]:
        """Speak an alert message"""
        if not self.voice_enabled:
            return {'spoken': False, 'reason': 'Voice not enabled'}
        
        try:
            self.logger.info(f"Speaking alert: {message}")
            # Note: pyttsx3 is synchronous, but we keep the async interface
            self.tts_engine.say(message)
            self.tts_engine.runAndWait()
            return {'spoken': True, 'message': message}
        except Exception as e:
            self.logger.error(f"Error speaking alert: {e}")
            return {'spoken': False, 'error': str(e)}
    
    async def _speak_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Speak system status"""
        status_items = []
        
        if 'portfolio_value' in data:
            status_items.append(f"Portfolio value: {data['portfolio_value']}")
        
        if 'open_positions' in data:
            status_items.append(f"{data['open_positions']} open positions")
        
        if 'daily_pnl' in data:
            pnl = data['daily_pnl']
            pnl_status = "profit" if pnl > 0 else "loss"
            status_items.append(f"Daily {pnl_status}: {abs(pnl)}")
        
        message = ". ".join(status_items)
        return await self._speak_alert(message)
    
    def set_voice_enabled(self, enabled: bool):
        """Enable or disable voice functionality"""
        if enabled and not self.voice_enabled:
            self._initialize_voice()
        elif not enabled:
            self.voice_enabled = False
            if self.tts_engine:
                try:
                    self.tts_engine.stop()
                except:
                    pass

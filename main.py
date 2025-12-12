"""
Orion Phi-4 Main Entry Point
Multi-Agent AI Trading System
"""
import asyncio
import signal
import sys
from typing import Optional

from src.utils.logger import get_logger
from src.utils.config_manager import config_manager
from src.ai.multi_agent_system import OrionPhi4Engine
from src.ai.orchestrator import QuantumOrchestrator
from src.core.trading_engine import get_trading_engine
from src.core.memory_manager import get_memory_manager
from src.data.market_feeds import get_market_feed
from src.trading.portfolio_manager import get_portfolio_manager
from src.trading.risk_manager import get_risk_manager
from src.trading.strategies.quantum_mean_reversion import QuantumMeanReversionStrategy
from src.trading.strategies.neuro_synthetic import NeuroSyntheticStrategy
from src.trading.strategies.dark_pool_predictor import DarkPoolPredictorStrategy
from src.trading.strategies.volatility_arbitrage import VolatilityArbitrageStrategy

logger = get_logger(__name__)


class OrionPhi4System:
    """Main Orion Phi-4 Trading System"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.running = False
        
        # Initialize components
        self.logger.info("=" * 80)
        self.logger.info("Initializing Orion Phi-4 Multi-Agent AI Trading System")
        self.logger.info("=" * 80)
        
        # Core components
        self.ai_engine = OrionPhi4Engine()
        self.orchestrator = QuantumOrchestrator()
        self.trading_engine = get_trading_engine()
        self.memory_manager = get_memory_manager()
        self.market_feed = get_market_feed()
        self.portfolio = get_portfolio_manager()
        self.risk_manager = get_risk_manager()
        
        # Trading strategies
        self.strategies = {
            'quantum_mean_reversion': QuantumMeanReversionStrategy(),
            'neuro_synthetic': NeuroSyntheticStrategy(),
            'dark_pool_predictor': DarkPoolPredictorStrategy(),
            'volatility_arbitrage': VolatilityArbitrageStrategy()
        }
        
        self.logger.info("All components initialized successfully")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("Shutdown signal received")
        self.running = False
    
    async def start(self):
        """Start all system components"""
        try:
            self.logger.info("Starting Orion Phi-4 System...")
            
            # Start components
            await self.ai_engine.start()
            await self.trading_engine.start()
            await self.memory_manager.start()
            await self.market_feed.start()
            
            self.running = True
            
            self.logger.info("=" * 80)
            self.logger.info("Orion Phi-4 System is ONLINE")
            self.logger.info("=" * 80)
            
            # Display initial status
            await self._display_status()
            
            # Main loop
            await self._main_loop()
            
        except Exception as e:
            self.logger.error(f"Error starting system: {e}", exc_info=True)
            raise
    
    async def stop(self):
        """Stop all system components"""
        self.logger.info("Stopping Orion Phi-4 System...")
        
        self.running = False
        
        # Stop components
        await self.market_feed.stop()
        await self.memory_manager.stop()
        await self.trading_engine.stop()
        await self.ai_engine.stop()
        
        self.logger.info("Orion Phi-4 System stopped")
    
    async def _main_loop(self):
        """Main system loop"""
        iteration = 0
        
        while self.running:
            try:
                iteration += 1
                self.logger.info(f"\n{'='*80}")
                self.logger.info(f"Iteration {iteration}")
                self.logger.info(f"{'='*80}")
                
                # Get market data
                market_data = await self._get_market_data()
                
                # Run AI agent analysis
                agent_results = await self.ai_engine.analyze_market(market_data)
                
                # Orchestrate consensus
                consensus = await self.orchestrator.orchestrate(agent_results['agent_analyses'])
                
                # Run trading strategies
                strategy_results = await self._run_strategies(market_data)
                
                # Make trading decision
                await self._make_trading_decision(consensus, strategy_results, market_data)
                
                # Display status
                if iteration % 5 == 0:
                    await self._display_status()
                
                # Wait before next iteration
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def _get_market_data(self) -> dict:
        """Get current market data"""
        symbols = self.market_feed.get_symbols()
        
        # Get latest data for first symbol (can be extended to all symbols)
        symbol = symbols[0] if symbols else 'BTC/USDT'
        latest = await self.market_feed.get_latest(symbol)
        
        # Get historical data
        historical = await self.market_feed.get_historical(symbol, periods=100)
        
        market_data = {
            'symbol': symbol,
            'current_price': latest.close if latest else 50000,
            'prices': [d['close'] for d in historical],
            'volumes': [d['volume'] for d in historical],
            'latest': latest.to_dict() if latest else {}
        }
        
        return market_data
    
    async def _run_strategies(self, market_data: dict) -> dict:
        """Run all trading strategies"""
        strategy_results = {}
        
        for name, strategy in self.strategies.items():
            try:
                result = strategy.analyze(market_data)
                strategy_results[name] = result
                
                if result.get('success'):
                    self.logger.info(
                        f"Strategy {name}: {result['signal']} "
                        f"(confidence: {result.get('confidence', 0):.2%})"
                    )
            except Exception as e:
                self.logger.error(f"Error in strategy {name}: {e}")
                strategy_results[name] = {'success': False, 'error': str(e)}
        
        return strategy_results
    
    async def _make_trading_decision(
        self,
        consensus: dict,
        strategy_results: dict,
        market_data: dict
    ):
        """Make and execute trading decision"""
        
        # Get consensus signal
        signal = consensus.get('consensus', 'hold')
        confidence = consensus.get('confidence', 0.5)
        
        self.logger.info(f"\nConsensus: {signal.upper()} (confidence: {confidence:.2%})")
        
        # Only trade if confidence is high enough
        if confidence < 0.6:
            self.logger.info("Confidence too low, holding position")
            return
        
        # Check risk
        portfolio_state = self.portfolio.get_portfolio_state()
        
        # Simple trading logic
        symbol = market_data['symbol']
        current_price = market_data['current_price']
        
        if signal == 'buy':
            # Check if we have cash and no position
            if portfolio_state['cash'] > 0 and symbol not in [p['symbol'] for p in portfolio_state['positions']]:
                
                # Calculate position size
                position_size = portfolio_state['cash'] * 0.1 / current_price  # 10% of cash
                
                # Open position
                result = self.portfolio.open_position(
                    symbol=symbol,
                    side='long',
                    quantity=position_size,
                    price=current_price
                )
                
                if result['success']:
                    self.logger.info(f"✓ Opened BUY position: {position_size:.4f} {symbol} @ {current_price}")
                else:
                    self.logger.warning(f"✗ Failed to open position: {result.get('error')}")
        
        elif signal == 'sell':
            # Check if we have position to close
            position = self.portfolio.get_position(symbol)
            if position:
                result = self.portfolio.close_position(symbol, current_price)
                
                if result['success']:
                    pnl = result['pnl']
                    self.logger.info(f"✓ Closed position: {symbol} @ {current_price}, PnL: {pnl:+.2f}")
                else:
                    self.logger.warning(f"✗ Failed to close position: {result.get('error')}")
    
    async def _display_status(self):
        """Display system status"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("SYSTEM STATUS")
        self.logger.info("=" * 80)
        
        # Portfolio status
        portfolio_state = self.portfolio.get_portfolio_state()
        self.logger.info(f"Portfolio Value: ${portfolio_state['total_value']:,.2f}")
        self.logger.info(f"Cash: ${portfolio_state['cash']:,.2f}")
        self.logger.info(f"Positions: {portfolio_state['num_positions']}")
        self.logger.info(f"Total PnL: ${portfolio_state['total_pnl']:+,.2f} ({portfolio_state['return_pct']:+.2f}%)")
        self.logger.info(f"Drawdown: {portfolio_state['drawdown']:.2%}")
        
        # Agent status
        agent_status = self.ai_engine.get_system_status()
        self.logger.info(f"\nActive Agents: {len(agent_status['agents'])}")
        
        # Memory status
        memory_stats = self.memory_manager.get_stats()
        self.logger.info(f"Memory Items: {memory_stats['total_items']}")
        
        self.logger.info("=" * 80 + "\n")


async def main():
    """Main entry point"""
    system = None
    
    try:
        # Create and start system
        system = OrionPhi4System()
        await system.start()
        
    except KeyboardInterrupt:
        logger.info("\nKeyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    finally:
        if system:
            await system.stop()
    
    return 0


if __name__ == "__main__":
    # Run the system
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

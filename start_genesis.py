"""
Genesis Startup Script - Quick Start for Orion Phi-4
"""
import asyncio
import sys

from src.utils.logger import get_logger
from src.ai.multi_agent_system import OrionPhi4Engine

logger = get_logger(__name__)


async def genesis_initialization():
    """Genesis initialization sequence"""
    
    print("\n" + "=" * 80)
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                      ORION PHI-4 GENESIS SEQUENCE                             ║")
    print("║                   Multi-Agent AI Trading System v1.0                          ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print("=" * 80 + "\n")
    
    logger.info("Initiating Genesis Sequence...")
    
    # Step 1: Initialize AI Engine
    logger.info("[1/5] Initializing Orion Phi-4 AI Engine...")
    try:
        engine = OrionPhi4Engine()
        logger.info("✓ AI Engine initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize AI Engine: {e}")
        return False
    
    # Step 2: Start AI Agents
    logger.info("[2/5] Starting Multi-Agent System...")
    try:
        await engine.start()
        logger.info("✓ All agents started successfully")
    except Exception as e:
        logger.error(f"✗ Failed to start agents: {e}")
        return False
    
    # Step 3: Verify Agent Health
    logger.info("[3/5] Verifying agent health...")
    try:
        health = await engine.health_check()
        if health:
            logger.info("✓ All agents are healthy")
        else:
            logger.warning("⚠ Some agents may not be functioning optimally")
    except Exception as e:
        logger.error(f"✗ Health check failed: {e}")
        return False
    
    # Step 4: Test Agent Communication
    logger.info("[4/5] Testing agent communication...")
    try:
        test_data = {
            'prices': [100, 101, 102, 103, 102, 101, 100, 99, 98, 99, 100] * 10,
            'volumes': [1000, 1100, 1200, 1150, 1000, 950, 900, 850, 900, 950, 1000] * 10
        }
        
        result = await engine.analyze_market(test_data)
        
        if result.get('consensus_signal'):
            logger.info(f"✓ Agent communication successful")
            logger.info(f"  Consensus: {result['consensus_signal']}")
            logger.info(f"  Confidence: {result['average_confidence']:.2%}")
        else:
            logger.warning("⚠ Agent communication test returned unexpected results")
    except Exception as e:
        logger.error(f"✗ Agent communication test failed: {e}")
        return False
    
    # Step 5: Display System Status
    logger.info("[5/5] Retrieving system status...")
    try:
        status = engine.get_system_status()
        
        print("\n" + "=" * 80)
        print("SYSTEM STATUS")
        print("=" * 80)
        print(f"Status: {'ONLINE' if status['running'] else 'OFFLINE'}")
        print(f"Active Agents: {len(status['agents'])}")
        print("\nAgent Details:")
        
        for agent_id, agent_status in status['agents'].items():
            status_emoji = "✓" if agent_status['status'] == 'idle' else "⚠" if agent_status['status'] == 'processing' else "✗"
            print(f"  {status_emoji} {agent_id}: {agent_status['status']}")
        
        print("=" * 80 + "\n")
        
        logger.info("✓ System status retrieved")
    except Exception as e:
        logger.error(f"✗ Failed to retrieve system status: {e}")
        return False
    
    # Stop engine
    await engine.stop()
    
    print("\n" + "=" * 80)
    print("╔═══════════════════════════════════════════════════════════════════════════════╗")
    print("║                     GENESIS SEQUENCE COMPLETED                                ║")
    print("║                                                                               ║")
    print("║  The Orion Phi-4 system is ready for deployment.                             ║")
    print("║  Run 'python main.py' to start the full trading system.                      ║")
    print("╚═══════════════════════════════════════════════════════════════════════════════╝")
    print("=" * 80 + "\n")
    
    return True


async def quick_test():
    """Quick test of core functionality"""
    
    print("\n" + "=" * 80)
    print("QUICK FUNCTIONALITY TEST")
    print("=" * 80 + "\n")
    
    logger.info("Testing core imports...")
    
    try:
        # Test imports
        from src.ai.multi_agent_system import OrionPhi4Engine, AgentManager
        from src.ai.orchestrator import QuantumOrchestrator
        from src.ai.agents.quantum_agent import QuantumFinanceAgent
        from src.ai.agents.pattern_agent import PatternAnalyticsAgent
        from src.ai.agents.poker_agent import PokerLogicAgent
        from src.core.trading_engine import TradingEngine
        from src.core.memory_manager import MemoryManager
        from src.data.quantum_cache import QuantumCache
        from src.trading.strategies.quantum_mean_reversion import QuantumMeanReversionStrategy
        
        logger.info("✓ All imports successful")
        
        # Test basic functionality
        logger.info("Testing basic functionality...")
        
        engine = OrionPhi4Engine()
        logger.info("✓ Engine instantiation successful")
        
        await engine.start()
        logger.info("✓ Engine start successful")
        
        await engine.stop()
        logger.info("✓ Engine stop successful")
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS PASSED")
        print("=" * 80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        print("\n" + "=" * 80)
        print("✗ TESTS FAILED")
        print("=" * 80 + "\n")
        return False


def print_banner():
    """Print startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                               ║
    ║   ██████╗ ██████╗ ██╗ ██████╗ ███╗   ██╗    ██████╗ ██╗  ██╗██╗    ██╗  ██╗ ║
    ║  ██╔═══██╗██╔══██╗██║██╔═══██╗████╗  ██║    ██╔══██╗██║  ██║██║    ██║  ██║ ║
    ║  ██║   ██║██████╔╝██║██║   ██║██╔██╗ ██║    ██████╔╝███████║██║    ███████║ ║
    ║  ██║   ██║██╔══██╗██║██║   ██║██║╚██╗██║    ██╔═══╝ ██╔══██║██║    ╚════██║ ║
    ║  ╚██████╔╝██║  ██║██║╚██████╔╝██║ ╚████║    ██║     ██║  ██║██║         ██║ ║
    ║   ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚═╝     ╚═╝  ╚═╝╚═╝         ╚═╝ ║
    ║                                                                               ║
    ║                   Multi-Agent AI Trading System                               ║
    ║                          Genesis v1.0                                         ║
    ║                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def main():
    """Main entry point for genesis script"""
    
    print_banner()
    
    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Quick test mode
        success = await quick_test()
    else:
        # Full genesis sequence
        success = await genesis_initialization()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

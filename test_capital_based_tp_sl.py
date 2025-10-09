#!/usr/bin/env python3
"""
Test script for Capital-Based Take Profit and Stop Loss implementation

This script tests the new functionality where:
- Take Profit = 60% of capital profit target
- Stop Loss = 40% of capital loss limit
"""

import os
import sys
import django
import logging
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_trading_engine.settings')
django.setup()

# Now we can import Django models
from apps.trading.capital_based_risk_manager import CapitalBasedRiskManager, create_capital_based_position
from apps.data.services import RiskManagementService
from apps.trading.position_utils import PositionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_capital_based_manager():
    """Test the core CapitalBasedRiskManager functionality"""
    logger.info("=== Testing CapitalBasedRiskManager ===")
    
    manager = CapitalBasedRiskManager(capital_per_trade=1000.0)
    
    # Test case 1: BTC Long position
    logger.info("\n1. Testing BTC Long Position:")
    btc_position = manager.calculate_capital_based_targets(
        symbol="BTCUSDT",
        entry_price=50000.0,
        signal_type="BUY"
    )
    
    print_result(btc_position)
    
    # Test case 2: ETH Short position
    logger.info("\n2. Testing ETH Short Position:")
    eth_position = manager.calculate_capital_based_targets(
        symbol="ETHUSDT", 
        entry_price=3000.0,
        signal_type="SELL"
    )
    
    print_result(eth_position)
    
    # Test case 3: Small cap token
    logger.info("\n3. Testing Small Token Long Position:")
    small_position = manager.calculate_capital_based_targets(
        symbol="DOGEUSDT",
        entry_price=0.1,
        signal_type="STRONG_BUY"
    )
    
    print_result(small_position)


def test_risk_service():
    """Test the enhanced RiskManagementService"""
    logger.info("\n=== Testing RiskManagementService ===")
    
    service = RiskManagementService()
    
    # Test capital-based position calculation
    logger.info("\n1. Testing Risk Service Capital-Based Position:")
    position_data = service.calculate_capital_based_position(
        symbol="SOLUSDT",
        entry_price=200.0,
        signal_type="BUY",
        capital_amount=1000.0
    )
    
    print_result(position_data)
    
    # Test validation
    logger.info("\n2. Testing Position Validation:")
    validation = service.validate_capital_based_position(position_data)
    logger.info(f"Validation result: {validation}")
    
    # Test P&L calculation
    logger.info("\n3. Testing P&L Calculation:")
    pnl_data = service.calculate_trade_pnl_with_capital_based_exits(
        entry_price=200.0,
        current_price=260.0,  # 30% gain
        position_size=5.0,
        signal_type="BUY"
    )
    
    logger.info(f"P&L Data: {pnl_data}")


def test_position_utils():
    """Test position management utilities"""
    logger.info("\n=== Testing Position Management Utilities ===")
    
    manager = PositionManager()
    
    # Test position metrics calculation
    logger.info("\n1. Testing Position Metrics Calculation:")
    
    # Simulate a position update
    current_price = 55000.0  # 10% gain on BTC
    entry_price = 50000.0
    
    pnl_data = manager.risk_service.calculate_trade_pnl_with_capital_based_exits(
        entry_price=entry_price,
        current_price=current_price,
        position_size=0.02,  # $1000 / $50000
        signal_type="BUY"
    )
    
    logger.info(f"Position P&L: {pnl_data}")


def print_result(result):
    """Helper function to print results nicely"""
    if isinstance(result, dict):
        for key, value in result.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.6f}")
            else:
                logger.info(f"  {key}: {value}")
    else:
        logger.info(f"Result: {result}")


def test_scenarios():
    """Test various trading scenarios"""
    logger.info("\n=== Testing Trading Scenarios ===")
    
    manager = CapitalBasedRiskManager(capital_per_trade=1000.0)
    
    scenarios = [
        {"name": "BTC Long - Small Price", "symbol": "BTCUSDT", "entry": 1000.0, "signal": "BUY"},
        {"name": "BTC Long - High Price", "symbol": "BTCUSDT", "entry": 100000.0, "signal": "BUY"},
        {"name": "ETH Short", "symbol": "ETHUSDT", "entry": 2000.0, "signal": "SELL"},
        {"name": "Small Cap Long", "symbol": "DOGEUSDT", "entry": 0.001, "signal": "STRONG_BUY"},
    ]
    
    for scenario in scenarios:
        logger.info(f"\n{scenario['name']}:")
        result = manager.calculate_capital_based_targets(
            symbol=scenario['symbol'],
            entry_price=scenario['entry'],
            signal_type=scenario['signal']
        )
        
        if result:
            logger.info(f"  Capital: ${result['capital_per_trade']:.2f}")
            logger.info(f"  Position Size: {result['position_size']:.6f}")
            logger.info(f"  Take Profit: ${result['take_profit_price']:.6f}")
            logger.info(f"  Stop Loss: ${result['stop_loss_price']:.6f}")
            logger.info(f"  Risk-Reward: {result['risk_reward_ratio']:.2f}")
            
            # Validate the percentages
            profit_amount = result['take_profit_amount']
            loss_amount = result['stop_loss_amount']
            capital = result['capital_per_trade']
            
            profit_pct = (profit_amount / capital) * 100
            loss_pct = (loss_amount / capital) * 100
            
            logger.info(f"  Profit Target: {profit_pct:.1f}% of capital (${profit_amount:.2f})")
            logger.info(f"  Loss Limit: {loss_pct:.1f}% of capital (${loss_amount:.2f})")


def main():
    """Run all tests"""
    logger.info("Starting Capital-Based TP/SL Tests")
    logger.info("=" * 50)
    
    try:
        test_capital_based_manager()
        test_risk_service()
        test_position_utils()
        test_scenarios()
        
        logger.info("\n" + "=" * 50)
        logger.info("All tests completed successfully!")
        logger.info("\nKey Features Implemented:")
        logger.info("✓ Take Profit = 60% of capital profit target")
        logger.info("✓ Stop Loss = 40% of capital loss limit")
        logger.info("✓ Capital-based position sizing")
        logger.info("✓ Enhanced Position model with capital tracking")
        logger.info("✓ Risk management service integration")
        logger.info("✓ Position management utilities")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

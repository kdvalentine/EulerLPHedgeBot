#!/usr/bin/env python3
"""
Final system check - verifies all components are operational.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

load_dotenv()


async def check_system():
    """Run comprehensive system check."""
    print("=" * 60)
    print("NoetherBot System Check")
    print("=" * 60)
    
    results = {}
    
    # 1. Check environment
    print("\n📋 Environment Variables:")
    env_vars = [
        "RPC_URL",
        "EULERSWAP_POOL", 
        "BINANCE_API_KEY",
        "BINANCE_API_SECRET"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if "SECRET" in var or "KEY" in var:
                display = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
            else:
                display = value[:50] + "..." if len(value) > 50 else value
            print(f"  ✅ {var}: {display}")
            results[var] = True
        else:
            print(f"  ❌ {var}: Not set")
            results[var] = False
    
    # 2. Check imports
    print("\n📦 Module Imports:")
    modules = [
        ("Web3", "web3"),
        ("CCXT", "ccxt"),
        ("SQLAlchemy", "sqlalchemy"),
        ("Textual", "textual"),
        ("Rich", "rich"),
    ]
    
    for name, module in modules:
        try:
            __import__(module)
            print(f"  ✅ {name}")
            results[f"module_{module}"] = True
        except ImportError:
            print(f"  ❌ {name} - Run: pip install {module}")
            results[f"module_{module}"] = False
    
    # 3. Check RPC connection
    print("\n🌐 Ethereum RPC:")
    try:
        from web3 import Web3
        rpc_url = os.getenv("RPC_URL")
        if rpc_url:
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if w3.is_connected():
                block = w3.eth.block_number
                print(f"  ✅ Connected (Block: {block:,})")
                results["rpc"] = True
            else:
                print(f"  ❌ Cannot connect to RPC")
                results["rpc"] = False
        else:
            print(f"  ❌ RPC_URL not set")
            results["rpc"] = False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results["rpc"] = False
    
    # 4. Check Binance
    print("\n💱 Binance API:")
    try:
        import ccxt.async_support as ccxt
        
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")
        
        if api_key and api_secret:
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            })
            
            await exchange.load_markets()
            balance = await exchange.fetch_balance()
            print(f"  ✅ Connected (Futures enabled)")
            results["binance"] = True
            await exchange.close()
        else:
            print(f"  ❌ API keys not set")
            results["binance"] = False
            
    except Exception as e:
        if "-2015" in str(e):
            print(f"  ⚠️  API keys valid but need futures permissions")
        else:
            print(f"  ❌ Error: {str(e)[:50]}")
        results["binance"] = False
    
    # 5. Check database
    print("\n💾 Database:")
    try:
        from database_manager import DatabaseManager
        db = DatabaseManager("sqlite:///noether_bot.db")
        print(f"  ✅ SQLite initialized")
        results["database"] = True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results["database"] = False
    
    # 6. Check pool
    print("\n🏊 EulerSwap Pool:")
    pool_address = os.getenv("EULERSWAP_POOL", "").lower()
    correct_pool = "0x55dcf9455eee8fd3f5eed17606291272cde428a8".lower()
    
    if pool_address == correct_pool:
        print(f"  ✅ Correct pool configured")
        results["pool"] = True
    else:
        print(f"  ❌ Pool address mismatch")
        results["pool"] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal Checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("\n✅ ALL SYSTEMS OPERATIONAL!")
        print("\nYou can now run:")
        print("  python main.py              # Start the bot")
        print("  python scripts/monitor_mainnet.py  # Monitor only")
    else:
        print("\n⚠️  Some components need attention")
        print("\nFailed checks:")
        for key, value in results.items():
            if not value:
                print(f"  - {key}")
    
    return passed == total


if __name__ == "__main__":
    print("\nNoetherBot Final System Check")
    print("Verifying all components...\n")
    
    result = asyncio.run(check_system())
    sys.exit(0 if result else 1)
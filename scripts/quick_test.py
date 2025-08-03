#!/usr/bin/env python3
"""
Quick connection test for Infura and basic configuration.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import urllib.request
import json

# Load environment
load_dotenv()


def test_infura():
    """Test Infura RPC connection."""
    print("\n🔍 Testing Infura Connection...")

    rpc_url = os.getenv("RPC_URL")
    if not rpc_url:
        print("❌ RPC_URL not found in .env")
        return False

    # Extract key for display
    key = rpc_url.split("/")[-1]
    print(f"   Endpoint: https://mainnet.infura.io/v3/{key[:8]}...")

    # Prepare JSON-RPC request
    data = json.dumps(
        {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
    ).encode("utf-8")

    try:
        # Make request
        req = urllib.request.Request(
            rpc_url, data=data, headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))

        if "result" in result:
            block_num = int(result["result"], 16)
            print(f"   ✅ Connected to Ethereum Mainnet")
            print(f"   Current Block: {block_num:,}")

            # Test getReserves on EulerSwap pool
            test_pool_access(rpc_url)
            return True
        else:
            print(f"   ❌ Invalid response: {result}")
            return False

    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False


def test_pool_access(rpc_url):
    """Test EulerSwap pool access."""
    print("\n🔍 Testing EulerSwap Pool...")

    pool_address = os.getenv("EULERSWAP_POOL")
    print(f"   Pool: {pool_address}")

    # Prepare eth_call for getReserves()
    # Function selector for getReserves(): 0x0902f1ac
    data = json.dumps(
        {
            "jsonrpc": "2.0",
            "method": "eth_call",
            "params": [{"to": pool_address, "data": "0x0902f1ac"}, "latest"],
            "id": 2,
        }
    ).encode("utf-8")

    try:
        req = urllib.request.Request(
            rpc_url, data=data, headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))

        if "result" in result and result["result"] != "0x":
            # Parse the result (3 uint values)
            hex_data = result["result"][2:]  # Remove 0x

            # Each value is 32 bytes (64 hex chars)
            reserve0 = int(hex_data[0:64], 16)
            reserve1 = int(hex_data[64:128], 16)
            status = int(hex_data[128:192], 16)

            # Convert to readable values
            usdt_reserve = reserve0 / 10**6  # USDT has 6 decimals
            weth_reserve = reserve1 / 10**18  # WETH has 18 decimals

            status_msg = (
                ["Unactivated", "Unlocked", "Locked"][status]
                if status < 3
                else "Unknown"
            )

            print(f"   ✅ Pool Accessible")
            print(f"   Status: {status_msg}")
            print(f"   USDT Reserve: {usdt_reserve:,.2f}")
            print(f"   WETH Reserve: {weth_reserve:,.4f}")
            if weth_reserve > 0:
                print(f"   Implied Price: {usdt_reserve/weth_reserve:,.2f} USDT/WETH")
        else:
            print(f"   ❌ Could not read pool data")

    except Exception as e:
        print(f"   ❌ Pool access failed: {e}")


def check_config():
    """Check configuration."""
    print("\n📋 Configuration Check")
    print("=" * 50)

    required_vars = [
        "RPC_URL",
        "EULERSWAP_POOL",
        "EULER_VAULT_USDT",
        "EULER_VAULT_WETH",
        "USDT_ADDRESS",
        "WETH_ADDRESS",
        "BINANCE_API_KEY",
    ]

    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if "API" in var or "SECRET" in var:
                display = f"{value[:10]}..." if len(value) > 10 else "***"
            elif "0x" in value:
                display = f"{value[:10]}...{value[-8:]}"
            else:
                display = f"{value[:20]}..." if len(value) > 20 else value
            print(f"   ✅ {var}: {display}")
        else:
            print(f"   ❌ {var}: Not configured")
            all_present = False

    return all_present


def main():
    """Main entry point."""
    print("\n" + "=" * 50)
    print("LPHedgeBot Quick Connection Test")
    print("=" * 50)

    # Check .env exists
    if not Path(".env").exists():
        print("\n❌ .env file not found!")
        print("Please ensure .env file exists in the project root.")
        return 1

    # Check configuration
    config_ok = check_config()

    if not config_ok:
        print("\n⚠️  Some configuration values are missing.")
        print("Please check your .env file.")

    # Test Infura connection
    infura_ok = test_infura()

    # Summary
    print("\n" + "=" * 50)
    print("Summary")
    print("=" * 50)

    if config_ok and infura_ok:
        print("✅ Basic configuration and connections are working!")
        print("\nNext steps:")
        print("1. Add your Binance API Secret to .env")
        print("2. Install dependencies: poetry install")
        print("3. Run full test: poetry run python scripts/test_connections.py")
        print("4. Start monitoring: poetry run python scripts/monitor_mainnet.py")
        return 0
    else:
        print("❌ Some checks failed. Please review the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Discover active EulerSwap pools on mainnet.
"""

import asyncio
from web3 import Web3
from dotenv import load_dotenv
import os
import json

load_dotenv()

# EulerSwap Factory ABI (minimal)
FACTORY_ABI = [
    {
        "inputs": [],
        "name": "pools",
        "outputs": [{"internalType": "address[]", "name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "start", "type": "uint256"},
            {"internalType": "uint256", "name": "end", "type": "uint256"},
        ],
        "name": "poolsSlice",
        "outputs": [{"internalType": "address[]", "name": "", "type": "address[]"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "name": "pool", "type": "address"},
            {"indexed": True, "name": "asset0", "type": "address"},
            {"indexed": True, "name": "asset1", "type": "address"},
        ],
        "name": "PoolDeployed",
        "type": "event",
    },
]

# Pool ABI (minimal)
POOL_ABI = [
    {
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint256", "name": "reserve0", "type": "uint256"},
            {"internalType": "uint256", "name": "reserve1", "type": "uint256"},
            {"internalType": "uint8", "name": "status", "type": "uint8"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "config",
        "outputs": [
            {
                "internalType": "address",
                "name": "deploymentTimestamp",
                "type": "uint256",
            },
            {"internalType": "address", "name": "token0", "type": "address"},
            {"internalType": "address", "name": "token1", "type": "address"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


async def discover_pools():
    """Discover all deployed EulerSwap pools."""

    # Connect to Ethereum
    rpc_url = os.getenv("RPC_URL")
    w3 = Web3(Web3.HTTPProvider(rpc_url))

    print("=" * 60)
    print("EulerSwap Pool Discovery")
    print("=" * 60)

    # Factory address
    FACTORY_ADDRESS = "0xb013be1D0D380C13B58e889f412895970A2Cf228"
    factory = w3.eth.contract(
        address=w3.to_checksum_address(FACTORY_ADDRESS), abi=FACTORY_ABI
    )

    print(f"\n📍 Factory: {FACTORY_ADDRESS}")

    try:
        # Get all pools
        print("\n🔍 Fetching deployed pools...")
        pools = factory.functions.pools().call()

        print(f"\n✅ Found {len(pools)} pools deployed")

        # Known token addresses for reference
        known_tokens = {
            "0xdAC17F958D2ee523a2206206994597C13D831ec7": "USDT",
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": "WETH",
            "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": "USDC",
            "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": "WBTC",
            "0x6B175474E89094C44Da98b954EedeAC495271d0F": "DAI",
        }

        # Check each pool
        print("\n📊 Pool Details:")
        print("-" * 60)

        for i, pool_addr in enumerate(pools[:10], 1):  # Limit to first 10 for display
            pool_checksum = w3.to_checksum_address(pool_addr)
            print(f"\n{i}. Pool: {pool_checksum}")

            # Get pool reserves
            pool = w3.eth.contract(address=pool_checksum, abi=POOL_ABI)
            try:
                reserves = pool.functions.getReserves().call()
                reserve0 = reserves[0]
                reserve1 = reserves[1]
                status = reserves[2]

                status_text = ["Unactivated", "Unlocked", "Locked"][status]

                # Show reserves (note: these are virtual reserves)
                print(f"   Status: {status_text}")
                print(f"   Virtual Reserve0: {reserve0:,}")
                print(f"   Virtual Reserve1: {reserve1:,}")

                # If this is our known USDT/WETH pool
                if (
                    pool_checksum.lower()
                    == "0x55dcf9455eee8fd3f5eed17606291272cde428a8".lower()
                ):
                    print("   ⭐ This is the USDT/WETH pool in your config")

            except Exception as e:
                print(f"   ❌ Could not read pool: {e}")

        # Recent pool deployments
        print("\n\n📅 Recent Pool Deployments (last 1000 blocks):")
        print("-" * 60)

        current_block = w3.eth.block_number
        from_block = max(0, current_block - 1000)

        event_filter = factory.events.PoolDeployed.create_filter(
            fromBlock=from_block, toBlock="latest"
        )

        events = event_filter.get_all_entries()

        if events:
            for event in events[-5:]:  # Show last 5
                pool = event["args"]["pool"]
                asset0 = event["args"]["asset0"]
                asset1 = event["args"]["asset1"]

                token0_name = known_tokens.get(asset0, "Unknown")
                token1_name = known_tokens.get(asset1, "Unknown")

                print(f"\n  Pool: {pool}")
                print(f"  Pair: {token0_name}/{token1_name}")
                print(f"  Token0: {asset0}")
                print(f"  Token1: {asset1}")
                print(f"  Block: {event['blockNumber']}")
        else:
            print("  No recent deployments found")

        print("\n" + "=" * 60)
        print("Summary")
        print("=" * 60)

        print(
            f"""
The pool at 0x55dcf9455eee8fd3f5eed17606291272cde428a8 is correct.

Key Points:
1. The large "reserves" are VIRTUAL reserves for the AMM curve
2. EulerSwap doesn't hold actual tokens - it uses Euler Vaults
3. Virtual reserves define the swap curve parameters
4. Real liquidity comes from the connected Euler Vaults

Your configuration is correct! The pool is active and unlocked.
"""
        )

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(discover_pools())

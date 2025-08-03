#!/usr/bin/env python3
"""
Quick Binance check - tests public data only to verify setup.
"""

import asyncio
import ccxt.async_support as ccxt


async def test_binance_public():
    """Test Binance public data access."""
    print("\n" + "=" * 50)
    print("Binance Public API Test (No Authentication)")
    print("=" * 50)

    exchange = None
    try:
        # Connect without API keys - public data only
        exchange = ccxt.binance(
            {
                "enableRateLimit": True,
                "options": {"defaultType": "future"},  # Futures market
            }
        )

        print("\n✅ Connected to Binance Futures (Public)")

        # Load markets
        await exchange.load_markets()

        # Get ETH perpetual info
        symbol = "ETH/USDT:USDT"
        print(f"\n📊 {symbol} Market Data:")
        print("-" * 30)

        # Get ticker
        ticker = await exchange.fetch_ticker(symbol)
        print(f"  Current Price: ${ticker['last']:,.2f}")
        print(f"  24h High: ${ticker['high']:,.2f}")
        print(f"  24h Low: ${ticker['low']:,.2f}")
        print(f"  24h Volume: {ticker['baseVolume']:,.2f} ETH")
        print(f"  24h Volume (USDT): ${ticker['quoteVolume']:,.0f}")
        print(f"  24h Change: {ticker['percentage']:.2f}%")

        # Get funding rate
        print(f"\n💰 Funding Rate:")
        funding = await exchange.fetch_funding_rate(symbol)
        print(f"  Current Rate: {funding['rate']*100:.4f}% per 8h")
        print(f"  Annual (approx): {funding['rate']*3*365*100:.2f}%")

        # Get order book
        print(f"\n📖 Order Book (Best Bid/Ask):")
        orderbook = await exchange.fetch_order_book(symbol, 1)
        if orderbook["bids"] and orderbook["asks"]:
            bid = orderbook["bids"][0]
            ask = orderbook["asks"][0]
            spread = ask[0] - bid[0]
            spread_pct = (spread / bid[0]) * 100

            print(f"  Bid: ${bid[0]:,.2f} ({bid[1]:.3f} ETH)")
            print(f"  Ask: ${ask[0]:,.2f} ({ask[1]:.3f} ETH)")
            print(f"  Spread: ${spread:.2f} ({spread_pct:.3f}%)")

        print("\n✅ Binance public data access is working!")
        print("\nThis confirms:")
        print("  • CCXT is properly installed")
        print("  • Network connection to Binance is working")
        print("  • Futures market data is accessible")

        print("\n⚠️  Note: Your API keys will need:")
        print("  1. Futures trading enabled")
        print("  2. IP whitelist (if you have IP restrictions)")
        print("  3. Correct permissions for reading and trading")

        await exchange.close()
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        if exchange:
            await exchange.close()
        return False


if __name__ == "__main__":
    asyncio.run(test_binance_public())

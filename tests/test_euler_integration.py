"""Tests for EulerSwap protocol integration."""

import pytest
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, MagicMock
from web3 import Web3

from euler_swap import EulerPoolManager, PoolParams
from swap_monitor import SwapMonitor


@pytest.mark.asyncio
async def test_euler_pool_manager_fetch_params():
    """Test fetching pool parameters from EulerSwap contract."""
    # Mock Web3 and contract
    mock_w3 = Mock(spec=Web3)
    mock_contract = MagicMock()

    # Mock getParams response (matching IEulerSwap.Params struct)
    mock_params = (
        "0xVault0Address",  # vault0
        "0xVault1Address",  # vault1
        "0xEulerAccount",  # eulerAccount
        10000000,  # equilibriumReserve0 (uint112)
        5000000000000000000,  # equilibriumReserve1 (uint112, 5 ETH)
        2000000000000000000000,  # priceX
        1000000000000000000000,  # priceY
        500000000000000000,  # concentrationX (0.5)
        500000000000000000,  # concentrationY (0.5)
        3000000000000000,  # fee (0.003 = 0.3%)
        100000000000000,  # protocolFee (0.0001 = 0.01%)
        "0xProtocolFeeRecipient",  # protocolFeeRecipient
    )

    # Mock getAssets response
    mock_assets = ("0xUSDTAddress", "0xWETHAddress")

    mock_contract.functions.getParams.return_value.call = AsyncMock(
        return_value=mock_params
    )
    mock_contract.functions.getAssets.return_value.call = AsyncMock(
        return_value=mock_assets
    )

    # Create pool manager
    manager = EulerPoolManager(mock_w3, "0xPoolAddress", mock_contract)

    # Fetch parameters
    params = await manager.fetch_pool_params()

    # Verify parameters
    assert params.vault0 == "0xVault0Address"
    assert params.vault1 == "0xVault1Address"
    assert params.euler_account == "0xEulerAccount"
    assert params.equilibrium_reserve0 == Decimal("10000000")
    assert params.equilibrium_reserve1 == Decimal("5000000000000000000")
    assert params.fee == Decimal("0.003")  # 0.3%
    assert params.protocol_fee == Decimal("0.0001")  # 0.01%
    assert params.token0_address == "0xUSDTAddress"
    assert params.token1_address == "0xWETHAddress"

    # Check equilibrium price calculation
    equilibrium_price = params.equilibrium_price
    assert equilibrium_price == Decimal("2")  # priceX/priceY = 2000/1000 = 2


@pytest.mark.asyncio
async def test_swap_monitor_handles_status():
    """Test that swap monitor properly handles EulerSwap status values."""
    # Mock dependencies
    mock_exchange = AsyncMock()
    mock_exchange.get_current_perpetual_position = AsyncMock(
        return_value={"size": Decimal("0"), "side": None}
    )

    mock_w3 = MagicMock()
    mock_w3.eth = AsyncMock()
    mock_w3.eth.block_number = 18000000
    mock_w3.to_checksum_address = Mock(side_effect=lambda x: x)

    # Create mock contract
    mock_contract = MagicMock()

    # Test different status values
    test_cases = [
        (1000000, 500000000000000000, 0),  # Unactivated pool
        (1000000, 500000000000000000, 1),  # Unlocked (normal)
        (1000000, 500000000000000000, 2),  # Locked (reentrancy)
    ]

    for reserve0, reserve1, status in test_cases:
        mock_contract.functions.getReserves.return_value.call = AsyncMock(
            return_value=(reserve0, reserve1, status)
        )

        # Create monitor with mocked Web3
        monitor = SwapMonitor(
            rpc_url="http://localhost:8545",
            pool_address="0xPoolAddress",
            abi_path="abi/eulerswap_pool.json",
            exchange=mock_exchange,
            symbol_perpetual="ETH/USDT:USDT",
        )
        monitor.w3 = mock_w3
        monitor.contract = mock_contract

        # Fetch reserves
        r0, r1, pool_status = await monitor.fetch_reserves()

        # Verify correct handling
        assert pool_status == status
        assert r0 == Decimal(reserve0) / Decimal(10**6)  # USDT with 6 decimals
        assert r1 == Decimal(reserve1) / Decimal(10**18)  # WETH with 18 decimals

        # Verify snapshot creation still works
        snapshot = await monitor.fetch_snapshot()
        assert snapshot is not None
        assert snapshot.reserve_token0 == r0
        assert snapshot.reserve_token1 == r1


@pytest.mark.asyncio
async def test_pool_manager_quote_calculation():
    """Test quote calculation through EulerSwap contract."""
    mock_w3 = Mock(spec=Web3)
    mock_contract = MagicMock()

    # Setup pool parameters
    mock_contract.functions.getParams.return_value.call = AsyncMock(
        return_value=(
            "0xVault0",
            "0xVault1",
            "0xEulerAccount",
            10000000000,
            5000000000000000000,  # reserves
            2000000000000000000000,
            1000000000000000000000,  # prices
            500000000000000000,
            500000000000000000,  # concentrations
            3000000000000000,
            100000000000000,
            "0xFeeRecipient",
        )
    )
    mock_contract.functions.getAssets.return_value.call = AsyncMock(
        return_value=("0xUSDT", "0xWETH")
    )

    # Mock computeQuote response (0.49 WETH for 1000 USDT input)
    mock_contract.functions.computeQuote.return_value.call = AsyncMock(
        return_value=490000000000000000  # 0.49 WETH in wei
    )

    manager = EulerPoolManager(mock_w3, "0xPoolAddress", mock_contract)
    await manager.fetch_pool_params()

    # Get quote for swapping 1000 USDT to WETH
    quote = await manager.get_quote(
        amount_in=Decimal("1000"),
        token_in_is_token0=True,  # USDT is token0
        exact_in=True,
    )

    # Verify quote
    assert quote == Decimal("0.49")  # Should get 0.49 WETH for 1000 USDT

    # Verify computeQuote was called with correct parameters
    mock_contract.functions.computeQuote.assert_called_with(
        "0xUSDT",  # tokenIn
        "0xWETH",  # tokenOut
        1000000000,  # amount scaled to 6 decimals for USDT
        True,  # exactIn
    )


@pytest.mark.asyncio
async def test_pool_manager_swap_limits():
    """Test fetching swap limits from EulerSwap."""
    mock_w3 = Mock(spec=Web3)
    mock_contract = MagicMock()

    # Setup basic pool data
    mock_contract.functions.getAssets.return_value.call = AsyncMock(
        return_value=("0xUSDT", "0xWETH")
    )
    mock_contract.functions.getParams.return_value.call = AsyncMock(
        return_value=(
            "0xVault0",
            "0xVault1",
            "0xEulerAccount",
            10000000000,
            5000000000000000000,
            2000000000000000000000,
            1000000000000000000000,
            0,
            0,  # No concentration
            3000000000000000,
            0,
            "0xFeeRecipient",
        )
    )

    # Mock getLimits response (max 5000 USDT in, max 2.4 WETH out)
    mock_contract.functions.getLimits.return_value.call = AsyncMock(
        return_value=(5000000000, 2400000000000000000)  # Scaled values
    )

    manager = EulerPoolManager(mock_w3, "0xPoolAddress", mock_contract)
    await manager.fetch_pool_params()

    # Get swap limits for USDT -> WETH
    limit_in, limit_out = await manager.get_swap_limits(token_in_is_token0=True)

    # Verify limits
    assert limit_in == Decimal("5000")  # 5000 USDT max input
    assert limit_out == Decimal("2.4")  # 2.4 WETH max output

    # Verify getLimits was called correctly
    mock_contract.functions.getLimits.assert_called_with("0xUSDT", "0xWETH")


@pytest.mark.asyncio
async def test_desynchronization_detection():
    """Test detection of reserve desynchronization."""
    mock_w3 = Mock(spec=Web3)
    mock_contract = MagicMock()

    # Setup pool with equilibrium at 10000 USDT, 5 WETH
    mock_contract.functions.getParams.return_value.call = AsyncMock(
        return_value=(
            "0xVault0",
            "0xVault1",
            "0xEulerAccount",
            10000000000,
            5000000000000000000,  # 10000 USDT, 5 WETH equilibrium
            2000000000000000000000,
            1000000000000000000000,
            0,
            0,
            0,
            0,
            "0xFeeRecipient",
        )
    )
    mock_contract.functions.getAssets.return_value.call = AsyncMock(
        return_value=("0xUSDT", "0xWETH")
    )

    manager = EulerPoolManager(mock_w3, "0xPoolAddress", mock_contract)
    await manager.fetch_pool_params()

    # Test synchronized reserves (close to equilibrium)
    is_desynced = manager.is_reserve_desynchronized(
        (Decimal("10200000000"), Decimal("4900000000000000000")),  # 2% deviation
        threshold_percent=Decimal("5"),
    )
    assert not is_desynced

    # Test desynchronized reserves (far from equilibrium)
    is_desynced = manager.is_reserve_desynchronized(
        (
            Decimal("11000000000"),
            Decimal("4000000000000000000"),
        ),  # 10% and 20% deviation
        threshold_percent=Decimal("5"),
    )
    assert is_desynced


def test_pool_params_calculations():
    """Test PoolParams calculations and properties."""
    params = PoolParams(
        vault0="0xVault0",
        vault1="0xVault1",
        euler_account="0xEulerAccount",
        equilibrium_reserve0=Decimal("10000"),
        equilibrium_reserve1=Decimal("5"),
        price_x=Decimal("2000"),
        price_y=Decimal("1000"),
        concentration_x=Decimal("0.8"),
        concentration_y=Decimal("0.8"),
        fee=Decimal("0.003"),
        protocol_fee=Decimal("0.0001"),
        protocol_fee_recipient="0xFeeRecipient",
        token0_address="0xUSDT",
        token1_address="0xWETH",
        token0_decimals=6,
        token1_decimals=18,
    )

    # Test equilibrium price calculation
    assert params.equilibrium_price == Decimal("2")  # 2000/1000 = 2

    # Test concentration check
    assert params.is_concentrated is True

    # Test max swap sizes
    assert params.max_swap_size_token0 == Decimal("10000")
    assert params.max_swap_size_token1 == Decimal("5")

    # Test dictionary conversion
    params_dict = params.to_dict()
    assert params_dict["equilibrium_price"] == "2"
    assert params_dict["is_concentrated"] is True
    assert params_dict["token0_decimals"] == 6
    assert params_dict["token1_decimals"] == 18

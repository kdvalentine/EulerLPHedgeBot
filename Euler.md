# Search_the_documentation

## https://docs.euler.finance/search

Skip to main content
# Search the documentation


---

## https://docs.euler.finance/brandAssets

Skip to main content
See the brand gudelines here: https://euler.finance/brand


---

## https://docs.euler.finance/category/guides

Skip to main content
## 📄️ How to vote
## 📄️ How to make a proposal


---

## https://docs.euler.finance/concepts/accounts

Skip to main content
Although each wallet address on Euler is only allowed at most one outstanding liability at any given time, the EVC provides each wallet address with 256 _virtual_ account addresses. These addresses allow users to better manage risk by establishing multiple risk-isolated positions in a gas-efficient manner across segregated accounts.
Note that in the absence of accounts users would be forced to construct multiple positions across different wallet addresses, adding significant friction to their ability to trade. They would need to hold ETH to pay for gas in each address, carry out approvals on each address, and login to the user interface using each address separately.
warning
Account addresses are internal to the EVC and compatible vaults, and care should be taken to ensure that these addresses are not used by other contracts. For example, never transfer your regular ERC20 tokens to an account address other than your wallet address.


---

## https://docs.euler.finance/concepts/clusters

Skip to main content
On this page
The credit vault is the building block of modular money markets on Euler. The EVK allows vault deployers to flexibly configure the behavior of individual vaults and also control vault-to-vault collateral relationships in a granular manner. Thanks to these affordances, EVK-built vault clusters can not only replicate popular money market setups such as Aave (monolithic lending) and Morpho (isolated lending) but also extend and improve them beyond their individual deficiencies.
A major consideration when designing an onchain money market is placing it on the axis between capital efficiency (monolithic) and risk isolation (isolated). While both have their merits, lending protocols are often specialized and limited to one part of the spectrum. By contrast, Euler vault clusters can be be configured in any manner because collateral relationships are pairwise by default. In addition, settings that are often market-wide elsewhere, are configurable per vault on Euler.
## Dampening Monolith Risks​
Monolithic money markets are popular because they allow users to be very capital-efficient. However this comes with a _big caveat_ : it turns up the risk of a systemic market-wide wipeout. To give one example, if an attacker maliciously inflates the price of an asset they become eligible to borrow all other assets, hurting all participants as a result.
Monolithic lending protocols often implement various mitigations to their inherent systemic risks such as collateral isolation mode, supply and borrow caps, high-correlation borrowing modes and others. Ultimately they remain beholden to the inflexibility of the monolith, and are often forced to manage risks by modularizing aspects of the protocol. By contrast, money markets built with the Euler Vault Kit are highly modular by design. This allows a monolith-like lending market to be built with a toolkit of precise risk management functions that let governors manage market conditions effectively.
  * Dampening Monolith Risks




---

## https://docs.euler.finance/concepts/evc

Skip to main content
On this page
The Ethereum Vault Connector (EVC) is an open-source interoperability layer that connects credit vaults together to enable their use as collateral for one another. The EVC allows users to efficiently batch and execute multiple operations in one transaction.
## Additional Features of the EVC​
The EVC's authentication layer offers a number of account management features. The most notable are virtual isolated accounts and _operators_ , which allow delegation of account management to specialized smart contracts. The EVC allocates 256 virtual accounts to every user, letting them conveniently build multiple borrowing positions within a single wallet. Combined with the ability to batch multiple operations in one transaction, the EVC allows users to efficiently build sophisticated positions in a few clicks.
  * Additional Features of the EVC




---

## https://docs.euler.finance/concepts/interest-rates

Skip to main content
Users who borrow from vaults pay interest on their outstanding debts. This interest is then directed to lenders in the vault for their liquidity provision service. By default 10% of accrued borrowing interest is withheld as a fee, which is then split halfway between the vault governor and Euler DAO.
The borrowing rate of a vault is determined by its _interest rate model (IRM)_. These are mathematical functions that take the utilization rate (the proportion of assets that are borrowed) and return the borrowing interest rate at the moment. A common model is the Linear Kink IRM which increases the rate gradually until a target utilization rate (e.g. 80%) is exceeded, after which the rate rises sharply to encourage de-risking behaviors.
The IRM lives as a separate contract outside of the vault. This makes IRM contracts reusable since they are stateless mathematical functions. The vault governor can install a new IRM at any point in time while the EVK has safeguards in place to disable broken IRMs without excessively damaging users.


---

## https://docs.euler.finance/concepts/liquidations

Skip to main content
On this page
Euler has a robust liquidation mechanism to maintain the solvency of vaults and protect the deposits of lenders. Liquidation on Euler occurs when the account’s risk-adjusted collateral value drops to or below its debt level, prompting automated bots to handle the liquidation process. The liquidation mechanics are designed to be efficient and fair: liquidators receive discounted collateral from the borrower’s vault, incentivizing them to cover the borrower’s debt. Discounts scale based on how much the account is under-collateralized, creating incentives only when liquidation is financially viable. This system maintains protocol stability without unduly penalizing borrowers or offering excessive rewards to liquidators.
## Parameters​
Each vault has a maximum liquidation discount parameter which vault creators can set to attract liquidators without excessive impact on borrowers. This setting helps prevent harmful liquidation spirals, unlike systems that offer steep discounts at the onset.
An optional, but recommended, cool-off period can be used to prevent immediate liquidations after the user creates their borrow position. This period creates a short buffer to reduce the risk of certain attack types and stabilize vaults, especially when using pull-based oracles. It ensures that liquidations only happen when needed, rather than due to momentary price shifts or market manipulation.
By default, vaults have bad debt socialization enabled to handle remaining bad debt if the liquidated account's collateral does not fully cover its obligations. This process shares the remaining liability across all the depositors in the vault, promoting vault-wide stability. Vault governors can disable this feature if they prefer alternative methods to manage bad debt.
## Liquidation Bot​
Since liquidation operations are profitable, MEV bots are incentivized to proactively search for liquidation opportunities. Euler Labs maintains an open-source liquidation bot operated by Euler Labs and other partners.
## Proactive Liquidations​
For added control, users can choose alternate liquidation protection through EVC operators. This allows them to set custom stop-loss conditions, specify rewards, and define slippage limits, giving users the flexibility to manage their risk in ways that suit their needs.
  * Parameters
  * Liquidation Bot
  * Proactive Liquidations




---

## https://docs.euler.finance/concepts/oracles

Skip to main content
On this page
Each vault contains its own pricing configuration within the oracle router contract. The router maps the vault's asset and its collaterals to individual oracle adapters. The router's configuration can be adjusted by the governor to add or replace adapters.
## Modular Oracle System​
Euler vaults come with a powerful modular price oracle system which gives vault governors unprecedent flexibility in the pricing logic of their vaults. All oracle components conform to the same interface and can be easily combined to customize the pricing configuration.
Euler vaults can fetch prices from:
  * **Oracle providers:** Chainlink, Chronicle, RedStone Push/Pull, Pyth, and Balancer Rate Providers;
  * **Onchain data:** Uniswap V3, Pendle, ERC-4626, and Fixed Rates;


Check out the Oracle Dashboard to inspect available oracle adapters.
  * Modular Oracle System




---

## https://docs.euler.finance/concepts/rewards

Skip to main content
On this page
Participation in Euler vaults can be incentivized in two ways: onchain via Reward Streams or offchain via Merkl. Both reward types are seamlessly integrated into the Euler app.
## Reward Streams​
Reward Streams is an innovative open-source module empowering projects to seamlessly stream rewards to users of new markets in a permissionless and trustless manner. This module is a robust and adaptable implementation of the billion-dollar algorithm, enabling the simultaneous distribution of multiple reward tokens.
Unlike traditional methods, users can subscribe to receive their preferred rewards without the need to transfer their vault shares to a staking smart contract. This unique feature allows suppliers to earn rewards while concurrently taking out loans, presenting a dynamic and efficient approach to incentivizing and engaging users.
## Merkl​
Euler also supports off-chain reward distribution through Merkl. Campaigns can target supplying, borrowing or borrowing against a specific collateral. Accumulated rewards are updated once every ~4 hours and are claimable in the Euler app or directly on the Merkl Dashboard.
  * Reward Streams




---

## https://docs.euler.finance/concepts/risk-management

Skip to main content
On this page
Vaults on Euler are either governed or ungoverned. Ungoverned vaults are considered fully immutable as their parameters will stay fixed forever, and once removed, governance cannot be added at a later time.
On the other hand, governed vaults allow a privileged account to modify the parameters of the vault in response to market dynamics. The most common risk actions are changing the loan-to-value ratio (LTV) of the vault and modifying the supply and borrow caps.
## Security​
The governor is a highly sensitive role that can exert direct control over a vault's balances. This is why governed vaults do not appear in the Euler App by default. Instead, governors must pass a vetting process conducted by Euler Labs, which includes having a multisig with a timelock installed.




---

## https://docs.euler.finance/concepts/vault-types

Skip to main content
On this page
Verified vault types are lists that classify vaults based on the characteristics they share. Verification is carried out by smart contracts called ‘perspectives’ and is designed to check that a vault, and all the vaults it is directly or indirectly exposed to via its collaterals, has certain characteristics.
## Verified Types​
**Escrow** vaults hold deposits that are escrowed for use as collateral for taking out loans from other vaults. They do not earn their depositors interest because they do not allow borrowing. They are ungoverned.
**Governed** vaults hold deposits that can both be used as collateral and borrowed, earning depositors additional yield. A DAO, risk manager, or an individual manages these vaults, controlling risk, interest rates, loan-to-value, and other risk parameters. They are suited for passive lenders who trust the governor's management.
**Ungoverned** vaults have fixed parameters with no active governor to manage risk, making them suited to lenders who prefer to manage their own risk. They come in two types:
  * **0x** ungoverned vaults have zero exposure to governance through their collaterals
  * **nzx** ungoverned vaults have non-zero exposure to governance because they may accept collateral with governance exposure


**Earn** vaults are a special class of governed vaults that aggregate passive lender assets that can be directed by the vault governor to flow into any underlying ERC4626 vault, including both ungoverned or governed Euler vaults, but also external vaults like sDAI. The vault governor manages risk/reward by altering flows into underlying vaults with different properties.
**Unverified** vaults have no distinguishing characteristics except that they were deployed using the main EVK vault factory smart contract. This offers minimal guarantees about their functionality. The factory class is intended for advanced users only.
## Why are there many vault types?​
Vaults deployed using the Euler Vault Kit (EVK) are highly customisable. Not only do vaults themselves have many risk parameters that can be tuned by vault creators and governors, but they can also leverage the power of the Ethereum Vault Connector (EVC) to recognise deposits in any number of other vaults as collateral.
These features of Euler provide vault creators and end users with a lot of flexibility, but also potentially make it harder for users to understand the features and risks associated with the vaults they want to use. Risk, in particular, comes not just from the vault a user directly interacts with, but also emerges from the direct and indirect exposure a vault has to the other vaults it recognises as collateral. This is where verified vault types are designed to help users.
Ultimately there are many possible ways to classify vaults, and so any classification schema is always going to be artificial. Users always need to do their due diligence before choosing to use a vault, regardless of what type it is classified as. Verified vault types are not prescriptive about vault safety or anything else. However, they may be useful in helping users to quickly recognise vaults that share certain characteristics.
Of particular concern to users is likely the mode of risk management used to set risk/reward parameters on a vault. If a vault is governed, passive users know that they need to trust the vault governor to adjust vault parameters in a sensible way as the risk environment changes. They need to trust the governor to limit a vault’s exposure to other risky vaults. If a vault is ungoverned, users know that vault parameters, including its exposure to other vaults, cannot change in response to the changing economic environment. They know that they will therefore need to proactively manage their own risks.
There are trade-offs between the two approaches that have been discussed at length elsewhere. But either way, it is important for users to be able to distinguish between these two major classes of vaults and the risks associated with them. The verified vault types listed above are there to help users to better make this distinction.
However, if the verified vault types suggested by the user interface are found not to be useful, then users have two options. First, they can opt to toggle off the classifications suggested by the default user interface and then manually add the addresses of vaults that they wish to use. Alternatively, more sophisticated users can create their own perspective smart contract and define their own class of vaults (see here for inspiration). These perspectives and their associated lists of vaults can then be uploaded to the user interface under the connected wallet’s settings.
  * Verified Types
  * Why are there many vault types?




---

## https://docs.euler.finance/concepts/vaults

Skip to main content
The Euler Vault Kit (EVK) allows anyone to deploy, configure and connect _credit vaults_ in various ways. Credit vaults are ERC-4626 compatible vaults extended with functionality for borrowing and liquidations, interest rates, governance, hooks, and more.
Like standard ERC-4626 vaults, Euler's credit vaults enable users to deposit a specified ERC-20 token and receive interest-accruing vault share tokens that represent their deposit. On top of that, credit vaults allow users to borrow tokens deposited in the vault and repay them at a later date. The vault's interest rate model determines the cost of borrowing, while the price oracle helps to keep track of the health of borrowing positions.
The rules for borrowing from a credit vault are determined by a privileged address called the _governor admin_. They can enable another credit vault to be recognized as collateral and set its maxmium loan-to-value ratio that borrowers must abide to. The vault's price oracle allows existing positions to be continually appraised and should a borrower come into violation of the LTV rules, their position becomes eligible for liquidation.
EVK credit vaults also implement more advanced functions such as flashloans, supply and borrow caps, interest rate fees, mandatory block delays for liquidations, user balance tracking and forwarding, arbitrary hooks on operations, debt socialization, and more.


---

## https://docs.euler.finance/contractAddresses

Skip to main content
The contract addresses are fetched from the euler-interfaces repo you can also view them here along with their corresponding ABI and interface files.
No networks available


---

## https://docs.euler.finance/developers/evc/howDoesItWork

Skip to main content
When users wish to borrow, they first need to link their account and collateral vaults to the borrowed-from vault through the EVC. Thanks to that, the liability vault, also known as the controller, will be consulted whenever a user wants to perform an action that could potentially impact the account's solvency, such as withdrawing collateral or taking a borrow. The EVC is responsible for calling the controller to determine whether the action is allowed or if it should be blocked to prevent account insolvency. You can think of the EVC as a special-purpose multicall contract that provides:
  * Caller authentication
  * Account and vault status enforcement
  * Multiple operations batching


For more detailed information, see the EVC dedicated website.


---

## https://docs.euler.finance/developers/evc/keyConcepts

Skip to main content
On this page
## Authentication and Authorization​
The EVC handles authentication while vaults manage authorization. When integrating with the EVC, it's important to understand this separation of concerns:
  * The EVC verifies that requests come from authorized users or contracts
  * Vaults determine if the authenticated user has sufficient permissions or balances for the requested operation


## Account Management​
The EVC provides each Ethereum address with 256 virtual accounts which allow a user to maintain multiple isolated positions within a single wallet. When integrating with the EVC, you can leverage these virtual accounts to:
  * Build multiple borrowing positions (because each account can have at most one open borrow position)
  * Isolate different trading strategies
  * Manage risk across different positions


## Batch Operations​
One of the EVC's core features is the ability to batch multiple operations into a single transaction. This enables:
  * Efficient position building
  * Complex trading strategies
  * Gas optimization for users


## Operators​
Operators are a powerful feature that extends beyond traditional token approvals. An operator is a contract or EOA that can act on behalf of a specified account. When enabled, operators can interact with vaults (i.e. withdraw/borrow funds) and perform other account operations on the EVC-aware contracts on behalf of the account that enabled them.
Common use cases for operators include:
  * Stop-loss/take-profit position modifiers
  * Trailing stop orders
  * Position management automation
  * Keeper-based custom liquidation strategies


For more detailed information, see the EVC dedicated website.
  * Authentication and Authorization
  * Account Management
  * Batch Operations




---

## https://docs.euler.finance/developers/evc/overview

Skip to main content
The Ethereum Vault Connector (EVC) is an open-source interoperability layer that connects credit vaults together to enable their use as collateral for one another. The EVC allows users to efficiently batch and execute multiple operations in one transaction.
For more detailed information, see the EVC dedicated website.


---

## https://docs.euler.finance/developers/evk/liquidationBot

Skip to main content
On this page
The code for Euler's liquidation bot can be found in the open source github repo here. Below is a description on how the bot works, as well as suggestions and tips for where new integrations would need to be made.
The bulk of the liquidation bot logic can be found in the liquidation_bot.py file, with some periphery/helper functions in the other files in the same folder.
The bot can be run on multiple chains simultaneously - in the config.yaml file simply copy the format of an existing chain under its chain ID, add the relevant contract addresses as well as the relevant RPC node to your .env file. Chain IDs to be included in the bot can be specified in the `app/__init__.py` file.
## How it works​
  1. **Account Monitoring** :
     * The primary way of finding new accounts is scanning for `AccountStatusCheck` events emitted by the EVC contract to check for new & modified positions.
     * This event is emitted every time a borrow is created or modified, and contains both the account address and vault address.
     * Health scores are calculated using the `accountLiquidity` implemented by the vaults themselves.
     * Accounts are added to a priority queue based on their health score and position size with a time of next update, with low health accounts being checked most frequently.
     * EVC logs are batched on bot startup to catch up to the current block, then scanned for new events at a regular interval.
  2. **Liquidation Opportunity Detection** :
     * When an account's health score falls below 1, the bot simulates a liquidation transaction across each collateral asset.
     * The bot gets a quote to swap the collateral assets into the debt assets, and simulates a liquidation transaction on the Liquidator.sol contract.
     * Gas cost is estimated for the liquidation transaction, then checks if the leftover assets after repaying debt is greater than the gas cost when converted to ETH.
     * If this is the case, the liquidation is profitable and the bot will attempt to execute the transaction.
  3. **Liquidation Execution -Liquidator.sol**:
     * If profitable, the bot constructs a transaction to call the `liquidateSingleCollateral` function on the Liquidator contract.
     * The Liquidator contract then executes a batch of actions via the EVC containing the following steps: 
       1. Enables borrow vault as a controller.
       2. Enable collateral vault as a collateral.
       3. Call liquidate() on the violator's position in the borrow vault, which seizes both the collateral and debt position.
       4. Withdraws specified amount of collateral from the collateral vault to the swapper contract.
       5. Calls the swapper contract with a multicall batch to swap the seized collateral, repay the debt, and sweep any remaining dust from the swapper contract.
       6. Transfers remaining collateral to the profit receiver.
       7. Submit batch to EVC.
     * There is a secondary flow still being developed to use the liquidator contract as an EVC operator, which would allow the bot to operate on behalf of another account and pull the debt position alongside the collateral to the account directly. This flow will be particularly useful for liquidating positions without swapping the collateral to the debt asset, for things such as permissioned RWA liquidations.
  4. **Swap Quotation** :
     * The bot currently uses Euler's Swap API meta-aggregator to get quotes for swapping seized collateral to repay debt. The open source repository as well as instructions on how to run your own can be found here.
     * Currently the bot withdraws and swaps all of the collateral asset into the debt asset, however an optimization could be made to only withdraw enough collateral to repay the debt, which requires some binary search logic for swap venues that can't properly handle exact output swaps.
  5. **Profit Handling** :
     * Any profit is sent to a designated receiver address.
     * Profit is sent in the form of overswapped debt asset (see above).
  6. **Slack Notifications** :
     * The bot can send notifications to a slack channel when unhealthy accounts are detected, when liquidations are performed, and when errors occur.
     * The bot also sends a report of all low health accounts at regularly scheduled intervals, which can be configured in the config.yaml file.
     * In order to receive notifications, a slack channel must be set up and a webhook URL must be provided in the .env file.


## How to run the bot​
### Installation​
The bot can be run either via building a docker container or manually. In both instances, it runs via a flask app to expose some endpoints for account health dashboards & metrics.
Before running either, setup a .env file by copying the .env.example file and updating with the relevant contract addresses, an EOA private key & API keys. Then, check config.yaml to make sure parameters, contracts, chains, and ABI paths have been set up correctly.
#### Running locally​
To run locally, we need to install some dependencies and build the contracts. This will setup a python virtual environment for installing dependencies. The below command assumes we have foundry installed, which can installed from the Foundry Book.
Setup:
```
foundryuppython3 -m venv venvsource venv/bin/activatepip install -r requirements.txtcd redstone_script && npm install && cd ..forge install && forge buildcd lib/evk-periphery && forge build && cd ../..mkdir logs state
```

**Run** :
```
python flask run --port 8080
```

Change the Port number to whatever port is desired for exposing the relevant endpoints from the `routes.py` file.
#### Docker​
After creating the .env file, the below command will create a container, install all dependencies, and start the liquidation bot: `docker compose build --progress=plain && docker compose up`
This may require some configuration changes on the Docker image to a basic Python enabled container.
### Configuration​
  * The bot uses variables from both the `config.yaml` file and the `.env` file to configure risk, chain, and address settings and private keys.


Make sure to build the contracts in both src and lib to have the correct ABIs loaded from the evk-periphery installation
Configuration through `.env` file:
REQUIRED:
  * `LIQUIDATOR_EOA, LIQUIDATOR_PRIVATE_KEY` - public/private key of EOA that will be used to liquidate
  * `RPC_URL` - RPC provider endpoint (Infura, Rivet, Alchemy etc.)
  * `SWAP_API_URL` - URL where you have deployed the Swap API meta-aggregator


OPTIONAL:
  * `SLACK_WEBHOOK_URL` - Optional URL to post notifications to slack
  * `RISK_DASHBOARD_URL` - Optional, can include a link in slack notifications to manually liquidate a position


Configuration in `config.yaml` file:
  * Risk parameters:
    * `HS_LIQUIDATION, HS_HIGH_RISK, HS_SAFE` - Bounds for interval update timing
    * `TEENY, MINI, SMALL, MEDIUM` - Size bounds for interval timing
    * `TEENY_LIQ, TEENY_HIGH, TEENY_LOW, TEENY_SAFE, etc` - Timing intervals depening on position size & HS
  * Reporting & other parameters:
    * `LOW_HEALTH_REPORT_INTERVAL` - Interval between low health reports
    * `SLACK_REPORT_HEALTH_SCORE` - Threshold to include an account on the low health report
    * `BORROW_VALUE_THRESHOLD` - Minimum $ amount to include in report
    * `LOGS_PATH, SAVE_STATE_PATH` - Path directing to save location for Logs & Save State
    * `SAVE_INTERVAL` - How often state should be saved
    * `PROFIT_RECEIVER` - Targeted receiver of any profits from liquidations
    * `EVAULT_ABI_PATH, EVC_ABI_PATH, LIQUIDATOR_ABI_PATH` - Paths to compiled contracts
  * Chain specific parameters:
    * Specified top level with Chain ID
    * `name` - Chain name
    * `EVC_DEPLOYMENT_BLOCK` - Block that the contracs were deployed
    * `RPC_NAME` - env variable name of relevant RPC URL
    * `WETH, EVC, SWAPPER, SWAP_VERIFIER, LIQUIDATOR_CONTRACT, PYTH` - Relevant deployed contract addresses.


### Deploying​
If you want to deploy your own version of the liquidator contract, you can run the command below:
```
forge script contracts/DeployLiquidator.sol --rpc-url $RPC_URL --broadcast --ffi -vvv --slow
```

### Notes​
Pull Oracles
  * Many vaults on Euler are configured with Pull oracles, that must be updated prior to any vault actions taking place. Logic for both Pyth and Redstone pull oracles is implemented in the PullOracleHandler class as well as some specific functions in the Liquidator Contract


Swap API
  * As mentioned previously the bot runs quotes through the Swap API, which is easy to set up locally with your own API keys
  * To add addtional swap venues for specific assets, this would be best done in the `Quoter` class to check the input/output tokens, and send the request to a new venue after filtering


There are quite a few optimizations/improvements that likely could be made with more time, for instance:
  * Storing enabled collateral/controller within the liquidator contract itself to avoid calls to EVC to check & enable already enabled collaterals
  * Reducing the number of calls made to the RPC with smarter caching
  * Smarter gas price & slippage profitability checks
  * Potentially skipping interaction with Liquidator contract entirely and constructing batch off chain
  * More precise swap calculations to avoid overswapping
  * Deconstruction of Pull oracle batches to avoid unnecessary updates on oracles that aren't being used
  * Secure routing via flashbots/bundling/etc


  * How it works
  * How to run the bot
    * Installation
    * Configuration




---

## https://docs.euler.finance/developers/evk/overview

Skip to main content
The Euler Vault Kit is a collection of components for building ERC-4626 compliant vaults. It is designed to be flexible so as to support a variety of use-cases.
Anyone who wishes to create a vault can choose some basic parameters and then invoke the EVK Factory. The parameters that much be chosen include:
  * Which other vaults can be accepted as collateral to borrow from your vault (if any), and what the maximum LTV (Loan-To-Value) ratio can be.
  * What pricing methodology should be used to price the assets contained in the vault, and the collaterals.
  * If there are any supply/borrow caps that limit the sizes handled by the vault.
  * Whether the creator should retain governance control so as to adjust the parameters in the future, or if the vault should be ungoverned.


Vault creators can install a fee receiver to earn a portion of the fees paid as interest, or forgo this in order to make the vault more attractive for users.
For the full technicaly details, see the EVK Whitepaper.


---

## https://docs.euler.finance/developers/feeFlow/dutch-auction

Skip to main content
Let us assume a protocol is accruing fees in a variety of different asset types across a wide variety of markets. Each market has a function that allows anyone to transfer accrued fees from the market to a FeeFlowController smart contract inside of FeeFlow at a time of their choosing. Being costly to do this, and in the absence of any other incentive to do so, this function is unlikely to be called on a market very often.
The FeeFlowController accumulates fees (often implicitly, see below) and periodically auctions them via a Dutch auction. The auction takes place in discrete epochs. Each epoch, the initPrice of the auction starts at a factor priceMultiplier times the settlement price of the auction in the prior epoch. It then falls linearly over time, tending to zero, over an epochPeriod. For example, the auction might start at a factor priceMultiplier=2 times the settlement price of the prior auction and last an epochPeriod=100 days.
At the beginning of an epoch, the FeeFlowController holds no fees and has a high price, so is unlikely to settle any time soon. However, as fees accrue on markets, and the auction price falls, there will usually come a time when the auction price is lower than the aggregate value of all accrued fees. The first person to pay the auction price at this point is allowed to claim all assets in the FeeFlowController.
Note that in practice the winning auction bidder will likely monitor the value of accrued fees across markets off chain and only transfer them to the FeeFlowController just-in-time; that is, in the same transaction or same block as the pay the winning bid for the auction. Thus the FeeFlowController will often not actually hold many, or indeed any, assets. It will instead usually only implicitly hold assets.
Inevitably, accrued fees in some of the markets will not be desired by bidders. They might not be worth the cost of gas to transfer them, or sell them, in the future. These will simply remain in their respective markets and may or may not be purchased in a later auction.


---

## https://docs.euler.finance/developers/feeFlow/overview

Skip to main content
Protocols in decentralised finance (DeFi) often generate revenues by accruing fees across a range of markets in a variety of different asset types. The default behaviour of the protocol will typically be to hold all these asset types on the protocol’s balance sheet as protocol-owned liquidity (POL). However, this will often be a suboptimal use of accrued fees.
In many instances it might be beneficial for the protocol to convert accrued fees into a single currency (perhaps USDC or ETH or the project’s native token) for accumulation or future distribution. Yet mechanisms for converting accrued fees into a single asset are notoriously problematic and generally not common in DeFi. Specifically, they are often inefficient, vulnerable to value extraction by validators (MEV), or otherwise require interventions by governance or trusted parties.
Here, we outline Fee Flow: an efficient, decentralised, MEV-resistant mechanism for protocols to be able to auction their accrued fees for a single type of asset.


---

## https://docs.euler.finance/developers/introduction

Skip to main content
On this page
Euler V2 is a modular lending protocol built around ERC-4626 vaults. It is designed to be highly flexible, so that the same system can be used to support a variety of financial products, and so that these products can interoperate:
  * Governed/immutable
  * Hypothecated collateral/escrowed collateral
  * Permissionless/permissioned
  * Static/dynamic interest rate models
  * Market/fundamental pricing


## Architecture​
The three primary components are:
  * Ethereum Vault Connector (EVC): This is a singleton "hub" contract that connects all of the vaults together, and tracks which accounts are currently being used as collateral to borrow from which other vaults. In addition, the EVC functions as a supercharged multicall-style contract, allowing advanced usage such as batching, simulations, gasless transactions, delegation of privileges to third-party contracts, and more.
  * Euler Vault Kit (EVK): Although the EVC can link together any vault implementation that implements the EVC protocol, the EVK is the primary reference implementation and is the recommended basis for building lending platforms. The EVK supports creation of vaults in a variety of configurations, as determined by the vault creator.
  * Euler Price Oracle (EPO): Accurate prices are critical for the safety of a lending platform. The EPO defines a common interface for querying prices, and includes a reference implementation capable of adapting all the common oracle classes.


  * Architecture




---

## https://docs.euler.finance/developers/oracle/ipriceOracle

Skip to main content
Each vault has the address of a price oracle installed. This address is immutable and cannot be changed, even by the vault governor. If updates to pricing sources are desired, this address should be a governed EulerRouter pricing component. All oracles must implement the IPriceOracle interface below:
```
interface IPriceOracle {  /// @return General description of this oracle implementation.  function name() external view returns (string memory);  /// @return outAmount The amount of `quote` that is equivalent to `inAmount` of `base`.  function getQuote(    uint256 inAmount,    address base,    address quote  ) external view returns (uint256 outAmount);  /// @return bidOutAmount The amount of `quote` you would get for selling `inAmount` of `base`.  /// @return askOutAmount The amount of `quote` you would spend for buying `inAmount` of `base`.  function getQuotes(    uint256 inAmount,    address base,    address quote  ) external view returns (uint256 bidOutAmount, uint256 askOutAmount);
```

This interface shapes oracle interactions in an important way: it forces the consumer to think in amounts rather than prices.
A subset of this interface (getQuote) has been standardized in ERC-7726.


---

## https://docs.euler.finance/developers/oracle/oracleAdapters

Skip to main content
On this page
An adapter is a minimal, fully immutable contract that queries an external price feed. It is the atomic building block of the Euler Price Oracles library.
## Design Principles​
The `IPriceOracle` interface is permissive in that it does not prescribe a particular way to implement it. However the adapters in this library adhere to a strict set of rules that we believe are necessary to enable safe, open, and self-governed markets to flourish.
### Immutable​
Adapters are fully immutable without governance or upgradeability.
### Minimally Responsible​
An adapter connects to one pricing system and queries a single price feed in that system.
### Bidirectional​
An adapter works in both directions. If it supports quoting `X/Y` it must also support `Y/X`.
### Observable​
An adapter's parameters and acceptance logic are easily observed on-chain.
## Summary of Adapters​
Adapter| Type| Method| Supported Pairs| Parameters  
---|---|---|---|---  
External| Push| Provider feeds| feed, max staleness  
External| Push| Provider feeds| feed, max staleness  
External| Pull| Provider feeds| feed, max staleness, max confidence interval  
External| Pull| Provider feeds| feed, max staleness, cache ttl  
Onchain| Rate| wstETH/stETH| -  
LidoFundamentalOracle| Onchain| Rate| wstETH/ETH| -  
Onchain| TWAP| UniV3 pools| fee, twap window  
Onchain| TWAP| Pendle markets| pendle market, twap window  
Onchain| Rate| Balancer rate providers| rate provider  
Onchain| Rate| Any| rate  
  * Design Principles
    * Minimally Responsible
    * Bidirectional
    * Observable
  * Summary of Adapters




---

## https://docs.euler.finance/developers/oracle/overview

Skip to main content
Inside a vault, each collateral is configured as the address of another vault, not the underlying asset (unless the asset is specially constructed to also function as a collateral vault). This means that the value of a user's collateral is in fact the value of the vault's shares. A vault share is not necessarily equal to a unit of the underlying asset because of the exchange rate.
Because converting quantities of shares to underlying asset amounts is itself a pricing operation, this responsibility is delegated to the price oracle. In some cross-chain designs, the price oracle may also be responsible for determining the exchange rate of a corresponding vault on a separate chain.
The Euler Price Oracle system is a composable on-chain pricing system. It is built around an interface called IPriceOracle, which is an abstraction for querying a diverse range of external pricing oracles and normalising their answers.
For full technical details, see the EPO Whitepaper.


---

## https://docs.euler.finance/developers/oracle/quotes

Skip to main content
Price fractions are never directly returned by the interface. Instead, the oracle acts as though it is quoting swap amounts. This avoids certain catastrophic losses of precisions, especially with low-decimal tokens (see an example with SHIB/USDC).
The quoting interface offers several benefits to consumers:
  * More intuitive queries: Oracles are commonly used in DeFi to determine the value of assets. getQuote does exactly that.
  * More expressive interface: The unit price is a special case of a quote where inAmount is one whole unit of base.
  * Safe and flexible integrations: Under IPriceOracle adapters are internally responsible for converting decimals. This allows consumers to decouple themselves from a particular provider as they can remain agnostic to its implementation details.


# Bid/Ask Pricing
Euler Price Oracles additionally expose getQuotes which returns two prices: the selling price (bid) and the buying price (ask).
Bid/ask prices are inherently safer to use in lending markets as they can accurately reflect instantaneous price spreads. While few oracles support bid/ask prices currently, we anticipate their wider adoption in DeFi as on-chain liquidity matures.
Importantly getQuotes allows for custom pricing strategies to be built under the IPriceOracle interface:
Querying two oracles and returning the lower and higher prices. Reporting two prices from a single source e.g. a TWAP and a median. Applying a synthetic spread or a volatility-dependent confidence interval around a mid-price.


---

## https://docs.euler.finance/developers/periphery/ERC20s

Skip to main content
On this page
Directory: src/ERC20
Collection of ERC20 contracts that can be used for different purposes.
## `ERC20WrapperLocked`​
A wrapper for locked ERC20 tokens that can be withdrawn as per the lock schedule defined in the inheriting contract, i.e. `RewardToken`. Regular wrapping, unwrapping are only supported for whitelisted callers with an `ADMIN` whitelist status. Regular ERC20 transfers are only supported between two whitelisted accounts. Under other circumstances, conditions apply; look at the implementation. If the account balance is non-whitelisted, their tokens can only be withdrawn as per the lock schedule and the remainder of the amount is transferred to the receiver address configured. If the account has a `DISTRIBUTOR` whitelist status, their tokens cannot be unwrapped by them, but in order to be unwrapped, they can only be transferred to the account that is not whitelisted and become a subject to the locking schedule or transferred to the account with an ADMIN whitelist status. A whitelisted account can always degrade their whitelist status and become a subject to the locking schedule.
  * `ERC20WrapperLocked`




---

## https://docs.euler.finance/developers/periphery/eulerRouterFactory

Skip to main content
Directory: src/EulerRouterFactory
Immutable factory contract that can be used to deploy instances of `EulerRouter`. It allows the deployment provenance of router instances to be verified by perspectives.
  * Although the factory (and implementation) is immutable, the routers themselves are created with a user-specifiable address as the governor so that adapters can be installed. If a perspective wishes for the routers to be immutable, it must also confirm this governor has been changed to `address(0)`.
  * Routers can have fallbacks specified. If present, these must also be verified to be safe.




---

## https://docs.euler.finance/developers/periphery/evkPeriphery

Skip to main content
On this page
Periphery contracts for the Euler Ecosystem. The periphery consists of several components that are designed to be used on-chain:
  * ERC20s
  * Governor contracts
  * Hook Target contracts
  * Interest Rate Model factories
  * Euler Router factory
  * Perspectives
  * Swaps
  * Lenses


## ERC20s​
Directory: src/ERC20
Collection of ERC20 contracts that can be used for different purposes.
## Governor contracts​
Directory: src/Governor
Collection of specialized governor contracts that can be installed as an admin in the EVK factory contract and as a governor admin in the EVK credit vaults.
## Hook Target contracts​
Directory: src/HookTarget
Collection of hook target contracts that can be configured as hook targets in the EVK credit vaults.
## Interest Rate Model factories​
Directory: src/IRMFactory
Collection of contracts for deploying interest rate models that can be used by the EVK credit vaults.
## Euler Router factory​
Directory: src/EulerRouterFactory
Immutable factory contract that can be used to deploy instances of `EulerRouter`. It allows the deployment provenance of router instances to be verified by perspectives.
## Perspectives​
Directory: src/Perspectives
Collection of contracts that encode validity criteria for the EVK credit vaults.
## Swaps​
Directory: src/Swaps
Utilities for performing DEX swaps for EVK credit vault operations.
## Lenses​
Directory: src/Lens
Collection of contracts to assist with off-chain querying of the accounts and credit vaults' chain-state.
  * Governor contracts
  * Hook Target contracts
  * Interest Rate Model factories
  * Euler Router factory
  * Perspectives




---

## https://docs.euler.finance/developers/periphery/governors

Skip to main content
On this page
Directory: src/Governor
Collection of specialized governor contracts that can be installed as an admin in the EVK factory contract and as a governor admin in the EVK credit vaults.
## `FactoryGovernor`​
This is a contract that is intended to be installed as the `upgradeAdmin` of the `GenericFactory` that is used to create EVK vaults. When invoked by a caller of suitable privilege, this contract will invoke methods on the factory.
There are 3 privilege levels: default admin and guardian.
  * Default admins can invoke the factory with arbitrary calldata using the `adminCall()` function.
  * Pause Guardians can call `pause()` which replaces the factory implementation with a ReadOnlyProxy instance. To unpause, a default admins should use `adminCall()` to reinstate a (possibly fixed) implementation.
  * Unpause Guardians can call `unpause()` to reinstate a previously paused implementation in case the factory implementation was replaced with a ReadOnlyProxy instance due to a false positive.


Note that invoking `pause()` on a `FactoryGovernor` will instantly pause all upgradeable vaults created by this factory, so it should be used with caution. Non-upgradeable vaults will be unaffected.
### `ReadOnlyProxy`​
This is a simple proxy contract that forwards all calls to an wrapped implementation. However, it always invokes the calls with `staticcall`, meaning that read-only operations will succeed, but any operations that perform state modifications will fail.
The intent behind this contract is to minimise the damage to third-party integrations in the event of a pause. State-changing operations will fail until the contract is unpaused, but at least operations like reading balance and debt amounts will succeed.
Note that this contract uses a `staticcall`-to-self trick similar to the EVK.
## `GovernorGuardian`​
Instances of this contract are intended to be installed as the governor of one or more EVK vaults. Similarly to `FactoryGovernor`, these are proxy-like contracts that allow users with the default admin role to invoke the vault with `adminCall()`, and users with the guardian role to `pause()`.
In addition, there is an `unpause()` function that can be invoked by anybody, once a `PAUSE_DURATION` amount of time has passed. Guardians can unpause immediately.
A `PAUSE_COOLDOWN` parameter prevents a guardian from continually pausing a vault: They must wait until a certain amount of time has elapsed after the previous pause.
In order to allow selective re-enabling of methods, guardians can invoke a `changePauseStatus()` function. This could be used to re-enable a subset of functionality, for example permitting withdrawals and repays but blocking a method that was discovered to contain buggy behaviour.
## `GovernorAccessControl`​
This contract can be installed as the governor of one or more EVK vaults and allows whitelisted callers to invoke specific functions on target contracts. It uses a fallback function to authenticate the caller and forward the call to the target contract. The address of the target contract is expected to be appended by the caller as trailing calldata and is extracted from it accordingly.
### `GovernorAccessControlEmergency`​
The `GovernorAccessControlEmergency` inherits from `GovernorAccessControl` and includes emergency functionality for certain critical operations. This allows authorized users to perform emergency actions without needing the full selector role:
  1. Emergency LTV Adjustment: Users with the `LTV_EMERGENCY_ROLE` can lower the borrow LTV without changing the liquidation LTV. As with all changes to borrow LTV, this takes effect immediately. The current ramp state for liquidation LTV (if any) is preserved.
  2. Emergency Vault Pausing: Users with the `HOOK_EMERGENCY_ROLE` can disable all operations on the vault.
  3. Emergency Caps Lowering: Users with the `CAPS_EMERGENCY_ROLE` can lower supply and/or borrow caps.


These emergency roles provide a way to quickly respond to critical situations without compromising the overall access control structure of the governor.
  * `FactoryGovernor`
    * `ReadOnlyProxy`
  * `GovernorGuardian`
  * `GovernorAccessControl`
    * `GovernorAccessControlEmergency`




---

## https://docs.euler.finance/developers/periphery/hookTarget

Skip to main content
On this page
## `HookTargetGuardian`​
Similar to `GovernorGuardian`, this contract can be associated with one or more vaults. Instead of being installed as a governor however, instances of this contract are installed as hook targets.
The advantage of using a hook target guardian is that multiple vaults can be instantly paused by one invocation of the hook guardian, as opposed to individually pausing multiple vaults. The guardian may not even know about all the different vaults it is pausing. However, the hook target guardian adds an extra gas overhead for normal operations on the vault.
Similarly to `GovernorGuardian`, there is an `unpause()` function. Although it can only be called by the guardian, the operations get unpaused automatically after a `PAUSE_DURATION` amount of time.
Same as for `GovernorGuardian`, a `PAUSE_COOLDOWN` parameter prevents a guardian from continually pausing a vault: They must wait until a certain amount of time has elapsed after the previous pause.
## `HookTargetAccessControl`​
This contract is designed to be used as a hook target for EVK vaults and allows specific operations on the vault to be executed only by whitelisted callers.
  * `HookTargetGuardian`
  * `HookTargetAccessControl`




---

## https://docs.euler.finance/developers/periphery/irmFactories

Skip to main content
On this page
Directory: src/IRMFactory
Collection of contracts for deploying interest rate models that can be used by the EVK credit vaults.
## `EulerKinkIRMFactory`​
It is an immutable factory contract for deploying Linear Kink IRM instances, used by EVK vaults. It does some basic parameter validation and tracks the addresses of created IRMs, so that the deployment provenance of IRM instances can be verified by perspectives. Linear Kink IRMs are immutable and stateless.
  * `EulerKinkIRMFactory`




---

## https://docs.euler.finance/developers/periphery/lenses

Skip to main content
On this page
Directory: src/Lens
Collection of contracts to assist with off-chain querying of the accounts and credit vaults' chain-state.
## `AccountLens`​
Contract for querying account-related information from the EVK credit vaults, EVC and rewards streams. It allows to calculate time to liquidation of a given account borrowing from a specific vault.
## `VaultLens`​
Contract for querying vault-related information including vault configuration, state, interest rates, LTV ratios, and price information.
## `IRMLens`​
Contract for querying interest rate model information. Used by the `VaultLens`.
## `OracleLens`​
Contract for querying oracle-related information. Used by the `VaultLens`.
## `UtilsLens`​
Contract containing utility functions for calculating interest rates, APYs, time to liquidation, and fetching price information. Used by the `AccountLens` and `VaultLens`.
## `LensTypes`​
Solidity file containing struct definitions used by the lens contracts for organizing and returning complex data structures.




---

## https://docs.euler.finance/developers/periphery/perspectives

Skip to main content
On this page
Directory: src/Perspectives
Collection of contracts that encode validity criteria for the EVK credit vaults.
Since the EVK is a kit, it attempts to be maximally flexible and doesn't enforce policy decisions on vault creators. This means that it is possible to create vaults with insecure or malicious configurations. Furthermore, an otherwise secure vault may be insecure because it accepts an insecure collateral as collateral (or a collateral vault itself accepts insecure collateral, etc, recursively).
Perspectives provide a mechanism for validating properties of a vault using on-chain verifiable logic. A perspective is a contract that implements the following interface:
```
interface IPerspective {  function perspectiveVerify(address vault, bool failEarly) external;  function isVerified(address vault) external view returns (bool);  function verifiedLength() external view returns (uint256);  function verifiedArray() external view returns (address[] memory);
```

`perspectiveVerify` will inspect the configuration of the provided vault and determine whether it meets the desired properties of this particular perspective and, if so, will record this fact in its storage. This recorded fact can be thought of as a cached or memoised value, so the gas-expensive verification only needs to happen once. Afterwards, `isVerified` and `verifiedArray` can be used to cheaply read this cached result.
Note that there is not necessarily any mechanism to invalidate the cache, so most perspectives should reject vaults that have a governor installed who could change the configuration to something not suitable. Alternatively, perspectives may check that the governor is a trusted entity, or perhaps that the governor is a limited contract and the verified values be changed by the governor.
## Token (Vault) Lists​
The primary use-case of perspectives is to provide a permissionless, on-chain approximation of Token Lists. Perspectives do not replace Token Lists, and user interfaces may choose to use both of these systems. A vault can be matched by many perspectives, and there is nothing stopping anybody from making a new perspective for any purpose.
Just like with Token Lists, user interfaces will allow users to import which perspectives they would like to use to filter vaults that don't meet their trust criteria. Advanced UIs may support special filtering features, such as "all vaults that meet 2 or more of the configured perspectives", or "all vaults on this perspective but not on this perspective".
Although any contract that conforms to `IPerspective` can be used as a perspective, we have created a flexible reference implementation that users or projects can adapt to fit their requirements.
If your UI would like to display vaults that conform to specific criteria, you can rely on the `verifiedArray` function of the already deployed perspective(s) or deploy your own.
For more details, including perspective types see whitepaper.
  * Token (Vault) Lists




---

## https://docs.euler.finance/developers/periphery/swaps

Skip to main content
On this page
Directory: src/Swaps
Utilities for performing DEX swaps for EVK credit vault operations.
The `Swapper` and `SwapVerifier` contracts are helper contracts designed to facilitate swaps and swap-to-repay operations on EVK vaults using EVC batches. A swap operation in Euler is executed through two consecutive calls to these contracts within an EVC batch.
## Swapper​
The `Swapper` contract is provided with tokens to sell, either by withdrawing from a collateral vault or by borrowing. It can then execute multiple external calls to arbitrary contracts, most often DEXs, to carry out the trade. The Swapper contract functions as a black box and does not guarantee that the trade will be executed as requested. It can be replaced at any time without requiring an audit. The system's security is ensured by the `SwapVerifier` contract.
## SwapVerifier​
Executing token swaps can be complex, but verifying them is straightforward. Given a specific amount of a token to sell, verifying a trade's correctness requires only confirming that the amount of the purchased token matches the quoted amount or falls within an acceptable slippage range. In Euler, this verification responsibility is delegated to the `SwapVerifier` contract, which, unlike the `Swapper`, is a trusted and fully audited contract.
### More information​
For a general overview of swaps in Euler and links to technical resources, please refer to the Swaps section
  * SwapVerifier
    * More information




---

## https://docs.euler.finance/developers/rewardStreams/

Skip to main content
Reward Streams is a powerful and flexible implementation of the billion-dollar algorithm, a popular method for proportional reward distribution in the Ethereum developer community. This project extends the algorithm's functionality to support both staking and staking-free (based on balance changes tracking) reward distribution, multiple reward tokens, and permissionless registration of reward distribution schemes (reward streams). This makes Reward Streams a versatile tool for incentivizing token staking and holding in a variety of use cases.
Reward Streams was developed to address the limitations of the billion-dollar algorithm, and to provide a more flexible and powerful implementation. Here's what Reward Streams offers:
  1. A common base contract (`BaseRewardStreams`) that is reused by both staking and balance-tracking mechanisms of rewards distribution.
  2. An easy-to-use mechanism for balance-tracking reward distribution, which requires only a subtle change to the ERC-20 token contract.
  3. A permissionless mechanism to create a reward stream, enabling anyone to incentivize staking/holding of any token with any reward.
  4. The ability for users to earn up to 5 different reward tokens simultaneously for staking/holding of a single rewarded token.
  5. Additive, fixed length epoch-based distribution of rewards where the reward rate may differ from epoch to epoch.
  6. Protection against reward tokens being lost in case nobody earns them.




---

## https://docs.euler.finance/developers/rewardStreams/howDoesItWork

Skip to main content
On this page
Reward Streams operates in two modes of rewards distribution: staking and balance-tracking. Each mode has a separate contract implementation.
## Reward Streams Mechanism​
### Tracking Reward Distribution​
The balance-tracking `TrackingRewardStreams` implementation inherits from the `BaseRewardStreams` contract. It defines the `IBalanceTracker.balanceTrackerHook` function, which is required to be called on every transfer of the rewarded token if a user opted in for the hook to be called. Provided that the account opted in for their balance to be tracked, on every balance change of the account which is a result of the deposit, withdrawal, shares transfer etc., the credit vault contract calls the `balanceTrackerHook` function. Once the hook is called, the contract updates the account's balance and all the enabled rewards distribution data in order to track the rewards accrual.
The already deployed `TrackingRewardStreams` (referred to as `BalanceTracker` in the deployed contract addresses section) can be used by any other newly developed ERC20-like contract. Assuming that one wants to embed the reward distribution mechanism into their own contract, it is enough that the token contract calls the `balanceTrackerHook` function on every balance change of the account. For inspiration, one can take a look at the mock ERC20 token contract here.
### Staking Reward Distribution​
The staking `StakingRewardStreams` implementation also inherits from the `BaseRewardStreams` contract. It defines two functions: `stake` and `unstake`, which are used to stake and unstake the rewarded token. This contract has been audited but haven't been yet deployed. If you are interested in using it, please reach out to us so we can deploy it for you.
### Internal Mechanics​
In both modes, each distributor contract defines an `EPOCH_DURATION` constant, which is the duration of a single epoch. This duration cannot be less than 1 week and more than 10 weeks. The currently deployed `TrackingRewardStreams` instance used by the EVK vaults has an epoch duration of 2 weeks.
When registering a new reward stream for the `rewarded` token, one must specify the `startEpoch` number when the new stream will come into effect. To protect users from obvious mistakes, the distributor contract enforces a soft requirement that ensures the `startEpoch` is not more than 5 epochs into the future. Moreover, one must specify the `rewardAmounts` array, which instructs the contract how much `reward` one wants to distribute in each epoch starting from `startEpoch`. The `rewardAmounts` array must have a length of at most 25 for one function call.
If rewarded epochs of multiple reward streams overlap, the amounts will be combined and the effective distribution will be the sum of the amounts in the overlapping epochs.
## Permissionless Reward​
Unlike other permissioned distributors based on the billion-dollar algorithm, Reward Streams distributors do not have an owner or admin meaning that none of the assets can be directly recovered from them. This property is required in order for the system to work in a permissionless manner, allowing anyone to transfer rewards token to a distributor and register a new reward stream. The drawback of this approach is that reward tokens may get lost if nobody earns them at the given moment (i.e. nobody stakes required assets or nobody enabled earning those rewards). In order to prevent reward tokens from being lost when nobody earns them at the moment, the rewards get virtually accrued by `address(0)` and, in exchange for updating given distribution data, are claimable by anyone with use of `updateReward` function.
  * Reward Streams Mechanism
    * Tracking Reward Distribution
    * Staking Reward Distribution
    * Internal Mechanics
  * Permissionless Reward




---

## https://docs.euler.finance/developers/rewardStreams/knownLimitations

Skip to main content
  1. **Epoch duration may not be shorter than 1 week and longer than 10 weeks** : This limitation is in place to ensure the stability and efficiency of the distribution system. The longer the epoch, the more gas efficient the distribution is.
  2. **Registered reward stream can start at most 5 epochs ahead and can last for a maximum of 25 epochs** : This limitation ensures that user inputs are reasonable and helps protect them from making obvious mistakes.
  3. **A user may have at most 5 rewards enabled at a time for a given rewarded token** : This limitation is in place to prevent users from enabling an excessive number of rewards, which could lead to increased gas costs and potential system instability.
  4. **During its lifetime, a distributor may distribute at most`type(uint160).max / 2e19` units of a reward token per rewarded token**: This limitation is in place not to allow accumulator overflow.
  5. **Not all rewarded-reward token pairs may be compatible with the distributor** : This limitation may occur due to unfortunate rounding errors during internal calculations, which can result in registered rewards being irrevocably lost. To avoid this, one must ensure that the following condition, based on an empirical formula, holds true:


`6e6 * block_time_sec * expected_apr_percent * 10**reward_token_decimals * price_of_rewarded_token / 10**rewarded_token_decimals / price_of_reward_token > 1`
For example, for the SHIB-USDC rewarded-reward pair, the above condition will not be met, even with an unusually high assumed APR of 1000%: `block_time_sec = 12` `expected_apr_percent = 1000` `rewarded_token_decimals = 18` `reward_token_decimals = 6` `price_of_rewarded_token = 0.00002` `price_of_reward_token = 1`
`6e6 * 12 * 1000 * 10**6 * 0.00002 / 10**18 / 1` is less than `1`.
  1. **If nobody earns rewards at the moment (i.e. nobody staked/deposited yet), they're being virtually accrued by address(0) and may be claimed by anyone** : This feature is designed to prevent reward tokens from being lost when nobody earns them at the moment. However, it also means that unclaimed rewards could potentially be claimed by anyone.
  2. **If nobody earns rewards at the moment, despite being virtually accrued by address(0) and claimable by anyone, they might still get lost due to rounding** : This limitation may occur due to unfortunate rounding errors during internal calculations, which can result in registered rewards being irrevocably lost. To ensure that the value lost due to rounding is not significant, one must ensure that 1 wei of the reward token multiplied by epoch duration has negligible value.


For example, if the epoch duration is 2 weeks (which corresponds to ~1.2e6 seconds) and the reward token is WBTC, in one rounding, up to ~1.2e6 WBTC may be lost. At the current BTC price, this value corresponds to ~$700, which is a significant value to lose for just one update of the reward stream. Hence, one must either avoid adding rewards that have a significant value of 1 wei or make sure that someone earns rewards at all times.
  1. **Distributor contracts do not have an owner or admin meaning that none of the assets can be directly recovered from them** : This feature is required for the system to work in a permissionless manner. However, it also means that if a mistake is made in the distribution of rewards, the assets cannot be directly recovered from the distributor contracts.
  2. **Distributor contracts do not support rebasing and fee-on-transfer tokens** : This limitation is in place due to internal accounting system limitations. Neither reward nor rewarded tokens may be rebasing or fee-on-transfer tokens.
  3. **Precision loss may lead to the portion of rewards being lost to the distributor** : Precision loss is inherent to calculations in Solidity due to its use of fixed-point arithmetic. In some configurations of the distributor and streams, depending on the accumulator update frequency, a dust portion of the rewards registered might get irrevocably lost to the distributor. However, the amount lost should be negligible as long as the condition from 5. is met.
  4. **Permissionless nature of the distributor may lead to DOS for popular reward-rewarded token pairs** : The distributor allows anyone to incentivize any token with any reward. A bad actor may grief the party willing to legitimately incentivize a given reward-rewarded token pair by registering a tiny reward stream long before the party decides to register the reward stream themselves. Such a reward stream, if not updated frequently, may lead to a situation where the legitimate party is forced to update it themselves since the time the bad actor set up their stream. This may be costly in terms of gas.




---

## https://docs.euler.finance/developers/swaps/swapsOverview

Skip to main content
Token swaps are essential within a lending platform for three main reasons: building leverage, rebalancing positions, and selling collateral during liquidations. Traditionally, to build leverage, users would either loop manually (borrow, swap on an external DEX, deposit, repeat) or use external flash loans. Both methods are suboptimal in terms of gas costs and user experience. To address these shortcomings, Euler integrates swapping directly into the system.
Creating or closing leveraged positions requires swapping between collateral and borrowed assets. When a multiply position is created, borrowed assets are swapped for collateral assets and deposited into the collateral vault. Thanks to deferred liquidity checks, this can happen in a single transaction, achieving the same effect as traditional looping. To close a leveraged position, the collateral asset is withdrawn from the collateral vault, swapped for the debt asset, and used to repay the debt in the liability vault—all within a single transaction.
The trade itself is executed on an external DEX. Users do not need to withdraw assets to their wallets or send separate transactions. Instead, within a single EVC batch, the sold assets are withdrawn to a periphery contract, which executes the trade on the DEX. The proceeds are then deposited back into the selected vault or used to repay the debt. To ensure the best possible trade execution, multiple swap aggregators like 1Inch, LI.FI, and Paraswap are queried by an off-chain meta-aggregator, which selects the best quote and passes it to the swapping contract. The periphery contracts then deposit the acquired assets back for the user or use them to repay the user's debt.
The meta-aggregator is available as an open-source API. Given the trade parameters, it generates complete transaction payloads that can be used directly in an EVC batch.
To find out more about the swapping infrastructure, please see:
  * Swapping periphery contracts
  * Swaps meta-aggregator API




---

## https://docs.euler.finance/FAQ

Skip to main content


---

## https://docs.euler.finance/Glossary

Skip to main content
Term| Definition  
---|---  
**EVC**|  Ethereum Vault Connector  
**EVK**|  Euler Vault Kit  
**EPO**|  Euler Price Oracle  
**Health**|  A number that shows the risk of liquidation due to price changes. If it drops below 1, the account can be liquidated. Higher health means lower risk of liquidation.  
**TTL**|  Time to liquidation. How long it would take for your account to be liquidated if prices stayed the same, but you kept earning or paying interest at the current rates.


---

## https://docs.euler.finance/governance/

Skip to main content


---

## https://docs.euler.finance/governance/EUL

Skip to main content
On this page
EUL is an ERC20 token that acts as the native governance token of the Euler protocol. EUL tokens represent voting power to effect change over the Euler protocol code or the Euler DAO treasury.
## Utility in Fee Flow​
Fees collected from Euler vaults are periodically auctioned through Fee Flow auctions. These auctions use EUL as the bidding currency, ensuring that protocol-generated fees are consistently converted into EUL. The accumulated EUL currently returns to the Euler DAO treasury, but the DAO could choose to burn it, distribute it as incentives for EUL stakers or protocol users, or allocate it in any other way it deems appropriate.
## Token distribution​
The total supply of EUL is 27,182,818 (in homage to Euler’s number, e). Below is the allocation breakdown as of 31/01/25, with links to governance proposals reflecting historical changes.
### Euler DAO​
Around 34% of EUL tokens have been allocated to the Euler DAO, protocol users, or used to fund various ecosystem growth initiatives. Holders of EUL tokens can vote on how treasury tokens are used. Among this group:
  * ~1% (271,828 EUL) was distributed to users on Euler during its soft launch in 2021.
  * ~0.18% (48,100 EUL) was deployed to Uniswap v3 as protocol-owned liquidity following a governance proposal on 22/02/24.
  * ~22.9% (6,236,107 EUL) remain in the Euler DAO treasury, unlocked.
  * ~6.3% (1,712,517 EUL) was distributed to protocol users as rewards during the period 2021 to 2025.


info
**Important note**. Token numbers for the treasury and protocol users change continuously as EUL is distributed as rEUL rewards to users following a governance proposal on 04/11/24. Numbers shown or only accurate as of 31/01/25.
### Euler Foundation​
Around 3.7% of EUL tokens have been allocated to the Euler Foundation, a legal entity representing the interests of the Euler DAO. These tokens have largely been used to facilitate ecosystem growth via provision of protocol-owned liquidity:
  * ~0.018% (5,000) EUL was allocated to the Euler Foundation as an operating budget, following a governance proposal on 15/12/23.
  * ~3.7% (1,000,000 EUL) was allocated to the Euler Foundation to enable them to facilitate ecosystem initiatives, following a governance proposal on 18/05/24. Note that: 
    * A total of 906,200 EUL was deployed by the Euler Foundation as additional protocol-owned liquidity to Balancer v2, Aera, and Arrakis.
    * A remaining 80,598 EUL is held by the Euler Foundation multisig wallet.


### Strategic partners​
Around 39.5% of EUL tokens have been allocated to various cohorts of strategic growth partners, who helped provide support for the development of the Euler protocol in various ways. All of these tokens are fully unlocked. Among these:
  * ~4% (1,087,313 EUL) were given to Encode, an early project incubator.
  * ~10% (2,718,282 EUL) were given to Cohort A growth partners, including Lemniscap, CMT Digital, Launchub, and others.
  * ~15.85% (7,026,759 EUL) were given to Cohort B growth partners, including Paradigm, a variety of industry angel investors, and others.
  * ~9.67% (2,628,170 EUL) were given to Cohort C growth partners, including Haun Ventures, Coinbase Ventures, Uniswap Labs Ventures, Jane Street, and others.


### Euler Labs​
Around 26.5% of EUL tokens have been allocated to project founders and other contributors to the development of the protocol via their association with Euler Labs:
  * ~26.5% (2,864,001 EUL) to employees, advisors and consultants of Euler Labs. Note that: 
    * Founder vesting linear unlock schedule starting on 01/01/2022.
    * Non-founder vesting is specific to individuals, but typically follows a non-linear 48 month schedule.
    * Figure shown here includes an additional 1.6m tokens allocated in a governance proposal on 07/03/24.


## Reward EUL (rEUL)​
Reward EUL (rEUL) is a locked form of EUL to incentivize early adopters of the v2 version of the protocol. Users of Euler receive rEUL rewards by participating in supported markets, with both supply and borrow activities eligible for rewards. The rEUL token converts 1:1 into EUL over six months, following a non-linear unlock schedule:
  * 20% unlocks immediately.
  * 80% unlocks linearly over six months.
  * Users can redeem unlocked EUL anytime, but locked EUL is forfeited and burned if not fully vested.


See the rEUL Rewards Governance Proposal for more details.
## Multichain support​
Euler uses LayerZero's Omnichain Fungible Token (OFT) standard for bridging EUL tokens across networks.
The implementation relies on a dual-hub model with Ethereum mainnet and Base as the primary hubs for EUL transfers. Mainnet uses a lock-based OFT adapter, while Base and other networks use a MintBurnOFTAdapter. This structure balances security, liquidity, and cost efficiency, ensuring seamless cross-chain EUL transfers while simplifying infrastructure management. Learn more in the LayerZero Bridge Governance Proposal.
### Addresses​
All official addresses can be found in the Euler Interfaces GitHub Repository, where they are grouped by network ID. They are also provided for convenience here below.
#### Euler (EUL)​
The addresses of the main Euler governance token, EUL:
  * Ethereum 0xd9Fcd98c322942075A5C3860693e9f4f03AAE07b
  * Polygon: 0x1323a02946877e0F0c1CA99468f4429Cc0F0954c
  * Base: 0xa153Ad732F831a79b5575Fa02e793EC4E99181b0
  * Sonic: 0x8e15C8D399e86d4FD7B427D42f06c60cDD9397e7
  * Swellchain: 0x80ccFBec4b8c82265abdc226Ad3Df84C0726E7A3
  * Arbitrum One: 0x462cD9E0247b2e63831c3189aE738E5E9a5a4b64
  * Ink: 0xB90e23CeF93CA91c1526aAF9742A13A0946E9de4
  * BOB: 0xDe1763aFA5eB658CfFFfD16835AfeB47e7aC0B8D


#### Reward EUL (rEUL)​
The addresses of the locked version of the Euler governance token, rEUL:
  * Ethereum: 0xf3e621395fc714B90dA337AA9108771597b4E696
  * Polygon: 0xbfB6318123dA1682B8bD963846C1e9608F5F3Cda
  * Base: 0xE08e1f00D388E201e48842E53fA96195568e6813
  * Sonic: 0x09E6cab47B7199b9d3839A2C40654f246d518a80
  * Swellchain: 0x021694af083d67950Ac994E63e0a70C30D913836
  * Arbitrum One: 0xFA31599a4928c2d57C0dd77DFCA5DA1E94E6D2D2
  * Ink: 0x47296EC1Ec5143640653169D1a6c8C2C387E41A6
  * BOB: 0x9f395F610Af9ffC98693A0769190446180dc7192


#### Burned rEUL​
Early unlockers of rEUL send EUL to a burn address, taking them out of circulation. The addresses of burned EUL are:
  * Ethereum: 0x000000000000000000000000000000000000dead
  * Base: 0x000000000000000000000000000000000000dead


## Protocol-owned liquidity​
The Euler DAO maintains protocol-owned liquidity at the following venues:
  * Balancer v2: 217,400 EUL (tx1, tx2)
  * Aera: 400,000 EUL (tx1, tx2)
  * Arrakis: 288,800 EUL (tx)
  * Uniswap v3: 48,100 EUL (tx1, tx2)


The multisig owning the first three of these LP tokens is controlled by the Euler Foundation and can be viewed on DeBank.
## Links​
More information about EUL can be found on:


  * Utility in Fee Flow
  * Token distribution
    * Euler Foundation
    * Strategic partners
    * Euler Labs
  * Reward EUL (rEUL)
  * Multichain support
  * Protocol-owned liquidity




---

## https://docs.euler.finance/governance/foundation

Skip to main content


---

## https://docs.euler.finance/governance/guides/howToMakeAProposal

Skip to main content


---

## https://docs.euler.finance/governance/guides/howToVote

Skip to main content


---

## https://docs.euler.finance/governance/treasury

Skip to main content
All newly created EUL tokens enter circulation initially via a smart contract called the Euler Treasury. The treasury is managed by EUL token holders through on-chain and off-chain governance procedures and overseen by the Euler Foundation.
The address for the treasury is: 0xcAD001c30E96765aC90307669d578219D4fb1DCe.


---

## https://docs.euler.finance/legal/privacy-policy

Skip to main content
Visit https://app.euler.finance/privacy-policy to read the latest Privacy Policy.


---

## https://docs.euler.finance/legal/risk-disclosures

Skip to main content
Visit https://app.euler.finance/risk-disclosures to read the latest Risk Disclosures.


---

## https://docs.euler.finance/legal/terms-of-service

Skip to main content
Visit https://app.euler.finance/terms to read the latest Terms of Use.


---

## https://docs.euler.finance/lite-paper/

Skip to main content
On this page
By Euler Labs
## Introduction​
Euler is a flexible platform for decentralized lending and borrowing, designed to adapt and grow with the evolving world of DeFi. Euler’s modular design and institutional-grade security empower builders to create and manage custom lending markets in a fully permissionless way, tailored precisely to their needs.
At the product layer, Euler v2 is a system of ERC-4626 vaults built using a custom-built vault development kit, called the EVK, and chained together using the EVC. The vault kit is agnostic about governance, upgradability, oracles, and much else. Different vault classes support different use-cases, giving users freedom through choice and modularity. Euler v2 will launch with several initial classes of vaults built on the EVK. Builders can customise and integrate these as they wish, or design their own vaults with just a few clicks.
**Escrowed collateral** vaults hold deposits that can be used as collateral for taking out loans from other vaults, but do not earn their depositors interest because they do not allow borrowing. They are ungoverned.
**Governed** vaults hold deposits that can both be used as collateral and borrowed, earning depositors additional yield. A DAO, risk manager, or individual manages these vaults, controlling risk, interest rates, loan-to-value, and other risk parameters. They are suited for passive lenders who trust the governor's management.
**Ungoverned** vaults have fixed parameters with no active governor to manage risk, making them suited to lenders who prefer to manage their own risk. They come in two types:
  * **0x** ungoverned vaults have zero exposure to governance through their collaterals
  * **nzx** ungoverned vaults have non-zero exposure to governance because they may accept collateral with governance exposure


**Yield aggregator** vaults are a special class of governed vaults that aggregate passive lender assets that can be directed by the vault governor to flow into any underlying ERC4626 vault, including both ungoverned or governed Euler vaults, but also external vaults like sDAI. The vault governor manages risk/reward by altering flows into underlying vaults with different properties.
### Synthetic assets​
The modular architecture of Euler v2 enables not only vanilla lending and borrowing via vaults, but also the creation of collateralized debt positions and synthetic assets. These can benefit from deep collateral liquidity inside Euler, advanced risk management and trading features provided by the EVC, and be bolstered by FeeFlow (see below). As well as synthetic assets already planned for governance by Euler DAO, the architecture of Euler enables the creation of a product class where new synthetic assets can be created in a permissionless fashion. More will be revealed about Euler synthetics in the near future.
### Reward Streams: permissionless rewards without staking​
RewardStreams is an innovative open-source module empowering projects to seamlessly stream rewards to users of new markets in a permissionless manner. This module is a robust and adaptable implementation of the billion-dollar algorithm, enabling the simultaneous distribution of multiple reward tokens.
Unlike traditional methods, users can subscribe to receive their preferred rewards without the need to transfer their vault shares to a staking smart contract. This unique feature allows suppliers to earn rewards while concurrently taking out loans, presenting a dynamic and efficient approach to incentivizing and engaging users.
### Fee Flow: reverse Dutch auctions for fees​
FeeFlow is a new and powerful open-source module that provides the Euler DAO with greater control over fees generated on Euler markets, maximising ecosystem growth. This powerful tool enables the auctioning of fees to accumulate assets such as ETH, stETH, USDC, or potentially even EUL, amplifying the DAO's financial flexibility. Alternatively, these fees can be utilised to acquire DAO-backed synthetic assets, providing organic demand and helping to stabilise the asset. In this scenario, the synthetic asset becomes a valuable instrument within Euler's market ecosystem, creating new and diverse trading opportunities
FeeFlow employs a reverse Dutch auction mechanism, periodically auctioning off fees by systematically reducing the auction price as fees accumulate. In Euler v2, vault creators can set fees, ensuring a passive income stream while sharing a portion with the Euler DAO in a decentralised, efficient, and MEV-resistant manner. This innovative approach enables the DAO to convert fees from various assets into a unified, accumulated token.
### Free Market Liquidations​
Euler v2 allows more advanced vault creators to customise and design their own liquidation flow, but the EVK comes equipped with Euler v1’s innovative reverse Dutch auction liquidation flow as standard. This mechanism was popular with borrowers and traders on Euler v1, where bonuses for liquidators on large loans were <0.7%, the cheapest of any DeFi lending protocol. This not only protects borrowers, but also helps protect lenders by maintaining the solvency of pools. Ultimately, the less collateral paid to MEV bots by borrowers, the better.
## Ethereum Vault Connector (EVC)​
The EVC is an interoperability layer and powerful primitive enabling vault creators in the Euler ecosystem to bootstrap new lending products easily by connecting vaults together and recognizing existing deposits in far away vaults as collateral. Whilst a key module inside Euler v2, the EVC is an open-source project supported by Euler Labs that anyone can launch products on. The white paper and development documentation can be found at evc.wtf.
One of the goals of the EVC is to abstract away many of the features common to all credit-based protocols in order to let developers focus on product features tailored to specific types of users. In this way it helps developers build their own lending protocols, stablecoins, yield aggregators, margin trading apps, and much else. In the long run, it is expected to usher in a wave of innovation in lending as it supports lending products backed not only ERC20 tokens, but also irregular asset classes, such as RWAs, NFTs, IOUs, synthetics, and more. Growth of vaults designed to work with the EVC expands the Euler ecosystem and leads to more flexibility for lenders and borrowers alike. This leads to higher yields and powerful network effects over the long term.
### Account Managers for advanced trading and risk management​
For developers building on the EVC, it provides a range of important features for more advanced users of lending protocols out of the box. These include multicall-like batching, flash liquidity for efficient refinancing of loans, simulations, gasless transactions, and more.
One of the powerful features of the EVC is account manager functionality implemented through a smart contract called an operator. Operators can be smart contracts or EOAs that can be delegated responsibility to act on a user’s behalf. Amongst other use cases, this feature can be used to implement advanced trading and risk management strategies, including conditional orders like stop-loss and take-profit, custom liquidation flows, or intent-based systems. Developers can build their own operator smart contracts to implement risk management and position automation strategies and make them available to users as separate products.
The EVC is a multicall contract with a special user authentication layer. It allows any external contracts to be called without needing adaptor contracts. This not only means that all the functionality is accessible to both EOAs and smart contract wallets, but also allows for limitless expansion of the ecosystem through the development of new EVC-compatible products in a permissionless fashion.
Although the EVC allows only one outstanding liability at any given time, it provides each address with 256 virtual addresses (“sub-accounts”), which provide a gas-efficient way for users to isolate and manage risk without the need to maintain multiple separate wallet accounts.
### Collateral direct from a user’s wallet​
An alternative path to creating a collateral-only asset is to create an ERC20Collateral token, which is a simple extension to the ERC20 token standard to enforce compatibility with the EVC. Project making use of this extension can unlock an entirely new wave of composability. Users are no longer required to deposit their tokens into vaults in order to use them as collateral, they can do so directly from their wallet. This helps them retain their governance rights and other token privileges, whilst also helping avoid generating unnecessary taxable events.
Whenever the user's balance decreases (outgoing transfer/token burn), the token contract calls into the EVC to check whether the outstanding loan rules are not violated. With an addition of a simple modifier which routes transfer calls through the EVC, mentioned account status checks can be deferred until the end of a batch of multiple operations, allowing a user to freely use their tokens within a batch as long as their account is solvent at the end. ERC20Collateral also makes the token compatible with EVC sub-accounts system out of the box.
## Use-cases and examples​
### Leverage by chaining LRT/LST/ETH vaults​
  * Create an vault for each major LST allowing all major LRTs as collateral.
  * Create a WETH vault that allows each of those major LSTs and each of the LRTs as collateral.
  * Use-case: LRTs depositors borrow LSTs, and LRTs + LSTs depositors borrow WETH, swap, re-deposit, and leverage their yield. Consequence: this special Euler WETH vault has the highest demand for borrowing of any vault in DeFi.


### Leveraged liquidity provision​
  * Create a WETH vault and a LST vault that allow WETH/LST LP as collateral.
  * Use-case: LP token holders borrow more WETH and LST against their LP tokens and deposit into an AMM to get more LP tokens.
  * Consequence: LP token holders can leverage their LP positions whilst using simple, gas-efficient AMM protocols.


### Impermanent loss hedge​
  * Create a WETH/USDC LP token vault that allows WETH and USDC as collateral.
  * Use-case: WETH and USDC token holders can borrow LP tokens to hedge or go short.
  * Consequence: LP token holders earn additional yield on their tokens, helping compensate against impermanent loss.


### USD carry trades​
  * Create a custom vault pair that allows USDC to borrow USDT, and USDT to borrow USDC on high leverage.
  * Use-case: if USDC APY is higher than USDT APY, users can deposit USDC, borrow USDT, swap to USDC, and re-deposit to carry out a carry trade.
  * Consequence: users can hedge exposure to stablecoin depeg risk, carry out interest rate arbitrage, and profit from carry trades.


### Margin-trading real-world assets​
  * Create a vault for USDC allowing a high-yielding RWAs as collateral, using hooks to enable secondary-transfer restrictions to be observed.
  * Use-case: RWA depositors borrow USDC at lower yield, swap to more RWA, and re-deposit, looping to go long.
  * Consequence: Margin trading on real-world assets as RWA depositors can leverage their yield and earn the interest rate spread on leverage


## Long-term picture​
The ability to lend and borrow digital assets is the foundation on which DeFi is built. Lending protocols are typically composed with decentralised exchanges (DEXs) in order to hedge risk and construct leveraged positions. In this way, borrowers pay interest to lenders, forming the foundation for capital markets in DeFi. Whilst lenders today have many options from which to earn sustainable and passive forms of yield, the trading experience for borrowers and traders remains remarkably poor.
Monolithic lending protocols restrict borrowing with limited asset selections and conservative, one-size-fits-all loan-to-value (LTV) requirements, and then punish traders with heavy fines when they face liquidation. Meanwhile, isolated lending markets offer more flexibility, but often fragment liquidity and increase net costs for traders by disallowing rehypothecation and therefore extra yield on collateral. Moreover, in many cases traders are forced to navigate multiple protocols, governance systems, and user interfaces, paying leveraged fees to each along the way. Together, these market constraints and inefficiencies mean that many traders end up turning to CeFi platforms and relying on perpetual futures markets to put on trades, rather than using decentralised spot markets. This means lower yields for DeFi lenders and, consequently, lower liquidity in less capital efficiency in DeFi across the board.
Euler v2 is a modular lending platform that aims to fix these problems and become the primary liquidity layer for DeFi. Monolithic lending protocols like Aave v3 help foster greater capital efficiency because they pool collateral used for different purposes together and enable rehypothecation. However, they only allow new collateral types to be added under restrictive economic conditions and typically only via governance actions. Isolated lending protocols like Compound v3 or Morpho Blue tend to allow greater flexibility in collateral use, but tend to fragment collateral and prevent rehypothecation, leading to lower capital efficiency.
Euler’s modular architecture helps to solve the liquidity fragmentation problem associated with isolated pools by allowing permissionless creation of vaults that can use any other vault in the broader ecosystem as collateral. This ability to connect together different types of vaults from different product lines via the EVC provides unparalleled flexibility and modularity for lenders, borrowers, builders, traders, and more.
Thanks to the modular design of the system, this can all be achieved without compromising on security or risk management. Vault-chaining via the EVC promises to enable new yield opportunities available nowhere else in DeFi today. With time, whole new product lines can be innovated and brought into the ecosystem helping to power vast network effects. Real-world assets, non-fungible tokens, IOUs for un-collateralised lending, peer-to-peer lending, oracle-free lending, and much more, are all possible directions for the growth of the ecosystem. With this design, together with other developments yet to be announced, Euler aims to become a global liquidity layer and one-stop shop for lending, borrowing, and trading on EVM-based networks.
## Acknowledgements​
With special thanks to Certora, Alberto Cuesta Cañada, Christoph Michel, and StErMi for helpful feedback on some of the mechanisms described herein.
  * Introduction
    * Synthetic assets
    * Reward Streams: permissionless rewards without staking
    * Fee Flow: reverse Dutch auctions for fees
    * Free Market Liquidations
  * Ethereum Vault Connector (EVC)
    * Account Managers for advanced trading and risk management
    * Collateral direct from a user’s wallet
  * Use-cases and examples
    * Leverage by chaining LRT/LST/ETH vaults
    * Leveraged liquidity provision
    * Impermanent loss hedge
    * USD carry trades
    * Margin-trading real-world assets
  * Long-term picture
  * Acknowledgements




---

## https://docs.euler.finance/security/active-monitoring

Skip to main content
Leading web3 security firms actively monitor the Euler protocol across all the networks it is deployed to in order to swiftly detect potential threats. Depending on whether or not vaults have the appropriate access controls for pause and upgradability, one of two things will happen upon detection of a threat.
  * **For vaults with pause and upgrade functionality** : In case of a threat, these vaults can be temporarily halted (read-only mode) and then upgraded to address the issue through a timelock mechanism.
  * **For immutable vaults** : Users will receive immediate notifications upon threat detection and must implement their own emergency withdrawal strategies.




---

## https://docs.euler.finance/security/bug-bounty

Skip to main content
On this page
Euler offers a bug bounty program on Cantina with rewards up to $1 million. The program encourages security researchers to identify vulnerabilities across its modular lending platform, specifically in components like the Euler Vault Kit (EVK), Ethereum Vault Connector (EVC), Euler Price Oracle (EPO) and other key modules.
## Program highlights​
  * **Rewards** : Up to $1M for smart contract vulnerabilities; website-specific bounties up to $25,000.
  * **Scope** : Includes the main contracts of the Euler Vault Kit, Ethereum Vault Connector, Euler Price Oracle, and Reward Streams, among others.
  * **Severity definitions** : Critical, high, and medium severity definitions guide reward levels, based on the vulnerability’s impact and likelihood.
  * **Eligibility requirements** : Only original, previously unreported, non-public vulnerabilities are rewarded; eligibility criteria must be strictly followed.


For details on severity, scope, rewards, and testing guidelines, please refer to the full Cantina documentation.
  * Program highlights




---

## https://docs.euler.finance/security/overview

Skip to main content
Euler v2 stands as one of the most rigorously and expensively audited DeFi projects in the world. Its modular architecture isolates risk, makes code easier to test, analyze, and audit, and helps reduces single points of failure. For a detailed overview of the steps taken to secure Euler, you can explore a dedicated blog post on the topic here.
The protocol codebase has undergone over 40 comprehensive security reviews conducted by more than 16 of the world's leading web3 security firms. In addition to these reviews, the protocol's robustness is reinforced by extensive testing libraries, including bespoke fuzz testing and a formal verification testing suite.
Before its launch, Euler v2 underwent a record-breaking $1.25M Cantina security competition, with only low-severity and informational findings reported. Following its release, the protocol was battle-tested in a $3.5M capture-the-flag (CTF) challenge hosted by Hats Finance.
To maintain ongoing security, Euler v2 features an active bug bounty program on Cantina, offering rewards of up to $1M. Furthermore, the protocol is continuously monitored by leading security firms in collaboration with a specialized security council composed of top web3 security experts. The user interface has been audited to ensure it adheres to best-in-class security practices and is protected by Cloudflare.


---

## https://docs.euler.finance/security/pause-and-upgrade

Skip to main content
On this page
The option to add pause and upgrade functionality to vaults is completely optional at the protocol level, and instead provided by a vault factory governor smart contract. For factories with this feature, the "pause" function temporarily halts (read-only mode) vaults to prevent unauthorized activity in case of an emergency.
To enhance security, the default "canonical" vault factory, integrated with the Euler interface, includes both pause and upgrade capabilities. The same firms carrying out active monitoring act as "pause guardians" for this factory, with the authority to temporarily halt vaults in case of threats. An independent security council of experienced auditors oversees and approves all upgrades to the canonical factory, ensuring their safety and integrity.
# Technical specification
The rules for pause and upgrade of the canonical vault factory are summarised in Figure 1.
**Figure 1.** Summary of canonical vault factory pause and upgradability rules and access controls.
## Pause rules​
Pausing can only be carried out by entities with the `PAUSE_GUARDIAN_ROLE` role. Once the vault factory is in read-only mode, one of two things can happen.
In the event of a pause carried out because of a false positive threat, unpausing can be carried out by entities with the `UNPAUSE_ADMIN_ROLE` role. Unpausing brings the vault factory to the pre-pause state and does not allow for any other changes.
In the event of a pause carried out because of a true positive threat or report of a time sensitive critical vulnerability, Euler DAO, which holds the `PROPOSER_ROLE`, can propose an upgrade to the vault factory code to fix a critical issue.
## Upgrade rules​
An upgrade does not get automatically implemented, but instead gets implemented by the factory governor `DEFAULT_ADMIN`, which is configured as a standard OpenZeppelin TimelockController. The timelock adds additional security by allowing the Euler community a period of time to verify upgrade proposals, and gives entities with the `CANCELLER_ROLE` role the opportunity to veto improper proposals. Improper proposals are those that perform operations not intended by the DAO (because of a DAO multisig compromise, for example).
# Access control roles
## FactoryGovernor​
  * `DEFAULT_ADMIN`: Allowed to set a new implementation to execute proposals that effect code changes on the canonical vault factory. It is held by a TimelockController smart contract. It can also add or remove addresses from the two roles below.
  * `PAUSE_GUARDIAN_ROLE`: Allows entities to put the canonical vault factory into a read-only mode. It is held by two leading web3 security monitoring firms, as well as Euler Labs Ops multisig.
  * `UNPAUSE_ADMIN_ROLE`: The unpause role allows entities to configure the canonical vault factory to exit read-only mode. It is held by Euler Labs Ops multisig.


## Timelock​
  * `PROPOSER_ROLE`: Allowed to make proposals on the timelock to effect operations (code upgrades, role changes) on the canonical vault factory. It is held by the Euler DAO multisig.
  * `CANCELLER_ROLE`: Allowed to veto proposals held in the timelock awaiting execution. This role is held by two parties: 
    1. The **Euler Security Council multisig** , which is a safe-of-safe multisig comprised of the Euler Labs Ops multisigs and the multisigs of two or more leading blockchain security firms. These firms are distinct from those holding the pause role.
    2. The **DAO** , which holds the proposer role and acts as an additional layer of accountability.
  * `EXECUTOR_ROLE`: The executor role is unspecified, which means that any unprivileged address may execute a proposal after the timelock period has elapsed.


  * Pause rules
  * Upgrade rules
  * FactoryGovernor




---

## https://docs.euler.finance/security/security-reviews

Skip to main content
Find details about all of Euler's security reviews in the table below. The protocol has received more than 40 security reviews by 16+ of the world’s leading web3 security firms.
Date| Scope| Security firm| Report URL  
---|---|---|---  
29 October 2024| EVK Periphery - rEUL wrapped locked token| CDSecurity| CDSecurity rEUL ERC20 wrapped locked token Report  
21 October 2024| EVK Periphery - CompatCheck Polygon and Avalanche| yAudit| yAudit Compatibility Polygon and Avalanche Report  
18 October 2024| EVK Periphery - custom liquidator & selector access| yAudit| yAudit EVK Custom Liquidator & Selector Access Control Report  
2 October 2024| EVK Periphery - rEUL| yAudit| yAudit rEUL ERC20 wrapped locked token Report  
1 October 2024| Euler Earn| Spearbit| Spearbit Euler Earn Report  
1 October 2024| Euler Earn| Victor Martinez Fuzzing Suite| TBD  
20 September 2024| EVK Periphery Forta Firewall hooks| yAudit - Forta Firewall Attestation hooks| yAudit - EVK Periphery - Forta Firewall hooks Report  
16 September 2024| Euler Earn| Omniscia| Omniscia Euler Earn Report  
5 September 2024| EPO| yAudit| yAudit EPO Update review Report  
26 August 2024| Euler Earn| yAudit| yAudit Euler Earn Report  
12 August 2024| Web2 infrastructure| Ruptura| PRIVATE  
8 August 2024| EVK Periphery - Vault Pause Guardian| yAudit| yAudit - EVK Periphery - Vault Pause Guardian Report  
8 July 2024| Euler V2| yAudit| yAudit CodeCompetition Fixes review  
17 June 2024| EVK Periphery| yAudit| yAudit EVK Periphery Report  
9 May 2024| Reward Streams| Mixbytes| Mixbytes Reward Streams Report  
1 May 2024| Reward Streams| Hunter Security| Hunter Security Reward Streams Report  
29 April 2024| EPO| ChainSecurity| ChainSecurity Oracle Report  
22 April 2024| EVK| ChainSecurity| ChainSecurity EVK Report  
22 April 2024| Euler V2| Cantina CodeCompetition| Cantina CodeCompetition Report  
8 April 2024| EVC| ChainSecurity| ChainSecurity EVC Report  
8 April 2024| EVK| Spearbit| Spearbit EVK Report  
8 April 2024| EPO| Spearbit| Spearbit EPO Report  
8 April 2024| EVK| OpenZeppelin| OpenZeppelin EVK Report  
8 April 2024| EPO| OpenZeppelin| OpenZeppelin Oracle Report  
1 April 2024| Euler V2| Spearbit VCISO cmichel - EulerV2| N/A  
25 March 2024| Euler V2| yAudit| yAudit Euler V2 Report  
18 March 2024| EVC| Omniscia| Omniscia EVC Report  
18 March 2024| EVK| Omniscia| Omniscia EVK Report  
18 March 2024| EPO| Omniscia| Omniscia EPO Report  
18 March 2024| EVC| OpenZeppelin| OpenZeppelin EVC Report  
7 March 2024| EVK| Certora| Certora EVK Report  
19 February 2024| FeeFlow| Ottersec - FeeFlow| Ottersec FeeFlow Report  
12 February 2024| FeeFlow| Team Omega| Team Omega FeeFlow Report  
6 February 2024| FeeFlow| Zellic| Zellic FeeFlow Report  
5 February 2024| EVK & EVC Playground| Victor Martinez Fuzzing Suite| Fuzzing Suite Report  
5 February 2024| Euler V2| Certora Formal Verification| N/A  
30 January 2024| EVC| Trail of Bits| Trail of Bits EVC Report  
10 January 2024| EVC| Hunter Security| Hunter Security EVC Report  
December 2023| Euler V2 (EVC & EVK)| Alberto Cuesta Cañada| N/A  
4 December 2023| EVC| yAudit  
22 November 2023| EVC| Certora Manual Verification  
1 October 2023| Euler V2| Spearbit VCISO cmichel&StErMi| N/A


---

## https://docs.euler.finance/users/account

Skip to main content
On this page
The Account Page is a dashboard for your lending and borrowing activity on a specific account.
**Link:** app.euler.finance/account/0 for `Account 0`.
Details
## Overview​
The overview on the left displays important account-level metrics. The risk section on the right displays the health score of the account. If your health drops below 1.00 then your account will be eligible for liquidation. To increase your health score you can either supply more collateral or repay a portion of your debt.
## Position​
This position section displays the supply and borrow activity for the account, as well as any accumulated rewards.




---

## https://docs.euler.finance/users/batching

Skip to main content
On this page
The Euler app comes with a transaction queue where you can string together multiple actions and executed them in one transaction. This is made possible thanks to the Ethereum Vault Connector which comes with built-in transaction batching. bar
Batching is even more powerful on Euler because the EVC defers account- and vault status checks until the end of the batch. This means the order of actions does not matter as long as the end state after executing them is consistent with the protocol rules. For example, while ordinarily you would need to
## Transaction Queue​
You can access your transaction queue in the sidebar where you can move, edit, or delete actions.
### Simulation Mode​
In the transaction queue you can enable simulation mode for the transactions. Simulation mode will show the app UI as if the transactions in the queue were executed onchain. This involves actual onchain simulation so any swaps in the transactions will return the actual amount received etc. Simulation mode is a useful tool to verify that your queued actions match your expectations on your Portfolio Page and elsewhere.
  * Transaction Queue
    * Simulation Mode




---

## https://docs.euler.finance/users/borrow-on-euler

Skip to main content
On this page
The Borrow Page shows all opportunities to borrow assets on Euler against your chosen collateral.
**Link:** app.euler.finance/borrow
info
A borrow position consists of 2 actions: supplying assets as collateral and borrowing against them.
## Choosing a Pair​
Unlike the Earn Page which shows a single market on a row, the Borrow Page shows pairs of markets.
### Pair Details​
  * **Collateral** : The asset deposited as collateral.
  * **Debt** : The asset borrowed against the collateral.
  * **Net APY** : The net annual precentage yield you earn with the position. This number is calculated as `Supply APY - Borrow APY`.
  * **LLTV** : The maximum permissible loan-to-value ratio for the pair. If the borrow position exceeds the LLTV, then you will be eligible for liquidation.
  * **Supply APY** : The annual precentage yield you earn for supplying collateral.
  * **Borrow APY** : The annual precentage yield you pay for borrowing. This value may be negative if there are rewards on the market, in which case you are being paid to borrow.
  * **Liquidity** : The available assets to borrow from the Debt market.


info
Each market has an accompanying numeric ID which uniquely identifies the market among all markets for that asset.
info
Each APY value is inclusive of intrinsic yield (e.g. staking yield) and available rewards campaigns. Hover over the value for a breakdown.
Once you select a pair you can click on its row to go to its dedicated pair page. This page lists all parameters of the pair in more details.
## Creating a Borrow Position​
To open the borrow position on your selected pair press the `Borrow` button on the right of the row.
You will be taken to a form where you can enter the amount and complete your transaction.
  * Choosing a Pair
    * Pair Details
  * Creating a Borrow Position




---

## https://docs.euler.finance/users/creating-leverage

Skip to main content
On this page
The Multiply Page shows all opportunities to create leveraged positions on Euler.
**Link:** app.euler.finance/multiply
info
A leveraged position consists of 4 actions: supplying assets as collateral, borrowing against them, swapping that back to the collateral asset and supplying it again as collateral.
## Choosing a Pair​
Similar to the Borrow Page the Multiply Page shows pairs of markets.
### Pair Details​
  * **Long Market** : The asset deposited as collateral.
  * **Short Market** : The asset borrowed against the collateral.
  * **Max ROE** : The net annual precentage yield you can earn with a position at maximum leverage.
  * **Max Multiplier** : The maximum leverage multiplier
  * **Supply APY** : The annual precentage yield you earn for supplying collateral.
  * **Borrow APY** : The annual precentage yield you pay for borrowing. This value may be negative if there are rewards on the market, in which case you are being paid to borrow.
  * **Liquidity** : The available assets to borrow from the Short market.


info
Each market has an accompanying numeric ID which uniquely identifies the market among all markets for that asset.
info
Each APY value is inclusive of intrinsic yield (e.g. staking yield) and available rewards campaigns. Hover over the value for a breakdown.
Once you select a pair you can click on its row to go to its dedicated pair page. This page lists all parameters of the pair in more details.
## Creating a Leveraged Position​
To open the position on your selected pair press the `Multiply` button on the right of the row.
You will be taken to a form where you can enter the amount and complete your transaction.
  * Choosing a Pair
    * Pair Details
  * Creating a Leveraged Position




---

## https://docs.euler.finance/users/earn-on-euler

Skip to main content
On this page
The Earn Page shows all opportunities to earn yield on Euler by lending out your assets.
**Link:** app.euler.finance/earn
info
Earning consists of a single action: supplying tokens to an Euler market. You earn interest on your assets when others borrow your tokens.
## Choosing a Market​
The Earn Page shows a table of all available markets on Euler.
### Market Details​
  * **Market** : The asset accepted by the market to deposit.
  * **Marketplace** : The marketplace is a logical grouping of markets according to purpose. A market may not belong to any marketplace.
  * **Governor** : The entity acting as a governor of the market. The governor may change market parameters. All governors work through a multisig with a mandatory timelock. A market may be `Ungoverned` which means the market parameters are immutable.
  * **Supply APY** : The annual precentage yield you earn for lending assets to the market.
  * **Total Supply** : The total amount and value of assets lent to the market. If this value is small, then the Supply APY of the market may be unstable.
  * **Collateral** : The markets accepted as collateral deposits in this market. This is useful to determine the risk exposure of your deposits. A market may not accept any collateral.
  * **Utilization** : The proportion of lent assets that are borrowed. Supply APY increases with utilization. Supplying into highly utilized markets may be risky.
  * **In Wallet** : The amount of tokens you have available in your wallet that could be deposited into a particular market.


info
Each market has an accompanying numeric ID which uniquely identifies the market among all markets for that asset.
info
Each APY value is inclusive of intrinsic yield (e.g. staking yield) and available rewards campaigns. Hover over the value for a breakdown.
Once you select a market you can click on its row to go to its dedicated market page. This page lists all parameters of the market in more details.
## Supplying into a Market​
To supply assets into your selected market press the `Quick supply` button on the right of the market row.
You will be taken to a form where you can enter the desired amount and complete your transaction.
  * Choosing a Market
    * Market Details
  * Supplying into a Market




---

## https://docs.euler.finance/users/finding-profitable-trades

Skip to main content
On this page
warning
The information presented in Euler Docs is for educational purposes only and **does not constitute financial advice**. It is recommended to conduct your own research before making trades.
Thanks to its advanced features in risk configuration and vault interoperability, Euler v2 is fertile ground for highly capital-efficient marketplaces impossible anywhere else. This makes Euler an attractive venue for 3 market strategies: trading, looping, and farming rewards.
## Pair Trading​
If you believe a certain asset will appreciate in value relative to another, you can exercise your hypothesis as a Multiply position on Euler. The most convenient place to explore such opportunities is the Multiply Page.
While browsing pairs take note of 3 important parameters:
  * **Max Multiplier** : The maximum permitted leverage multiplier you can achieve for the pair.
  * **ROE** : The return-on-equity is the annualized APY paid or received on your notional margin amount. This works similarly to a funding rate in futures or perpetuals exchanges except it is paid continuously while your position is open. Keep in mind that the table shows the ROE at maximum leverage. When setting up a position through `Open Position` you can observe the position ROE as you adjust the parameters.
  * **Liquidity** : This is the available liquidity in the Short Market that determines the maximum position size that can be created. Note that as a market's borrow interest rate increases with utilization so it is best to avoid borrowing all available liquidity.


### Stablecoin Margin​
If you are looking to trade a USD pair, keep in mind that unlike many trading venues, trades on Euler are made against a specific stablecoin e.g. USDC, USDT, USDS. Take care when choosing the stablecoin for your margin positions because each one has different risk profile. Some stablecoins have intrinsic yield which could make some positions less profitable than expected.
## Yield Looping​
Looping or carry trading is a strategy where you long a yield-bearing asset against its non-yield-bearing underlying. These trades are very popular because the assets are highly correlated which reduces (but does not eliminate) price risk. By applying leverage you can achieve high yields on the underlying asset. Examples of such trades are `wstETH/ETH`, `sDAI/DAI`, or `PT-LBTC/WBTC`.
The most convenient place to explore yield looping opportunities is the Multiply Page. Filter the table by choosing your short asset and sort by ROE to discover profitable correlated pairs.
### Risk Considerations​
While yield looping generally carries less liquidation risk there are some important details worth paying attention to.
  1. Check the oracle configured for pricing the yield-bearing asset. Exchange rate oracles are preferred as they do not reflect temporary price volatility.
  2. Some assets classes like LSTs and LRTs may depeg naturally while others like yield-bearing stables do not.
  3. When opening a large trade keep in mind the price impact. If it is large it may take a few days for the position to turn profitable.


## Farming Rewards​
Some markets may have active rewards campagins that are used to incentivize deposits or borrows. Rewarded vaults can be identified by ✨ sparkles next to the APY.
A simple strategy is to take advantage of these rewards by maximizing the Net APY on your position. Optionally this position can be hedged on Euler or elsewhere if the directional exposure is not desired.
  * Pair Trading
    * Stablecoin Margin
  * Yield Looping
    * Risk Considerations
  * Farming Rewards




---

## https://docs.euler.finance/users/managing-positions

Skip to main content
On this page
Every borrow or multiply positions you create carries liquidation risk. While liquidations on Euler are quite forgiving, you will nonetheless incur a capital loss if your position is liquidated.
Accounts with debt are assigned a health score that indicates how close it is to the Liquidation LTV. This health score may fluctuate as the market value of your collateral and debt fluctuates. If your health score falls under 1 then your position is eligible for liquidation.
While you have an outstanding debt you are responsible for monitoring and managing the health of your position. To see your positions at a glance head to the Portfolio Page and take a look at the `Lending & borrowing` section. Click `View details` under your selected account to navigate to the Account Page which shows advanced analytics on your outstanding position.
## Increasing Your Health Score​
Head to the Account Page for the account holding your borrow. You will find quick buttons to top up collateral or repay your debt.
  * Increasing Your Health Score




---

## https://docs.euler.finance/users/portfolio

Skip to main content
On this page
The Portfolio Page is a dashboard for your lending and borrowing activity on Euler.
**Link:** app.euler.finance/portfolio
Details
## Overview​
The overview section displays your Net Asset Value (NAV) and other important wallet-level aggregate metrics.
## Lending & borrowing​
This section shows the lending and borrowing activity in each account. The `View details` button leads to the Account Page for the selected account.
## Rewards​
The rewards table displays accrued token rewards from incentives campaigns and a button to claim them.
## Wallet Tokens​
This section shows wallet holdings eligible for lending on Euler. The `Earn` button leads to the Earn Page for Euler vaults that accept the selected token.
  * Lending & borrowing
  * Wallet Tokens




---

## https://docs.euler.finance/users/spy-mode

Skip to main content
Spy Mode is a hidden advanced feature that lets you view the App through the lens of someone else. To activate spy mode add `?spy=<ADDRESS>` to the end of the URL. Spy Mode is useful to observe other users' positions on Euler.


---

## https://docs.euler.finance/users/troubleshooting

Skip to main content
If you encounter a bug while using the app please follow these steps to troubleshoot it:
  1. Clear local storage and cookies.
  2. Reconnect your wallet.
  3. If your issue persists open a support ticket on Discord with the following information: 
     * Wallet address
     * Errors in Developer console (if any)
     * Screenshot uploaded to an image host
     * Transaction hash (if applicable)




---

## https://docs.euler.finance/vault-builders/deploy-the-oracle-router

Skip to main content
On this page
Once you have planned the vault architecture you are ready to start the deployment process.
The first step is to deploy an Oracle Router and configure it to price all of your vaults (and external collateral vaults) to a common denomination. The Router will be installed in every vault you subsequently deploy to make a coherent pricing configuration.
## Deploying the Oracle Router​
  1. Visit the Vault Manager UI and connect your wallet. 
  2. Navigate to the Oracle Page. 
  3. Press `Deploy` and execute the transaction to deploy the Oracle Router.


## Configuring Oracle Adapters​
  1. Input the Oracle Router address under `Manage Existing Router`. 
  2. Add the chosen Oracle Adapters for your vault assets, including external collateral vaults. 
     * Press `Add Oracle Adapter` at the top.
     * Under `Token 0` input the asset's ERC20 address.
     * Under `Token 1` input the unit of account, either WETH or USD (0x0000000000000000000000000000000000000348).
     * Wait for available adapters to load and select an adapter from the dropdown
     * Press `Add Oracle Adapter` and execute the transaction to complete the configuration.
     * Repeat these steps for every vault asset, including external vaults used as collateral.


## Modifying or Removing Oracle Adapters​
  1. Input the Oracle Router address under `Manage Existing Router`. 
  2. Browse the configured adapters on the right hand side. 
  3. Press `Edit` to change the configuration or `Delete` to remove it.


  * Deploying the Oracle Router
  * Configuring Oracle Adapters
  * Modifying or Removing Oracle Adapters




---

## https://docs.euler.finance/vault-builders/deploy-your-vaults

Skip to main content
Once you have deployed and configured your Oracle Router you are ready to start deploying Euler vaults.
  1. Visit the Vault Manager UI and connect your wallet. 
  2. Navigate to the Vault Page. 
  3. Input the address of the underlying ERC20 asset under `Underlying Asset`.
  4. Input the deployed Oracle Router under `Oracle Router`.
  5. Select the `Unit of Account` used in the Oracle Router.
  6. Press `Create Vault` and execute the transaction to deploy the vault.


Repeat these steps for every vault.


---

## https://docs.euler.finance/vault-builders/howToDeployAnIRM

Skip to main content
  1. Visit the EVK Vault Manager portal


The EVK Vault Manager portal provides easy ways to manage Euler Vault Kit contracts. Choose `Deploy IRM` section to deploy a new IRM.
  1. Fill all attributes


  * `BaseIR`: This is the interest rate applied when the utilization of the lending pool is zero. It represents the minimal interest charged to borrowers when there is little to no demand for borrowing.
  * `KinkIR`: This is the interest rate applied when the utilization rate reaches a specified point (the kink). At the kink, the interest rate changes more sharply to reflect higher demand for the borrowed assets.
  * `MaxIR`: This is the maximum interest rate that can be charged to borrowers. It represents a ceiling that the protocol will not exceed, even if demand for borrowing skyrockets and utilization is very high.
  * `Kink`: The kink represents the utilization threshold where the interest rate model changes. Below the kink, the interest rate increases gradually; above it, the interest rate increases much more sharply.
  * `Interest Fee`: This fee is a percentage of the interest paid by borrowers that is collected by the protocol.


  1. Sign the transaction


Sign the deploy transaction by clicking `CREATE IRM` button, and you are done.


---

## https://docs.euler.finance/vault-builders/howToNameVaults

Skip to main content
GitHub: https://github.com/euler-xyz/euler-labels


---

## https://docs.euler.finance/vault-builders/introduction

Skip to main content
On this page
The Euler Vault Kit allows you to permissionlessly deploy and configure credit vaults. This can be done in two ways, with a cutsom forge script or through our Vault Manager UI at create.euler.finance.
While deployment is permissionless, only select governed vaults show up on the official UI. To learn more, contact the Euler Labs team.
## Prerequisites​
Before you start deploying vaults, make sure you are familiar with the core concepts of Euler v2.
## Steps​
Deploying vaults with the Vault Manager UI happens in several steps.
  1. **Plan your vault architecture.** Select the assets you want to create vaults for and note down any existing vaults in the Euler ecosystem you plan to allow as collateral for borrowing from your vaults. Consider what types of vaults (Escrow, Base, or Managed) you want to create.
  2. **Deploy a pricing system.** Select a unit of account (usually WETH or USD) in which to value collateral and debt within your vaults, and add your preferred oracle types to an oracle router.
  3. **Create your vaults.** For each vault you need to point it toward the pricing system you created in step 2.
  4. **Configure your vaults.** Once your vaults and oracles are deployed, you need to configure LTVs, supply and borrow caps, and other risk-based parameters for your vaults.
  5. **Choose a governance system.** Once you have configured your vaults, you must decide whether to retain or revoke governance (make your vaults immutable).
  6. **Verify your vaults.** Add your vaults to verified vault lists, which will allow them to appear on supporting user-interfaces. Only verified Base and Escrow vaults are shown on euler.finance by default. All other vaults must be approved by the DAO or hosted on a separate website.
  7. **Add rewards to your vault (optional).** Reward depositors in your vaults (or existing vaults) by streaming them token rewards of your choice.


  * Prerequisites




---

## https://docs.euler.finance/vault-builders/vault-architecture

Skip to main content
Before deploying vaults, plan your vault architecture.
  * Select the ERC20 tokens you want to create vaults for.
  * Choose compatible oracles from the Oracle Dashboard or ping us to deploy a custom one
  * Pick the collaterals for every vault. For every collateral relationship have a borrow LTV and liquidation LTV in mind.
  * Pick any existing vaults in the Euler ecosystem that can be used as collateral in your cluster. Used strategically, external collateral vaults can bootstrap borrowing demand.




---

## https://docs.euler.finance/

Skip to main content
Euler is a flexible platform for decentralized lending and borrowing, designed to adapt and grow with the evolving world of DeFi.
For everyday users, Euler makes lending and borrowing simpler, more efficient, and more versatile, while giving them the freedom to explore new opportunities in DeFi.
Behind the scenes, Euler’s modular design and institutional-grade security empower builders to create and manage custom lending markets in a fully permissionless way, tailored precisely to their needs.
For more details, dive into the Lite Paper or join the community Discord server. Please don't hesitate to ask if you cannot find what you are looking for here.


---


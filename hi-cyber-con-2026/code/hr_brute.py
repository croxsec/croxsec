#!/usr/bin/env python3
from web3 import Web3
import itertools
w3=Web3()
def sel(sig): return Web3.keccak(text=sig)[:4].hex()

unknown=['05a523fb','276b7377','37a7b7d8','360dc2c8','398482d8','3ee7a701','40f788d2','4f4ad3a6','a10954fe','a2fb342d','a78695b0','ca38936e','d79a6512','dce0772c','f6487d8c']

words="""owner operator authority market vault reserve token collateral debt credit facility desk notary bank treasury
price value ltv health factor healthFactor ratio collateralization initialReserve reserveAmount minReserve maxReserve cap limit
borrow repay deposit withdraw mint burn redeem claim seize sweep rescue drain recover skim sync flash
init initialize seed configure set setPrice setMarket setVault setAuthority setOwner transferOwnership
pending proposed candidate newOwner nominee
locked lock staked stake shares share balance balances amount amounts
total totalDebt totalBorrowed totalSupply borrowed supplied
liquidation liquidationThreshold threshold penalty bonus discount fee flashFee
position positions loan loans account accounts user users
data info config params state status mode paused enabled
ratio base UNIT WAD RAY PERCENT BPS scale precision
nonce deadline permit digest DOMAIN_SEPARATOR eip712
kill switch emergency shutdown halt frozen
treasury tax revenue share split cut
outstanding due obligation liabilities creditLimit line
index rate interest apr supplyRate borrowRate utilization
k last reserves reserves0 reserves1 price0 price1
oracle feed answer round answeredInRound decimals latestRoundData
pegged peg target band spread deviation
authorized authorizedOperator whitelist blacklisted isAuthorized canCall hasAccess
guardian sentinel watchman auditor controller manager
report reports reporting period epoch cycle window
settle settlement clearing clearinghouse batch auction dutch
wrap unwrap underlying asset pToken cToken aToken yToken
receipt voucher receiptToken claimToken
gauge gaugeWeight weight vote votes voting escrow veNFT
streaming stream vesting vest cliff
proof merkle root verify claimed
refund refundable repayable reclaim
pendingReward rewards rewardRate rewardPerToken earned
flashFeeFlashLoan maxFlashLoan flashLoanFee
onFlashLoan callback receiver
"""

types=["","address","uint256","uint128","uint64","bytes32","bool","address,uint256","uint256,uint256","address,address","uint256,address","address,uint256,uint256","uint256,uint256,uint256","bytes","bytes32,uint256"]
found={}
for w in words.split():
    for t in types:
        sig=w+(f"({t})" if t else "()")
        h=sel(sig)
        if h in unknown:
            found[h]=sig
for h in unknown:
    print(h, "->", found.get(h,"?"))

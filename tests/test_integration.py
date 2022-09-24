from brownie import config, accounts, Lottery, network
from scripts.helpful_scripts import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from scripts.deploy_lottery import (
    deploy_lottery,
    fund_with_link,
)
import pytest
import time


def test_lottery_works():
    if network.show_active in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0

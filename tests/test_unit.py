from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
    get_contract,
)
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    # 1 eth = 2000 usd
    # x eth = 50 usd -> x == 0.025

    expected_value = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()

    assert entrance_fee == expected_value


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account()})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    enter_tx = lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    enter_tx.wait(1)

    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    account = get_account()
    lottery = deploy_lottery()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    fund_with_link(lottery.address)
    end_tx = lottery.endLottery({"from": account})
    end_tx.wait(1)

    assert lottery.lottery_state() == 2


def test_winner_gets_money():
    STATIC_RANDOM_NUMBER = 333

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    account = get_account()
    lottery = deploy_lottery()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})

    initial_account_balance = account.balance()

    fund_with_link(lottery.address)
    end_tx = lottery.endLottery({"from": account})
    request_id = end_tx.events["RequestedRandomness"]["requestId"]

    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RANDOM_NUMBER, lottery.address, {"from": account}
    )
    final_account_balance = account.balance()

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert final_account_balance > initial_account_balance

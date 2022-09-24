from scripts.helpful_scripts import get_account, get_contract, fund_with_link
from brownie import Lottery, config, network


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Lottery is deployed successfully!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    tx = lottery.startLottery({"from": account})
    tx.wait(1)
    print("The Lottery is started!")


def enter_lottery(index=0):  # Account index
    account = get_account(index)
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 10000000
    enter_tx = lottery.enter({"from": account, "value": value})
    enter_tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    fund_tx = fund_with_link(lottery.address)
    fund_tx.wait(1)
    end_tx = lottery.endLottery({"from": account})
    end_tx.wait(1)


# Run deploy, start, enter, end functions in main:
def main():
    deploy_lottery()
    # start_lottery()
    # enter_lottery()
    # end_lottery()

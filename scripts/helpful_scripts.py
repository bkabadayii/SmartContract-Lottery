from brownie import (
    network,
    accounts,
    config,
    MockV3Aggregator,
    Contract,
    VRFCoordinatorMock,
    LinkToken,
)

DECIMALS = 8
STARTING_PRICE = 200000000000

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def deploy_mocks():
    account = get_account()
    print(f"The active network is {network.show_active()}...")
    print("Deploying mocks...")

    # Deploy MockV3Aggregator
    print("Deploying MockV3Aggregator...")
    MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": account})

    # Deploy LinkToken
    print("Deploying LinkToken...")
    link_token = LinkToken.deploy({"from": account})

    # Deploy VRfCoordinatorMock
    print("Deploying VRFCoordinatorMock...")
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})

    print("Mocks deployed!")


def get_contract(contract_name):
    """This function will grab the contract addresses from the brownie config,
    if not defined: it will deploy a mock contract and return it.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:  # Check if a mock is deployed before
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print(f"Funded contract {amount/1000000000000000000} tokens!")
    return tx

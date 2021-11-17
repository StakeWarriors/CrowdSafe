from brownie import Contract, CrowdSafeV2, config, network
from scripts.deploy_crowd_safe import deploy_crowdsafe
from scripts.helpful_scripts import get_account, get_contract


def get_last_deployed():
    admin = get_account()
    contract = get_contract("TransparentUpgradeableProxy")
    proxy_crowdsafe = Contract.from_abi("CrowdSafeV2", contract, CrowdSafeV2.abi)


def main():
    admin = get_account()
    contract = config["networks"][network.show_active()]["TransparentUpgradeableProxy"]
    proxy_crowdsafe = Contract.from_abi("CrowdSafeV2", contract, CrowdSafeV2.abi)
    proxy_crowdsafe.__CrowdSafe_init(1, {"from": admin})
    print(f"admin={admin} proxy_crowdsafe_owner={proxy_crowdsafe.owner()}")
    proxy_crowdsafe.batchSet(
        [2, 21000000000000, 100000, 100, 50, 10, 10], [], [True], {"from": admin}
    )


# def main():
#     admin = get_account()
#     contract = get_contract("TransparentUpgradeableProxy")
#     contract.batchSet(
#         [2, 21000000000000, 100000, 100, 50, 10, 10], [], [True], {"from": admin}
#     )

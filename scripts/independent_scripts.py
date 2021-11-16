from brownie import (
    CrowdSafeV2,
)
from scripts.deploy_crowd_safe import deploy_crowdsafe
from scripts.helpful_scripts import get_account, get_contract


def main():
    admin = get_account()
    contract = get_contract("TransparentUpgradeableProxy")
    contract.batchSet(
        [2, 21000000000000, 100000, 100, 50, 10, 10], [], [True], {"from": admin}
    )

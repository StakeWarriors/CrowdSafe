from brownie import (
    network,
    config,
    accounts,
    TransparentUpgradeableProxy,
    ProxyAdmin,
    CrowdSafe,
)
import eth_utils

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
POLY_BLOCKCHAIN_ENVIRONMENTS = [
    "mumbai_moralis",
    "mumbai_moralis2",
    "polygon-main",
    "polygon-test",
]


def get_address(address):
    return config["networks"][network.show_active()][address]


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
    return accounts.add(config["wallets"]["from_blue_key"])


def is_local():
    return (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    )


def encode_function_data(initializer=None, *args):
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)


def upgrade(
    account,
    proxy,
    new_implementation_address,
    proxy_admin_contract=None,
    initializer=None,
    *args,
):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_implementation_address,
                encode_function_call,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, new_implementation_address, {"from": account}
            )
    else:
        if initializer:
            encode_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeToAndCall(
                new_implementation_address,
                encode_function_call,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgradeTo(
                new_implementation_address, {"from": account}
            )
    return transaction


def print_weblink():
    if not is_local():
        if network.show_active() in POLY_BLOCKCHAIN_ENVIRONMENTS:
            # Running this command without deploying will show most recent deployments
            print(
                f"https://polygonscan.com/address/{TransparentUpgradeableProxy[-1].address}"
            )
            print(f"https://polygonscan.com/address/{ProxyAdmin[-1].address}")
            print(f"https://polygonscan.com/address/{CrowdSafe[-1].address}")
        else:
            # Running this command without deploying will show most recent deployments
            print(
                f"https://{network.show_active()}.etherscan.io/address/{TransparentUpgradeableProxy[-1].address}"
            )
            print(
                f"https://{network.show_active()}.etherscan.io/address/{ProxyAdmin[-1].address}"
            )
            print(
                f"https://{network.show_active()}.etherscan.io/address/{CrowdSafe[-1].address}"
            )

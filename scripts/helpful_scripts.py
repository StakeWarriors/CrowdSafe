from brownie import (
    network,
    config,
    accounts,
    TransparentUpgradeableProxy,
    ProxyAdmin,
    CrowdSafe,
    CrowdSafeV2,
    Contract,
)
import eth_utils

FORKED_LOCAL_ENVIRONMENTS = ["mumbai_moralis", "mumbai_moralis2", "polygon-test"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]
POLY_BLOCKCHAIN_ENVIRONMENTS = [
    "mumbai_moralis",
    "mumbai_moralis2",
    "polygon-test",
    "polygon-main",
]


contract_to_mock = {
    "TransparentUpgradeableProxy": TransparentUpgradeableProxy,
    "ProxyAdmin": ProxyAdmin,
    "CrowdSafe": CrowdSafe,
    "CrowdSafeV2": CrowdSafeV2,
}


def get_address(address):
    return config["networks"][network.show_active()][address]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_red_key"])


def is_dev():
    return (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    )


def deploy_dev_contract(contract):
    account = get_account()
    if contract == "TransparentUpgradeableProxy":
        raise "No Deploy Code Implemented"
    if contract == "ProxyAdmin":
        return ProxyAdmin.deploy({"from": account})
    if contract == "CrowdSafe" or "CrowdSafeV2":
        return contract_to_mock[contract].deploy(
            {"from": account},
            publish_source=config["networks"][network.show_active()].get(
                "verify", False
            ),
        )


def get_contract(contract):
    if not is_dev() and len(config["networks"][network.show_active()][contract]) > 0:
        return Contract.from_explorer(
            config["networks"][network.show_active()][contract]
        )
    elif len(contract_to_mock[contract]) > 0:
        return contract_to_mock[contract][-1]
    else:
        return deploy_dev_contract(contract)


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
    transparentUpgradeableProxyAddr = None
    proxyAdminAddr = None
    crowdSafeAddr = None

    if len(TransparentUpgradeableProxy) > 0:
        transparentUpgradeableProxyAddr = TransparentUpgradeableProxy[-1].address
    else:
        transparentUpgradeableProxyAddr = config["networks"][network.show_active()][
            "TransparentUpgradeableProxy"
        ]
    if len(ProxyAdmin) > 0:
        proxyAdminAddr = ProxyAdmin[-1].address
    else:
        proxyAdminAddr = config["networks"][network.show_active()]["ProxyAdmin"]
    if len(CrowdSafe) > 0:
        crowdSafeAddr = CrowdSafe[-1].address
    else:
        crowdSafeAddr = config["networks"][network.show_active()]["CrowdSafeV2"]

    if not is_dev():
        if network.show_active() in FORKED_LOCAL_ENVIRONMENTS:
            # Running this command without deploying will show most recent deployments
            print(f"https://polygonscan.com/address/{transparentUpgradeableProxyAddr}")
            print(f"https://polygonscan.com/address/{proxyAdminAddr}")
            print(f"https://polygonscan.com/address/{crowdSafeAddr}")
    else:
        # Running this command without deploying will show most recent deployments
        print(
            f"https://mumbai.polygonscan.com/address/{transparentUpgradeableProxyAddr}"
        )
        print(f"https://mumbai.polygonscan.com/address/{proxyAdminAddr}")
        print(f"https://mumbai.polygonscan.com/address/{crowdSafeAddr}")

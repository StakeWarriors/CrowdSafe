from brownie import (
    network,
    CrowdSafe,
    CrowdSafeMock,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    config,
)
from scripts.helpful_scripts import get_account, encode_function_data, print_weblink


def deploy_crowdsafe(contract):
    account = get_account()
    crowdsafe = contract.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    return crowdsafe


def deploy_proxy(contract):
    account = get_account()
    proxy_admin = ProxyAdmin.deploy({"from": account})
    crowdsafe_encode_initializer_function = encode_function_data(
        contract.__CrowdSafe_init, contract.version() + 1
    )

    proxy = TransparentUpgradeableProxy.deploy(
        contract.address,
        proxy_admin.address,
        crowdsafe_encode_initializer_function,
        {"from": account, "gas_limit": 1200000},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    proxy_crowdsafe = Contract.from_abi("CrowdSafe", proxy.address, CrowdSafe.abi)
    return proxy, proxy_admin, proxy_crowdsafe


def deploy_contract():
    contract = deploy_crowdsafe(CrowdSafe)
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_proxy(contract)
    print_weblink()
    return proxy, proxy_admin, proxy_crowdsafe


def main():
    deploy_contract()

from brownie import (
    network,
    CrowdSafe,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    config,
)
from scripts.helpful_scripts import get_account, encode_function_data, upgrade


def deploy_crowdsafe(contract):
    account = get_account()
    print(f"Deploying to {network.show_active()}")
    crowdsafe = contract.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    return crowdsafe


def deploy_proxy(contract):
    account = get_account()
    proxy_admin = ProxyAdmin.deploy({"from": account})
    # initializer = contract.store, 1
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
    print(f"Proxy deployed to {proxy}")
    proxy_crowdsafe = Contract.from_abi("CrowdSafe", proxy.address, CrowdSafe.abi)
    print(f"Retrieved {proxy_crowdsafe.version()}")
    return proxy, proxy_admin, proxy_crowdsafe


def main():
    account = get_account()
    contract = deploy_crowdsafe(CrowdSafe)
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_proxy(contract)
    contractV2 = deploy_crowdsafe(CrowdSafe)
    upgrade_transaction = upgrade(
        account, proxy, contractV2.address, proxy_admin_contract=proxy_admin
    )
    upgrade_transaction.wait(1)

    print("Proxy has been Updated")
    proxy_crowdsafe = Contract.from_abi("CrowdSafe", proxy.address, CrowdSafe.abi)
    print(f"CrowdSafe before Increment {proxy_crowdsafe.version()}")
    proxy_crowdsafe.increment({"from": account})
    print(f"CrowdSafe after Increment {proxy_crowdsafe.version()}")

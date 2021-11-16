from brownie import (
    network,
    CrowdSafeV2,
    ProxyAdmin,
    Contract,
    TransparentUpgradeableProxy,
    config,
)
from scripts.helpful_scripts import (
    get_account,
    encode_function_data,
    get_contract,
    print_weblink,
)


def deploy_crowdsafe(contract):
    account = get_account()
    crowdsafe = contract.deploy(
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    return crowdsafe


def do_upgrade(contract, proxy, proxy_admin):
    account = get_account()
    proxy_crowdsafe = Contract.from_abi("CrowdSafeV2", proxy.address, CrowdSafeV2.abi)
    proxy_admin.upgrade(proxy.address, contract.address, {"from": account})
    return proxy, proxy_admin, proxy_crowdsafe


def migrate_contract():
    contract = deploy_crowdsafe(CrowdSafeV2)
    proxy = get_contract("TransparentUpgradeableProxy")
    proxy_admin = get_contract("ProxyAdmin")
    (proxy, proxy_admin, proxy_crowdsafe) = do_upgrade(contract, proxy, proxy_admin)

    print_weblink()
    return proxy, proxy_admin, proxy_crowdsafe


def fetch_last():
    # (proxy, proxy_admin, proxy_crowdsafe)=migrate_contract()
    proxy = get_contract("TransparentUpgradeableProxy")
    proxy_admin = get_contract("ProxyAdmin")
    proxy_crowdsafe = get_contract("CrowdSafeV2")
    print_weblink()
    return proxy, proxy_admin, proxy_crowdsafe


def test():
    transparentupgradeableproxy = TransparentUpgradeableProxy[-1]
    proxyadmin = ProxyAdmin[-1]
    crowdsafev2 = CrowdSafeV2[-1]

    print(f"{transparentupgradeableproxy} {proxyadmin} {crowdsafev2}")


def main():
    (proxy, proxy_admin, proxy_crowdsafe) = fetch_last()
    (proxy, proxy_admin, proxy_crowdsafe) = do_upgrade(
        proxy_crowdsafe, proxy, proxy_admin
    )
    print(f"{proxy} {proxy_admin} {proxy_crowdsafe}")

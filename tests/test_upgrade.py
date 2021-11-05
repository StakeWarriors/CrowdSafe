import pytest
from brownie import (
    CrowdSafe,
    CrowdSafeMock,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    exceptions,
)

from scripts.deploy_crowd_safe import deploy_contract, deploy_crowdsafe, deploy_proxy
from scripts.helpful_scripts import get_account, encode_function_data


def test_proxy_upgrade():
    account = get_account()
    crowdsafe = CrowdSafe.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})
    crowdsafe_encode_initializer_function = encode_function_data(
        crowdsafe.__CrowdSafe_init, crowdsafe.version() + 1
    )
    proxy = TransparentUpgradeableProxy.deploy(
        crowdsafe.address,
        proxy_admin.address,
        crowdsafe_encode_initializer_function,
        {"from": account, "gas_limit": 2100000},
    )

    crowdsafe_mock = CrowdSafeMock.deploy({"from": account})
    proxy_crowdsafe = Contract.from_abi(
        "CrowdSafeMock", proxy.address, CrowdSafeMock.abi
    )
    # Act
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_crowdsafe.setVersion(30, {"from": account})

    proxy_admin.upgrade(proxy.address, crowdsafe_mock.address, {"from": account})

    assert proxy_crowdsafe.version() == 1
    proxy_crowdsafe.setVersion(30, {"from": account})
    assert proxy_crowdsafe.version() == 30


FAKE_ADDRESS = "0x0000000000000000000000000000000000000001"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_proxy_upgrade_and_retain_data():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_contract()

    # @see @link{test_normal_user_can_report_scam}
    assert proxy_crowdsafe.highestScamThreatLevel() == 0
    assert proxy_crowdsafe.highestScamThreatAwareness() == 0
    assert proxy_crowdsafe.highestScamThreatAddress() == ZERO_ADDRESS
    account2 = get_account(index=1)
    proxy_crowdsafe.ReportScam(
        FAKE_ADDRESS, {"from": account2, "amount": 100000000000000}
    )
    assert proxy_crowdsafe.highestScamThreatLevel() == 5
    assert proxy_crowdsafe.highestScamThreatAwareness() == 1
    assert proxy_crowdsafe.highestScamThreatAddress() == FAKE_ADDRESS

    account = get_account()
    contract = deploy_crowdsafe(CrowdSafeMock)
    proxy_admin.upgrade(proxy.address, contract.address, {"from": account})

    assert proxy_crowdsafe.highestScamThreatLevel() == 5
    assert proxy_crowdsafe.highestScamThreatAwareness() == 1
    assert proxy_crowdsafe.highestScamThreatAddress() == FAKE_ADDRESS

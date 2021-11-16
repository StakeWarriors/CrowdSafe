import pytest
from brownie import exceptions,Wei
from scripts.helpful_scripts import get_account
from tests.migrate_helper import deploy_and_migrate
from brownie.test import given
from hypothesis import  strategies as st
st_buy_amount_eth = st.integers(min_value=int(Wei("1 gwei")), max_value=int(Wei("10 ether")))

FAKE_ADDRESS = "0x0000000000000000000000000000000000000001"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"



@pytest.fixture(scope="module", autouse=True)
def setup(module_isolation):
    pass

def test_normal_user_can_report_scam():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
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
    assert proxy_crowdsafe.getScamReportersLength() == 1
    assert proxy_crowdsafe.getReportedScamsLength() == 1
    assert proxy_crowdsafe.scamReporters(0) == get_account(index=1)


def test_normal_user_can_report_safe():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
    assert proxy_crowdsafe.safeLevel(proxy_crowdsafe.address) == 48690474535
    assert proxy_crowdsafe.safeAwareness(proxy_crowdsafe.address) == 1

    for i in range(6):
        proxy_crowdsafe.ReportSafe(
            FAKE_ADDRESS,                                
            {"from": get_account(index=i + 1), "amount": 15000000000000000000},
        )
    assert proxy_crowdsafe.highestSafetyLevel() == 4285716
    assert proxy_crowdsafe.highestSafetyAwareness() == 6
    assert proxy_crowdsafe.highestSafetyAddress() == FAKE_ADDRESS
    assert proxy_crowdsafe.getSafeReportersLength() == 7
    assert proxy_crowdsafe.getReportedSafeLength() == 2
    assert proxy_crowdsafe.safeReporters(1) == get_account(index=1)


def test_normal_user_cant_report_self():
    selv = get_account(index=1)
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_crowdsafe.ReportScam(selv, {"from": selv, "amount": 100})
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_crowdsafe.ReportSafe(selv, {"from": selv, "amount": 100})


def test_master_user_cant_report_scam():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_crowdsafe.ReportScam(FAKE_ADDRESS, {"from": get_account(), "amount": 100})


def test_master_user_cant_report_safe():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_crowdsafe.ReportSafe(FAKE_ADDRESS, {"from": get_account(), "amount": 100})


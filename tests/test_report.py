import pytest
from brownie import exceptions
from scripts.helpful_scripts import get_account
from scripts.deploy_crowd_safe import deploy_contract

FAKE_ADDRESS = "0x0000000000000000000000000000000000000001"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


def test_normal_user_can_report_scam():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_contract()
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
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_contract()
    assert proxy_crowdsafe.safeLevel(proxy_crowdsafe.address) == 48690474535
    assert proxy_crowdsafe.safeAwareness(proxy_crowdsafe.address) == 1

    for i in range(6):
        proxy_crowdsafe.ReportSafe(
            FAKE_ADDRESS,
            {"from": get_account(index=i + 1), "amount": 85_0_00000000_0_00000000},
        )
    assert proxy_crowdsafe.highestSafetyLevel() == 24285720
    assert proxy_crowdsafe.highestSafetyAwareness() == 6
    assert proxy_crowdsafe.highestSafetyAddress() == FAKE_ADDRESS
    assert proxy_crowdsafe.getSafeReportersLength() == 7
    assert proxy_crowdsafe.getReportedSafeLength() == 2
    assert proxy_crowdsafe.safeReporters(1) == get_account(index=1)


def test_normal_user_cant_report_self():
    selv = get_account(index=1)
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_contract()
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_crowdsafe.ReportScam(selv, {"from": selv, "amount": 100})
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_crowdsafe.ReportSafe(selv, {"from": selv, "amount": 100})


def test_master_user_cant_report_scam():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_contract()
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_crowdsafe.ReportScam(FAKE_ADDRESS, {"from": get_account(), "amount": 100})


def test_master_user_cant_report_safe():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_contract()
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_crowdsafe.ReportSafe(FAKE_ADDRESS, {"from": get_account(), "amount": 100})


def test_report_scam_user_by_amount():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_contract()
    account_to_ban = get_account(index=2)

    # Don't Like Bot Account
    proxy_crowdsafe.ReportScam(
        account_to_ban,
        {"from": get_account(index=1), "amount": 10_0_00000000_0_00000000},
    )

    # Bot Account can still vote
    proxy_crowdsafe.ReportSafe(FAKE_ADDRESS, {"from": account_to_ban, "amount": 100})

    assert proxy_crowdsafe.scamThreatLevel(account_to_ban) == 476191
    proxy_crowdsafe.ReportScam(
        account_to_ban,
        {"from": get_account(index=1), "amount": 1_0_00000000_0_00000000},
    )
    assert proxy_crowdsafe.scamThreatLevel(account_to_ban) == 523811

    with pytest.raises(exceptions.VirtualMachineError) as veto:
        proxy_crowdsafe.ReportSafe(
            FAKE_ADDRESS, {"from": account_to_ban, "amount": 100}
        )


def test_report_scam_user_by_awareness():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_contract()
    account_to_ban = get_account(index=4)
    proxy_crowdsafe._setReporterCountBan(3, {"from": get_account()})

    # Don't Like Bot Account
    proxy_crowdsafe.ReportScam(
        account_to_ban,
        {"from": get_account(index=1), "amount": 1},
    )
    proxy_crowdsafe.ReportScam(
        account_to_ban,
        {"from": get_account(index=2), "amount": 1},
    )

    # Bot Account can still vote
    proxy_crowdsafe.ReportSafe(FAKE_ADDRESS, {"from": account_to_ban, "amount": 1})

    proxy_crowdsafe.ReportScam(
        account_to_ban,
        {"from": get_account(index=3), "amount": 1},
    )

    with pytest.raises(exceptions.VirtualMachineError) as veto:
        proxy_crowdsafe.ReportSafe(
            FAKE_ADDRESS, {"from": account_to_ban, "amount": 100}
        )

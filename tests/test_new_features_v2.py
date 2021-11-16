import math 
import pytest
from brownie import exceptions
from scripts.helpful_scripts import get_account

from tests.migrate_helper import deploy_and_migrate

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
FAKE_ADDRESS = "0x0000000000000000000000000000000000000001"

def test_banned_and_recited_verified():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
    admin=get_account()
    hater = get_account(index=1)
    account_to_ban = get_account(index=2)
    liker = get_account(index=3)
    proxy_crowdsafe._setAmountBan(2,{"from":admin})

    # Don't Like Bot Account
    proxy_crowdsafe.ReportScam(
        account_to_ban,
        {"from": hater, "amount": 21000_0_00000000},
    )
    proxy_crowdsafe.ReportScam(
        hater,
        {"from": liker, "amount": 42000_0_00000000},
    )

    with pytest.raises(exceptions.VirtualMachineError) as veto:
        proxy_crowdsafe.ReportSafe(
            FAKE_ADDRESS, {"from": account_to_ban, "amount": 100}
        )
    proxy_crowdsafe.transfer(account_to_ban,3,{"from":liker})

    proxy_crowdsafe.ReportSafe(
        FAKE_ADDRESS, {"from": account_to_ban, "amount": 100}
    )    


def test_banned_and_recited_awareness_pass():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
    admin=get_account()
    account_to_ban = get_account(index=1)
    proxy_crowdsafe._setReporterCountBan(3,{"from":admin})

    proxy_crowdsafe.ReportSafe(
        admin,
        {"from": account_to_ban, "amount": 210000_0_00000000},
    )
    assert proxy_crowdsafe.reporterReportLength(account_to_ban) ==1

    # Don't Like Bot Account
    for i in range(4):
        proxy_crowdsafe.ReportScam(
            account_to_ban,
            {"from": get_account(index=i+2), "amount": 21000_0_00000000},
        )

    with pytest.raises(exceptions.VirtualMachineError) as veto:
        proxy_crowdsafe.ReportSafe(
            FAKE_ADDRESS, {"from": account_to_ban, "amount": 100}
        )
    assert proxy_crowdsafe.balanceOf(account_to_ban)==11
    tx=proxy_crowdsafe.ConvertTokensToScamAwarenessPoints(10,{"from":account_to_ban})
    assert proxy_crowdsafe.balanceOf(account_to_ban)==1
    eventCaught=tx.events["ArtificialAwareness"];

    assert eventCaught["requester"]==account_to_ban
    assert eventCaught["scamOrSafe"]==0
    assert eventCaught["verifiedBurned"]==10
    assert eventCaught["awarenessChanged"]==1
    proxy_crowdsafe.ReportSafe(
        FAKE_ADDRESS, {"from": account_to_ban, "amount": 100}
    )


def test_banned_and_recited_awareness_lost_residual_error():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
    admin=get_account()
    account_to_ban = get_account(index=1)
    proxy_crowdsafe._setReporterCountBan(3,{"from":admin})

    proxy_crowdsafe.ReportSafe(
        admin,
        {"from": account_to_ban, "amount": 63000_0_00000000},
    )
    assert proxy_crowdsafe.reporterReportLength(account_to_ban) ==1

    # Don't Like Bot Account
    for i in range(4):
        proxy_crowdsafe.ReportScam(
            account_to_ban,
            {"from": get_account(index=i+2), "amount": 21000_0_00000000},
        )

    with pytest.raises(exceptions.VirtualMachineError) as veto:
        proxy_crowdsafe.ConvertTokensToScamAwarenessPoints(4,{"from":account_to_ban})
    
# def test_banned_and_recited_awareness_pass():
#     (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
#     admin=get_account()
#     account_to_ban = get_account(index=1)
#     proxy_crowdsafe._setReporterCountBan(3,{"from":admin})

#     proxy_crowdsafe.ReportSafe(
#         admin,
#         {"from": account_to_ban, "amount": 210000_0_00000000},
#     )
#     assert proxy_crowdsafe.balanceOf(account_to_ban)==11
#     assert proxy_crowdsafe.safeAwareness(account_to_ban) ==0
#     proxy_crowdsafe.ConvertTokensToSafeAwarenessPoints(10,{"from":account_to_ban})
#     assert proxy_crowdsafe.safeAwareness(account_to_ban) ==1
#     assert proxy_crowdsafe.balanceOf(account_to_ban)==1

def test_event_listening():
    account = get_account(index=1)
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
    tx=proxy_crowdsafe.ReportSafe(
        FAKE_ADDRESS,
        {"from": account, "amount": 1_0_00000000_0_00000000},
    )
    reporter=tx.events[1]["reporter"]
    reciever=tx.events[1]["reciever"]
    confidence=tx.events[1]["confidence"]
    assert reporter == account
    assert reciever == FAKE_ADDRESS
    assert confidence == int(math.ceil(1_0_00000000_0_00000000/21000_0_00000000))

def test_report_safe_and_share_fair_portions():
    admin = get_account()
    you = get_account(index=1)
    me = get_account(index=2)
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()
    proxy_crowdsafe.ReportSafeAndShare(you,50,{"from":me,"amount":2100000000000000}).wait(1)
    assert proxy_crowdsafe.balanceOf(you) == 50
    assert proxy_crowdsafe.balanceOf(me) == 50

    proxy_crowdsafe.ReportSafeAndShare(you,75,{"from":me,"amount":2100000000000000}).wait(1)
    assert proxy_crowdsafe.balanceOf(you) == 125
    assert proxy_crowdsafe.balanceOf(me) == 75
    

def test_report_safe_and_share_minimum_portions():
    admin = get_account()
    you = get_account(index=1)
    me = get_account(index=2)
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_and_migrate()


    proxy_crowdsafe.ReportSafeAndShare(you,10,{"from":me}).wait(1)
    assert proxy_crowdsafe.balanceOf(me) == 1
    assert proxy_crowdsafe.balanceOf(you) == 1
import pytest
from brownie import (
    CrowdSafe,
    CrowdSafeV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    exceptions,
)

from scripts.deploy_crowd_safe import deploy_contract, deploy_crowdsafe
from scripts.helpful_scripts import get_account, encode_function_data
from scripts.migrate_crowdsafe import do_upgrade
from tests.migrate_helper import deploy_and_migrate, deploy_for_migrate

FAKE_ADDRESS = "0x0000000000000000000000000000000000000001"
ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

def test_proxy_upgrade_gain_functions():
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

    crowdsafe_v2 = CrowdSafeV2.deploy({"from": account})
    proxy_crowdsafe = Contract.from_abi(
        "CrowdSafeV2", proxy.address, CrowdSafeV2.abi
    )
    # Act
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_crowdsafe._goPause({"from": account})

    proxy_admin.upgrade(proxy.address, crowdsafe_v2.address, {"from": account})

    assert proxy_crowdsafe._pause() == False
    proxy_crowdsafe._goPause({"from": account})
    assert proxy_crowdsafe._pause() == True



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
    # This next line shouldn't be possible
    assert proxy_crowdsafe._setMinimumCompensation(100, {"from":get_account(index=1)})

    account = get_account()
    contract = deploy_crowdsafe(CrowdSafeV2)
    proxy_admin.upgrade(proxy.address, contract.address, {"from": account})

    assert proxy_crowdsafe.highestScamThreatAwareness() == 1
    assert proxy_crowdsafe.highestScamThreatLevel() == 5
    assert proxy_crowdsafe.highestScamThreatAddress() == FAKE_ADDRESS
    with pytest.raises(exceptions.VirtualMachineError):
        assert proxy_crowdsafe._setMinimumCompensation(100, {"from":get_account(index=1)})
    

def test_proxy_upgrade_and_batch_update():
    account = get_account()
    (proxy, proxy_admin, proxy_crowdsafe) =deploy_and_migrate()
    assert proxy_crowdsafe.minimumCompensation()==21000000000000;
    assert proxy_crowdsafe.getAmountBan()==5000000;
    assert proxy_crowdsafe.getReporterCountBan()==10000;
    assert proxy_crowdsafe.useProvidedPortion()==True;
    assert proxy_crowdsafe.defaultPortionToThem()==50;
    assert proxy_crowdsafe.minimumPortionToThem()==10;

    (proxy, proxy_admin, proxy_crowdsafe) = deploy_for_migrate(proxy, proxy_admin)
    proxy_crowdsafe.batchSet([2,2100000000,1000000,100,95,91,10],[],[False],{"from":account})

    assert proxy_crowdsafe.minimumCompensation()==2100000000;
    assert proxy_crowdsafe.getAmountBan()==1000000;
    assert proxy_crowdsafe.getReporterCountBan()==100;
    assert proxy_crowdsafe.useProvidedPortion()==False;
    assert proxy_crowdsafe.defaultPortionToThem()==95;
    assert proxy_crowdsafe.minimumPortionToThem()==91;

def helper_assert_all_storage_vars_consistent(proxy_crowdsafe, me,you):
    assert proxy_crowdsafe.highestScamThreatLevel()==2
    assert proxy_crowdsafe.highestScamThreatAwareness()==1
    assert proxy_crowdsafe.highestScamThreatAddress()==FAKE_ADDRESS
    assert proxy_crowdsafe.reportedScams(0) == FAKE_ADDRESS
    assert proxy_crowdsafe.scamReporters(0) == me
    assert proxy_crowdsafe.scamReporterSet(me) ==True
    assert proxy_crowdsafe.userContractScamLevel(me,FAKE_ADDRESS) == 2
    assert proxy_crowdsafe.scamThreatLevel(FAKE_ADDRESS)==2
    assert proxy_crowdsafe.scamThreatAwareness(FAKE_ADDRESS) ==1

    assert proxy_crowdsafe.highestSafetyLevel()==3
    assert proxy_crowdsafe.highestSafetyAwareness()==1
    assert proxy_crowdsafe.highestSafetyAddress()==FAKE_ADDRESS
    assert proxy_crowdsafe.reportedSafe(1)==FAKE_ADDRESS
    assert proxy_crowdsafe.safeReporters(1)==you
    assert proxy_crowdsafe.safeReporterSet(you)==True
    assert proxy_crowdsafe.userContractSafeLevel(you,FAKE_ADDRESS)==3
    assert proxy_crowdsafe.safeLevel(FAKE_ADDRESS)==3
    assert proxy_crowdsafe.safeAwareness(FAKE_ADDRESS)==1


def test_assert_all_storage_vars_consistent():
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_contract()
    me=get_account(index=1)
    you=get_account(index=2)
    proxy_crowdsafe.ReportScam(FAKE_ADDRESS,{"from":me,"amount":21000_0_00000000});
    proxy_crowdsafe.ReportSafe(FAKE_ADDRESS,{"from":you,"amount":21000_0_00000000*2});
    assert proxy_crowdsafe.minimumCompensation() ==21000_0_00000000
    assert proxy_crowdsafe.version()==1
    
    helper_assert_all_storage_vars_consistent(proxy_crowdsafe,me,you)

    (proxy, proxy_admin, proxy_crowdsafe) = do_upgrade(deploy_crowdsafe(CrowdSafeV2),proxy, proxy_admin)
    proxy_crowdsafe.batchSet([2,11000000000000,5000000,1000,50,10,10],[],[True],{"from":get_account()})
    assert proxy_crowdsafe.minimumCompensation() ==11000_0_00000000
    assert proxy_crowdsafe.version()==2
    helper_assert_all_storage_vars_consistent(proxy_crowdsafe, me,you)
    assert proxy_crowdsafe.useProvidedPortion() == True
    assert proxy_crowdsafe.defaultPortionToThem() ==50
    assert proxy_crowdsafe.minimumPortionToThem() == 10
    assert proxy_crowdsafe.verifiedToAwarenessRatio() == 10
    assert proxy_crowdsafe._pause() == False
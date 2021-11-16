from brownie import (
    CrowdSafe,
    CrowdSafeV2,
)
from scripts.deploy_crowd_safe import deploy_proxy
from scripts.helpful_scripts import get_account
from scripts.migrate_crowdsafe import deploy_crowdsafe, do_upgrade

def deploy_before_migrate():
    contract=deploy_crowdsafe(CrowdSafe)
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_proxy(contract)
    return (proxy, proxy_admin, proxy_crowdsafe) 

def deploy_for_migrate(proxy, proxy_admin):
    contract = deploy_crowdsafe(CrowdSafeV2)
    (proxy, proxy_admin, proxy_crowdsafe) =do_upgrade(contract,proxy, proxy_admin)
    return (proxy, proxy_admin, proxy_crowdsafe) 

def deploy_and_migrate():
    contract=deploy_crowdsafe(CrowdSafe)
    (proxy, proxy_admin, proxy_crowdsafe) = deploy_proxy(contract)
    contract = deploy_crowdsafe(CrowdSafeV2)
    (proxy, proxy_admin, proxy_crowdsafe)= do_upgrade(contract,proxy, proxy_admin)
    proxy_crowdsafe.batchSet([2,21000000000000,5000000,10000,50,10,10],[],[True],{"from":get_account()})
    return (proxy, proxy_admin, proxy_crowdsafe)
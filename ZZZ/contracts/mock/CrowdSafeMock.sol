// SPDX-License-Identifier: MIT
pragma solidity 0.8.9;

import "../vendor/openzeppelin-contracts/upgradeable-contracts/token/ERC20/ERC20Upgradeable.sol";
import "../vendor/openzeppelin-contracts/upgradeable-contracts/access/OwnableUpgradeable.sol";

contract CrowdSafeMock is ERC20Upgradeable, OwnableUpgradeable {
    uint256 public minimumCompensation;
    uint256 public version;
    uint256 private _amountBan;
    uint256 private _reporterCountBan;

    //Scam Variables
    uint256 public highestScamThreatLevel;
    uint256 public highestScamThreatAwareness;
    address public highestScamThreatAddress;
    address[] public reportedScams;
    address[] public scamReporters;

    mapping(address => bool) public scamReporterSet;
    mapping(address => mapping(address => uint256))
        public userContractScamLevel;
    mapping(address => uint256) public scamThreatLevel;
    mapping(address => uint256) public scamThreatAwareness;

    //Safe Variables
    uint256 public highestSafetyLevel;
    uint256 public highestSafetyAwareness;
    address public highestSafetyAddress;
    address[] public reportedSafe;
    address[] public safeReporters;

    mapping(address => bool) public safeReporterSet;
    mapping(address => mapping(address => uint256))
        public userContractSafeLevel;
    mapping(address => uint256) public safeLevel;
    mapping(address => uint256) public safeAwareness;

    function __CrowdSafe_init(uint256 _version) public initializer {
        __Ownable_init();
        __ERC20_init("Crowd Safe", "VERIFIED");

        minimumCompensation = 21000_0_00000000 wei;
        _amountBan = 500000;
        _reporterCountBan = 100;

        version = _version;

        if (!founderMintBan[_msgSender()]) {
            /**
             * Upon constuction of Crowd Safe contract.
             * The only means of collecting VERIFIED tokens is by reporting safe
             * or scam contracts
             */
            uint256 founderReserve = 48690474535 wei; // Matic Value
            // uint256 founderReserve = 23809523; // Ethereum Value
            _mint(msg.sender, founderReserve);

            reportedSafe.push(msg.sender);
            safeReporters.push(msg.sender);
            safeReporterSet[msg.sender] = true;
            userContractSafeLevel[msg.sender][address(this)] = founderReserve;
            safeLevel[address(this)] = founderReserve;
            safeAwareness[address(this)] = 1;
            founderMintBan[msg.sender] = true;
        }
    }

    function ReportScam(address fraudContract)
        public
        payable
        founderBanned
        banSpamBot
    {
        require(fraudContract != address(0));

        uint256 confidence = (msg.value + minimumCompensation) /
            minimumCompensation;
        _mint(msg.sender, confidence);
        if (!scamReporterSet[msg.sender]) {
            scamReporterSet[msg.sender] = true;
            scamReporters.push(msg.sender);
        }
        if (userContractScamLevel[msg.sender][fraudContract] == 0) {
            if (scamThreatLevel[fraudContract] == 0) {
                reportedScams.push(fraudContract);
            }
            scamThreatAwareness[fraudContract]++;
        }
        scamThreatLevel[fraudContract] += confidence;
        userContractScamLevel[msg.sender][fraudContract] = confidence;
        _ifMaxThreat(fraudContract);
    }

    function ReportSafe(address verifiedContract)
        public
        payable
        founderBanned
        banSpamBot
    {
        require(verifiedContract != address(0));

        uint256 confidence = (msg.value + minimumCompensation) /
            minimumCompensation;
        _mint(msg.sender, confidence);
        if (!safeReporterSet[msg.sender]) {
            safeReporterSet[msg.sender] = true;
            safeReporters.push(msg.sender);
        }
        if (userContractSafeLevel[msg.sender][verifiedContract] == 0) {
            if (safeLevel[verifiedContract] == 0) {
                reportedSafe.push(verifiedContract);
            }
            safeAwareness[verifiedContract]++;
        }
        safeLevel[verifiedContract] += confidence;
        userContractSafeLevel[msg.sender][verifiedContract] = confidence;
        _ifMaxSafety(verifiedContract);
    }

    function getReportedScamsLength() public view returns (uint256) {
        return reportedScams.length;
    }

    function getScamReportersLength() public view returns (uint256) {
        return scamReporters.length;
    }

    function getReportedSafeLength() public view returns (uint256) {
        return reportedSafe.length;
    }

    function getSafeReportersLength() public view returns (uint256) {
        return safeReporters.length;
    }

    function _ifMaxThreat(address fraudContract) internal {
        if (scamThreatLevel[fraudContract] > highestScamThreatLevel) {
            highestScamThreatAwareness = scamThreatAwareness[fraudContract];
            highestScamThreatLevel = scamThreatLevel[fraudContract];
            highestScamThreatAddress = fraudContract;
        }
    }

    function _ifMaxSafety(address verifiedContract) internal {
        if (safeLevel[verifiedContract] > highestSafetyLevel) {
            highestSafetyAwareness = safeAwareness[verifiedContract];
            highestSafetyLevel = safeLevel[verifiedContract];
            highestSafetyAddress = verifiedContract;
        }
    }

    function _setMinimumCompensation(uint256 _minimumCompensation) public {
        minimumCompensation = _minimumCompensation;
    }

    function _setAmountBan(uint256 amountBan) public {
        _amountBan = amountBan;
    }

    function _setReporterCountBan(uint256 reporterCountBan) public {
        _reporterCountBan = reporterCountBan;
    }

    function setVersion(uint256 _version) public onlyOwner {
        version = _version;
    }

    modifier banSpamBot() {
        require(
            scamThreatLevel[msg.sender] < _amountBan && //Matic Value
                // scamThreatLevel[msg.sender] < 10 && //Eth Value
                scamThreatAwareness[msg.sender] < _reporterCountBan,
            // scamThreatAwareness[msg.sender] < 5,
            "People's choice has banned this wallet from voting"
        );
        _;
    }

    /**
     * `modifier founderBanned()` bans the founder from minting new tokens however they
     * deem fit. It is important that a contract that inspires to wipe out dubious contracts
     * is in-and of itself a reliable contract. In this effort, founderBanned mofifier limits
     * the founder's capability. the ERC20Upgradeable.sol requires that any newly minted tokens
     * are not by the founders, but rather by the intended end-users through the intended mechanisms.
     *
     * This technique will protect "Crowd Safe" from the dreaded rug-pull.
     */
}

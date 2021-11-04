// SPDX-License-Identifier: MIT
pragma solidity 0.8.9;

import "./vendor/openzeppelin-contracts/upgradeable-contracts/token/ERC20/ERC20Upgradeable.sol";
import "./vendor/openzeppelin-contracts/upgradeable-contracts/access/OwnableUpgradeable.sol";

contract CrowdSafe is ERC20Upgradeable {
    uint256 public minimumCompensation = 21000000000000 wei;
    uint256 public version;

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

    constructor() {
        /**
         * Upon constuction of Crowd Safe contract.
         * The only means of collecting VERIFIED tokens is by reporting safe
         * or scam contracts
         */
        uint256 founderReserve = 500_000_000_000_0_00_000_000;
        _mint(msg.sender, founderReserve);
        reportedSafe.push(msg.sender);
        safeReporters.push(msg.sender);
        safeReporterSet[msg.sender] = true;
        userContractSafeLevel[msg.sender][address(this)] = founderReserve;
        safeLevel[address(this)] = 1;
        founderMintBan[msg.sender] = true;
    }

    function __CrowdSafe_init(uint256 _version) public initializer {
        __ERC20_init("Crowd Safe", "VERIFIED");
        version = _version;
        founderMintBan[msg.sender] = true;
    }

    function ReportScam(address fraudContract) public payable founderBanned {
        require(fraudContract != address(0));

        uint256 initialGas = gasleft();
        _mint(msg.sender, msg.value + minimumCompensation);
        uint256 confidence = msg.value + (gasleft() - initialGas);
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

    function ReportSafe(address verifiedContract) public payable founderBanned {
        require(verifiedContract != address(0));

        uint256 initialGas = gasleft();
        _mint(msg.sender, msg.value + minimumCompensation);
        uint256 confidence = msg.value + (gasleft() - initialGas);
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

    function _ifMaxThreat(address fraudContract) internal {
        if (scamThreatLevel[fraudContract] > highestScamThreatLevel) {
            highestScamThreatAwareness = scamThreatAwareness[fraudContract];
            highestScamThreatLevel = scamThreatLevel[fraudContract];
            highestScamThreatAddress = fraudContract;
        }
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

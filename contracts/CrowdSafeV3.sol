// SPDX-License-Identifier: MIT
pragma solidity 0.8.9;

import "./vendor/openzeppelin-contracts/upgradeable-contracts/token/ERC20/ERC20Upgradeable.sol";
import "./vendor/openzeppelin-contracts/upgradeable-contracts/access/OwnableUpgradeable.sol";

contract CrowdSafeV3 is ERC20Upgradeable, OwnableUpgradeable {
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
        whenNotPaused
    {
        require(fraudContract != address(0));
        require(fraudContract != msg.sender);

        uint256 confidence = (msg.value + minimumCompensation) /
            minimumCompensation;
        _mint(msg.sender, confidence);
        if (!scamReporterSet[msg.sender]) {
            if (scamThreatLevel[fraudContract] == 0) {
                reportedScams.push(fraudContract);
            }
            reporterReportLength[msg.sender]++;
            scamReporterSet[msg.sender] = true;
            scamReporters.push(msg.sender);
            reporterReports[msg.sender].push(fraudContract);
            scamThreatAwareness[fraudContract]++;
        }
        scamThreatLevel[fraudContract] += confidence;
        userContractScamLevel[msg.sender][fraudContract] += confidence;
        _ifMaxThreat(fraudContract);
        lastActive[msg.sender] = block.number;
        lastReferenced[fraudContract] = block.number;
        emit SubmitReport(msg.sender, fraudContract, 0, confidence);
    }

    function ReportSafe(address verifiedContract)
        public
        payable
        founderBanned
        banSpamBot
        whenNotPaused
    {
        require(verifiedContract != address(0));
        require(verifiedContract != msg.sender);

        uint256 confidence = (msg.value + minimumCompensation) /
            minimumCompensation;
        _mint(msg.sender, confidence);
        _submitSafeReport(verifiedContract, confidence);
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

    function _setMinimumCompensation(uint256 _minimumCompensation)
        public
        onlyOwner
    {
        minimumCompensation = _minimumCompensation;
    }

    function _setAmountBan(uint256 amountBan) public onlyOwner {
        _amountBan = amountBan;
    }

    function _setReporterCountBan(uint256 reporterCountBan) public onlyOwner {
        _reporterCountBan = reporterCountBan;
    }

    modifier banSpamBot() {
        require(
            scamThreatLevel[msg.sender] < balanceOf(msg.sender) + _amountBan &&
                scamThreatAwareness[msg.sender] <
                reporterReportLength[msg.sender] + _reporterCountBan,
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

    /**
     * CrowdSafe V2 Additions
     */

    bool public useProvidedPortion;
    uint8 public defaultPortionToThem;
    uint8 public minimumPortionToThem;
    uint256 public verifiedToAwarenessRatio;
    bool public _pause;
    mapping(address => uint256) public reporterReportLength;
    mapping(address => address[]) public reporterReports;

    event SubmitReport(
        address reporter,
        address reciever,
        uint8 scamOrSafe, //Leaving the door open for other registries?!
        uint256 confidence
    );
    event ArtificialAwareness(
        address requester,
        uint8 scamOrSafe, //Leaving the door open for other registries?!
        uint256 verifiedBurned,
        uint256 awarenessChanged
    );

    function getAmountBan() public view onlyOwner returns (uint256) {
        return _amountBan;
    }

    function getReporterCountBan() public view onlyOwner returns (uint256) {
        return _reporterCountBan;
    }

    function _setUseProvidedPortion(bool _useProvidedPortion) public onlyOwner {
        useProvidedPortion = _useProvidedPortion;
    }

    function _setVerifiedToAwarenessRatio(uint256 _verifiedToAwarenessRatio)
        public
        onlyOwner
    {
        verifiedToAwarenessRatio = _verifiedToAwarenessRatio;
    }

    function _setDefaultPortionToThem(uint8 _defaultPortionToThem)
        public
        onlyOwner
    {
        require(
            _defaultPortionToThem >= minimumPortionToThem &&
                _defaultPortionToThem <= 100
        );
        defaultPortionToThem = _defaultPortionToThem;
    }

    function _setMinimumPortionToThem(uint8 _minimumPortionToThem)
        public
        onlyOwner
    {
        require(_minimumPortionToThem <= 100);
        minimumPortionToThem = _minimumPortionToThem;
    }

    /**
     * Used in conjunction with contract updates
     */
    function batchSet(
        uint256[] memory argsUint,
        bytes[] memory byteArgs,
        bool[] memory boolArgs
    ) public onlyOwner {
        version = argsUint[0];
        _setMinimumCompensation(argsUint[1]);
        _setAmountBan(argsUint[2]);
        _setReporterCountBan(argsUint[3]);

        _setUseProvidedPortion(boolArgs[0]); // Boolean
        _setDefaultPortionToThem(uint8(argsUint[4]));
        _setMinimumPortionToThem(uint8(argsUint[5]));
        _setVerifiedToAwarenessRatio(argsUint[6]);
    }

    function ReportSafeAndShare(
        address shareMate,
        uint8 portionToThem /** May Or May not be used */
    ) public payable founderBanned banSpamBot whenNotPaused {
        require(shareMate != address(0));
        require(msg.sender != address(0));
        require(shareMate != msg.sender);
        uint8 portionToMe;
        if (useProvidedPortion) {
            require(
                portionToThem >= minimumPortionToThem && portionToThem <= 100
            );
            portionToMe = 100 - portionToThem;
        } else {
            portionToThem = defaultPortionToThem;
            portionToMe = 100 - defaultPortionToThem;
        }

        uint256 msgvalue = msg.value;
        uint256 confidenceMine = ((msgvalue + minimumCompensation) *
            uint8(portionToMe)) / (minimumCompensation * 100);
        uint256 confidenceTheirs = ((msgvalue + minimumCompensation) *
            portionToThem) / (minimumCompensation * 100);

        confidenceMine = confidenceMine > 0 ? confidenceMine : 1;
        confidenceTheirs = confidenceTheirs > 0 ? confidenceTheirs : 1;

        _mint(msg.sender, confidenceMine);
        _mint(shareMate, confidenceTheirs);

        _submitSafeReport(shareMate, confidenceMine + confidenceTheirs);
    }

    function _submitSafeReport(address safeReportable, uint256 confidence)
        internal
        whenNotPaused
    {
        if (!safeReporterSet[msg.sender]) {
            if (safeLevel[safeReportable] == 0) {
                reportedSafe.push(safeReportable);
            }
            safeReporterSet[msg.sender] = true;
            safeReporters.push(msg.sender);
            reporterReportLength[msg.sender]++;
            reporterReports[msg.sender].push(safeReportable);
            safeAwareness[safeReportable]++;
        }

        safeLevel[safeReportable] += confidence;
        userContractSafeLevel[msg.sender][safeReportable] += confidence;
        _ifMaxSafety(safeReportable);
        lastActive[msg.sender] = block.number;
        lastReferenced[safeReportable] = block.number;
        emit SubmitReport(msg.sender, safeReportable, 1, confidence);
    }

    function ConvertTokensToScamAwarenessPoints(uint256 verifiedAmount)
        public
        whenNotPaused
    {
        require(balanceOf(msg.sender) >= verifiedAmount);
        uint256 awarenessChanged = verifiedAmount / verifiedToAwarenessRatio;
        require(awarenessChanged > 0);
        _burn(msg.sender, verifiedAmount);
        scamThreatAwareness[msg.sender] -= awarenessChanged;
        emit ArtificialAwareness(
            msg.sender,
            0,
            verifiedAmount,
            awarenessChanged
        );
    }

    function ConvertTokensToSafeAwarenessPoints(uint256 verifiedAmount)
        public
        whenNotPaused
    {
        require(balanceOf(msg.sender) >= verifiedAmount);
        uint256 awarenessChanged = verifiedAmount / verifiedToAwarenessRatio;
        _burn(msg.sender, verifiedAmount);
        safeAwareness[msg.sender] += awarenessChanged;
        emit ArtificialAwareness(
            msg.sender,
            1,
            verifiedAmount,
            awarenessChanged
        );
    }

    function _goPause() public onlyOwner whenNotPaused {
        _pause = true;
    }

    function _goUnpause() public onlyOwner whenPaused {
        _pause = false;
    }

    modifier whenPaused() {
        require(!_pause);
        _;
    }
    modifier whenNotPaused() {
        require(!_pause);
        _;
    }

    /**
     * CrowdSafe V3 Additions
     */
    mapping(address => uint256) lastActive;
    mapping(address => uint256) lastReferenced;
}

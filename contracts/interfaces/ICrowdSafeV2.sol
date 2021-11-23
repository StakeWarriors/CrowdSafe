// SPDX-License-Identifier: MIT
pragma solidity 0.8.9;

interface ICrowdSafeV2 {
    function __CrowdSafe_init(uint256 _version) external payable;

    function ReportScam(address fraudContract) external payable;

    function ReportSafe(address verifiedContract) external payable;

    function getReportedScamsLength() external view returns (uint256);

    function getScamReportersLength() external view returns (uint256);

    function getReportedSafeLength() external view returns (uint256);

    function getSafeReportersLength() external view returns (uint256);

    function _setMinimumCompensation(uint256 _minimumCompensation) external;

    function _setAmountBan(uint256 amountBan) external;

    function _setReporterCountBan(uint256 reporterCountBan) external;

    /**
     * `modifier ()` bans the founder from minting new tokens however they
     * deem fit. It is important that a contract that inspires to wipe out dubious contracts
     * is in-and of itself a reliable contract. In this effort,  mofifier limits
     * the founder's capability. the ERC20Upgradeable.sol requires that any newly minted tokens
     * are not by the founders, but rather by the intended end-users through the intended mechanisms.
     *
     * This technique will protect "Crowd Safe" from the dreaded rug-pull.
     */

    /**
     * CrowdSafe V2 Additions
     */

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

    function getAmountBan() external view returns (uint256);

    function getReporterCountBan() external view returns (uint256);

    function _setUseProvidedPortion(bool _useProvidedPortion) external;

    function _setVerifiedToAwarenessRatio(uint256 _verifiedToAwarenessRatio)
        external;

    function _setDefaultPortionToThem(uint8 _defaultPortionToThem) external;

    function _setMinimumPortionToThem(uint8 _minimumPortionToThem) external;

    function ReportSafeAndShare(address shareMate, uint8 portionToThem)
        external
        payable;

    function ConvertTokensToScamAwarenessPoints(uint256 verifiedAmount)
        external;

    function ConvertTokensToSafeAwarenessPoints(uint256 verifiedAmount)
        external;
}

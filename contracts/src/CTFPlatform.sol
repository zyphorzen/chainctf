// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ECDSA} from "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import {EIP712} from "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract CTFPlatform is Ownable, EIP712 {
    using ECDSA for bytes32;

    struct Challenge {
        uint256 id;
        uint256 reward;
        bool active;
    }

    struct Achievement {
        address player;
        uint256 challengeId;
        uint256 nonce;
        uint256 deadline;
    }

    mapping(uint256 => Challenge) public challenges;
    mapping(address => uint256) public scores;
    mapping(address => mapping(uint256 => bool)) public solved;
    mapping(address => mapping(uint256 => bool)) public usedNonces;

    uint256 public challengeCount;
    address public verifier;

    bytes32 private constant ACHIEVEMENT_TYPEHASH =
        keccak256(
            "Achievement(address player,uint256 challengeId,uint256 nonce,uint256 deadline)"
        );

    error ZeroAddress();
    error ChallengeNotFound();
    error ChallengeInactive();
    error ChallengeAlreadySolved();
    error NonceAlreadyUsed();
    error AuthorizationExpired();
    error InvalidSignature();

    event ChallengeCreated(uint256 indexed challengeId, uint256 reward);
    event ChallengeStatusChanged(uint256 indexed challengeId, bool active);

    event VerifierChanged(
        address indexed previousVerifier,
        address indexed newVerifier
    );

    event ChallengeSolved(
        address indexed player,
        uint256 indexed challengeId,
        uint256 reward
    );

    constructor(
        address initialOwner,
        address initialVerifier
    ) Ownable(initialOwner) EIP712("ChainCTF", "1") {
        if (initialOwner == address(0) || initialVerifier == address(0)) {
            revert ZeroAddress();
        }

        verifier = initialVerifier;
    }

    function setVerifier(address newVerifier) external onlyOwner {
        if (newVerifier == address(0)) {
            revert ZeroAddress();
        }

        address previousVerifier = verifier;
        verifier = newVerifier;
        emit VerifierChanged(previousVerifier, newVerifier);
    }

    function createChallenge(uint256 reward) external onlyOwner {
        challengeCount++;

        challenges[challengeCount] = Challenge({
            id: challengeCount,
            reward: reward,
            active: true
        });

        emit ChallengeCreated(challengeCount, reward);
    }

    function setChallengeStatus(
        uint256 challengeId,
        bool active
    ) external onlyOwner {
        if (challengeId == 0 || challengeId > challengeCount) {
            revert ChallengeNotFound();
        }

        challenges[challengeId].active = active;
        emit ChallengeStatusChanged(challengeId, active);
    }

    function submitAchievement(
        Achievement calldata achievement,
        bytes calldata signature
    ) external {
        if (
            achievement.player == address(0) || achievement.player != msg.sender
        ) {
            revert InvalidSignature();
        }

        if (
            achievement.challengeId == 0 ||
            achievement.challengeId > challengeCount
        ) {
            revert ChallengeNotFound();
        }

        Challenge memory challenge = challenges[achievement.challengeId];

        if (!challenge.active) {
            revert ChallengeInactive();
        }

        if (solved[msg.sender][achievement.challengeId]) {
            revert ChallengeAlreadySolved();
        }

        if (usedNonces[msg.sender][achievement.nonce]) {
            revert NonceAlreadyUsed();
        }

        if (block.timestamp > achievement.deadline) {
            revert AuthorizationExpired();
        }

        bytes32 structHash = keccak256(
            abi.encode(
                ACHIEVEMENT_TYPEHASH,
                achievement.player,
                achievement.challengeId,
                achievement.nonce,
                achievement.deadline
            )
        );

        bytes32 digest = _hashTypedDataV4(structHash);
        address signer = digest.recover(signature);

        if (signer != verifier) {
            revert InvalidSignature();
        }

        usedNonces[msg.sender][achievement.nonce] = true;
        solved[msg.sender][achievement.challengeId] = true;
        scores[msg.sender] += challenge.reward;

        emit ChallengeSolved(
            msg.sender,
            achievement.challengeId,
            challenge.reward
        );
    }
}

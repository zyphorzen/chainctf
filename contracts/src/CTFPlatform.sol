// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract CTFPlatform is Ownable {
    struct Challenge {
        uint256 id;
        bytes32 challengeHash;
        uint256 reward;
        bool active;
    }

    mapping(uint256 => Challenge) public challenges;
    mapping(address => uint256) public scores;
    mapping(address => mapping(uint256 => bool)) public solved;

    uint256 public challengeCount;

    error ChallengeNotFound();
    error ChallengeInactive();
    error ChallengeAlreadySolved();
    error InvalidProof();
    error InvalidChallenge();

    event ChallengeCreated(uint256 indexed challengeId, bytes32 indexed challengeHash, uint256 reward);

    event ChallengeStatusChanged(uint256 indexed challengeId, bool active);

    event ChallengeSolved(address indexed player, uint256 indexed challengeId, uint256 reward);

    constructor(address initialOwner) Ownable(initialOwner) {}

    function createChallenge(bytes32 challengeHash, uint256 reward) external onlyOwner {
        challengeCount++;

        challenges[challengeCount] =
            Challenge({id: challengeCount, challengeHash: challengeHash, reward: reward, active: true});

        emit ChallengeCreated(challengeCount, challengeHash, reward);
    }

    function setChallengeStatus(uint256 challengeId, bool active) external onlyOwner {
        if (challengeId == 0 || challengeId > challengeCount) {
            revert ChallengeNotFound();
        }

        challenges[challengeId].active = active;

        emit ChallengeStatusChanged(challengeId, active);
    }

    function solveChallenge(uint256 challengeId, bytes32 proof) external {
        if (challengeId == 0 || challengeId > challengeCount) {
            revert ChallengeNotFound();
        }

        Challenge memory challenge = challenges[challengeId];

        if (!challenge.active) {
            revert ChallengeInactive();
        }

        if (solved[msg.sender][challengeId]) {
            revert ChallengeAlreadySolved();
        }

        if (proof != challenge.challengeHash) {
            revert InvalidProof();
        }

        solved[msg.sender][challengeId] = true;
        scores[msg.sender] += challenge.reward;

        emit ChallengeSolved(msg.sender, challengeId, challenge.reward);
    }

    function getChallengeHash(uint256 challengeId, bytes32 solutionHash) public pure returns (bytes32) {
        return keccak256(abi.encode(challengeId, solutionHash));
    }
}

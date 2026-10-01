// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract CTFPlatform {
    struct Challenge {
        uint256 id;
        bytes32 challengeHash;
        uint256 reward;
        bool active;
    }

    mapping (uint256 => Challenge) public challenges;
    mapping (address => uint256) public scores;
    mapping (address => mapping (uint256 => bool)) public solved;

    uint256 public challengeCount;

    event ChallengeCreated(
        uint256 indexed challengeId,
        bytes32 challengeHash,
        uint256 reward
    );

    event ChallengeSolved(
        address indexed player,
        uint256 indexed challengeId,
        uint256 reward
    );

    function createChallenge(
        bytes32 challengeHash,
        uint256 reward
    ) external {
        challengeCount++;

        challenges[challengeCount] = Challenge({
            id: challengeCount,
            challengeHash: challengeHash,
            reward: reward,
            active: true
        });

        emit ChallengeCreated(
            challengeCount,
            challengeHash,
            reward
        );
    }

    function solveChallenge(
        uint256 challengeId,
        bytes32 proof
    ) external {
        Challenge memory challenge = challenges[challengeId];

        require(challenge.active, "Challenge inactive");
        require(!solved[msg.sender][challengeId], "Already solved");

        require(
            proof == challenge.challengeHash,
            "Invalid proof"
        );

        solved[msg.sender][challengeId] = true;
        scores[msg.sender] += challenge.reward;

        emit ChallengeSolved(
            msg.sender,
            challengeId,
            challenge.reward
        );
    }
}
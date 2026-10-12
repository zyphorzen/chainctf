// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {CTFPlatform} from "../src/CTFPlatform.sol";

contract CTFPlatformInvariantTest is Test {
    CTFPlatform public platform;
    CTFHandler public handler;

    function setUp() public {
        uint256 verifierPrivateKey = 0xA11CE;
        address verifier = vm.addr(verifierPrivateKey);

        platform = new CTFPlatform(address(this), verifier);

        platform.createChallenge(100);
        platform.createChallenge(200);

        handler = new CTFHandler(platform, verifierPrivateKey);

        platform.transferOwnership(address(handler));

        targetContract(address(handler));
    }

    function invariant_ScoreMatchesExpectedRewards() public view {
        assertEq(
            platform.scores(handler.player()),
            handler.ghost_expectedScore()
        );
    }

    function invariant_ChallengeCountNeverDecreases() public view {
        assertGe(
            platform.challengeCount(),
            handler.initialChallengeCount()
        );
    }

    function invariant_SolvedRemainsSolved() public view {
        address player = handler.player();
        uint256 count = platform.challengeCount();
        for (uint256 i = 1; i <= count; i++) {
            if (handler.ghost_hasSolved(i)) {
                assertTrue(platform.solved(player, i));
            }
        }
    }
}

contract CTFHandler is Test {
    CTFPlatform public platform;
    uint256 private verifierPrivateKey;
    address public verifier;
    address public player = address(0xCAFE);

    uint256 public initialChallengeCount;
    uint256 public ghost_expectedScore;
    mapping(uint256 => bool) public ghost_hasSolved;
    mapping(uint256 => bool) public ghost_usedNonces;

    uint256 private nextNonce = 1;

    constructor(CTFPlatform _platform, uint256 _verifierPrivateKey) {
        platform = _platform;
        verifierPrivateKey = _verifierPrivateKey;
        verifier = vm.addr(_verifierPrivateKey);
        initialChallengeCount = _platform.challengeCount();
    }

    function createChallenge(uint256 reward) external {
        reward = bound(reward, 1, 10_000);
        platform.createChallenge(reward);
    }

    function setChallengeStatus(uint256 challengeId, bool active) external {
        uint256 count = platform.challengeCount();
        if (count == 0) return;
        challengeId = bound(challengeId, 1, count);
        platform.setChallengeStatus(challengeId, active);
    }

    function submitAchievement(uint256 challengeId) external {
        uint256 count = platform.challengeCount();
        if (count == 0) return;
        challengeId = bound(challengeId, 1, count);

        (, uint256 reward, bool active) = platform.challenges(challengeId);

        if (!active || platform.solved(player, challengeId)) {
            return;
        }

        uint256 nonce = nextNonce++;
        uint256 deadline = block.timestamp + 1 hours;

        CTFPlatform.Achievement memory achievement = CTFPlatform.Achievement({
            player: player,
            challengeId: challengeId,
            nonce: nonce,
            deadline: deadline
        });

        bytes32 digest = platform.getAchievementHash(achievement);
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(verifierPrivateKey, digest);
        bytes memory signature = abi.encodePacked(r, s, v);

        vm.prank(player);
        platform.submitAchievement(achievement, signature);

        ghost_expectedScore += reward;
        ghost_hasSolved[challengeId] = true;
        ghost_usedNonces[nonce] = true;
    }
}

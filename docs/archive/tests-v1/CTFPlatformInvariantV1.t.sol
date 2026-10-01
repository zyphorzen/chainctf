// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {CTFPlatform} from "../src/CTFPlatform.sol";

contract CTFPlatformInvariantTest is Test {
    CTFPlatform public platform;
    CTFHandler public handler;

    address player = address(0xCAFE);
    uint256 initialChallengeCount;

    function setUp() public {
        platform = new CTFPlatform(address(this));
        platform.createChallenge(keccak256("challenge-1"), 100);
        platform.createChallenge(keccak256("challenge-2"), 200);
        initialChallengeCount = platform.challengeCount();
        handler = new CTFHandler(platform, player);

        targetContract(address(handler));
    }

    function invariantScoreMatchesSuccessfulSolves() public view {
        assertEq(platform.scores(player), handler.expectedScore());
    }

    function invariantChallengeCountNeverDecreases() public view {
        assertGe(platform.challengeCount(), initialChallengeCount);
    }

    function invariantSolvedChallengeRemainsSolved() public view {
        bool solvedBefore = platform.solved(player, 1);

        if (solvedBefore) {
            assertTrue(platform.solved(player, 1));
        }
    }

    function invariantScoreNeverExceedsPossibleMaximum() public view {
        uint256 score = platform.scores(player);
        uint256 maximumScore = 300;

        assertLe(score, maximumScore);
    }
}

contract CTFHandler is Test {
    CTFPlatform public platform;
    address public player;

    uint256 public successfulSolves;
    uint256 public expectedScore;

    constructor(CTFPlatform _platform, address _player) {
        platform = _platform;
        player = _player;
    }

    function solveChallenge(uint256 challengeId) external {
        if (challengeId == 0) {
            return;
        }

        if (challengeId > platform.challengeCount()) {
            return;
        }

        (, bytes32 challengeHash, uint256 reward, bool active) = platform.challenges(challengeId);

        if (!active) {
            return;
        }

        if (platform.solved(player, challengeId)) {
            return;
        }

        vm.prank(player);
        platform.solveChallenge(challengeId, challengeHash);

        successfulSolves++;
        expectedScore += reward;
    }
}

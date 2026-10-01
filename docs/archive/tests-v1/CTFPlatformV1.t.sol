// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {CTFPlatform} from "../src/CTFPlatform.sol";

contract CTFPlatformTest is Test {
    CTFPlatform public platform;

    address player = address(1);

    function setUp() public {
        platform = new CTFPlatform(address(this));
    }

    function testCreateChallenge() public {
        bytes32 hash = keccak256(abi.encodePacked("challenge-1"));

        platform.createChallenge(hash, 100);
        assertEq(platform.challengeCount(), 1);

        (uint256 id, bytes32 challengeHash, uint256 reward, bool active) = platform.challenges(1);

        assertEq(id, 1);
        assertEq(challengeHash, hash);
        assertEq(reward, 100);
        assertTrue(active);
    }

    function testSolveChallenge() public {
        bytes32 hash = keccak256(abi.encodePacked("challenge-1"));

        platform.createChallenge(hash, 100);
        vm.prank(player);
        platform.solveChallenge(1, hash);

        assertTrue(platform.solved(player, 1));

        assertEq(platform.scores(player), 100);
    }

    function testCannotSolveTwice() public {
        bytes32 hash = keccak256(abi.encodePacked("challenge-1"));

        platform.createChallenge(hash, 100);
        vm.startPrank(player);
        platform.solveChallenge(1, hash);

        vm.expectRevert(CTFPlatform.ChallengeAlreadySolved.selector);

        platform.solveChallenge(1, hash);
        vm.stopPrank();
    }

    function testInvalidProof() public {
        bytes32 hash = keccak256(abi.encodePacked("challenge-1"));

        bytes32 wrongProof = keccak256(abi.encodePacked("wrong"));

        platform.createChallenge(hash, 100);
        vm.prank(player);
        vm.expectRevert(CTFPlatform.InvalidProof.selector);

        platform.solveChallenge(1, wrongProof);
    }
}

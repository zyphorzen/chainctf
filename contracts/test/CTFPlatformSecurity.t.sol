// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {CTFPlatform} from "../src/CTFPlatform.sol";

contract CTFPlatformSecurityTest is Test {
    CTFPlatform public platform;

    address owner = address(this);
    address attacker = address(0xBEEF);
    address player = address(0xCAFE);

    function setUp() public {
        platform = new CTFPlatform(owner);
    }

    function testOnlyOwnerCanCreateChallenge() public {
        vm.prank(attacker);
        vm.expectRevert();

        platform.createChallenge(keccak256("secret"), 100);
    }

    function testOnlyOwnerCanChangeStatus() public {
        platform.createChallenge(keccak256("secret"), 100);

        vm.prank(attacker);
        vm.expectRevert();

        platform.setChallengeStatus(1, false);
    }

    function testCannotSolveInactiveChallenge() public {
        bytes32 hash = keccak256("secret");

        platform.createChallenge(hash, 100);

        platform.setChallengeStatus(1, false);

        vm.prank(player);
        vm.expectRevert(CTFPlatform.ChallengeInactive.selector);

        platform.solveChallenge(1, hash);
    }

    function testCannotSolveUnknownChallenge() public {
        vm.prank(player);

        vm.expectRevert(CTFPlatform.ChallengeNotFound.selector);

        platform.solveChallenge(999, keccak256("secret"));
    }

    function testCannotSolveSameChallengeTwice() public {
        bytes32 hash = keccak256("secret");

        platform.createChallenge(hash, 100);

        vm.startPrank(player);
        platform.solveChallenge(1, hash);

        vm.expectRevert(CTFPlatform.ChallengeAlreadySolved.selector);

        platform.solveChallenge(1, hash);
        vm.stopPrank();
    }

    function testWrongProofDoesNotIncreaseScore() public {
        bytes32 correctHash = keccak256("correct");
        bytes32 wrongHash = keccak256("wrong");

        platform.createChallenge(correctHash, 100);

        vm.prank(player);

        vm.expectRevert(CTFPlatform.InvalidProof.selector);

        platform.solveChallenge(1, wrongHash);

        assertEq(platform.scores(player), 0);

        assertFalse(platform.solved(player, 1));
    }
}

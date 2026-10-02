// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {CTFPlatform} from "../src/CTFPlatform.sol";

contract CTFPlatformV2Test is Test {
    constructor(
        address initialOwner,
        address initialVerifier
    ) CTFPlatform(initialOwner, initialVerifier) {}

    function hashTypedData(bytes32 structHash) external view returns (bytes32) {
        return _hashTypedDataV4(structHash);
    }

    CTFPlatform public platform;

    uint256 verifierPrivateKey = 0xA11CE;
    address verifier;

    address player = address(0xCAFE);
    address attacker = address(0xBEEF);

    uint256 constant REWARD = 100;
    uint256 constant NONCE = 1;

    function setUp() public {
        verifier = vm.addr(verifierPrivateKey);
        platform = new CTFPlatform(address(this), verifier);
        platform.createChallenge(REWARD);
    }

    function _createAchievement(
        address achievementPlayer,
        uint256 challengeId,
        uint256 nonce,
        uint256 deadline
    ) internal pure returns (CTFPlatform.Achievement memory) {
        return
            CTFPlatform.Achievement({
                player: achievementPlayer,
                challengeId: challengeId,
                nonce: nonce,
                deadline: deadline
            });
    }

    function _signAchievement(
        CTFPlatform.Achievement memory achievement,
        uint256 privateKey
    ) internal view returns (bytes memory signature) {
        bytes32 typeHash = keccak256(
            "Achievement(address player,uint256 challengeId,uint256 nonce,uint256 deadline)"
        );

        bytes32 structHash = keccak256(
            abi.encode(
                typeHash,
                achievement.player,
                achievement.challengeId,
                achievement.nonce,
                achievement.deadline
            )
        );

        bytes32 digest = keccak256(
            abi.encodePacked(
                "\x19\x01",
                platform.DOMAIN_SEPARATOR(),
                structHash
            )
        );

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(privateKey, digest);

        return abi.encodePacked(r, s, v);
    }

    function testValidAchievement() public {
        uint256 deadline = block.timestamp + 1 hours;

        CTFPlatform.Achievement memory achievement = _createAchievement(
            player,
            1,
            NONCE,
            deadline
        );

        bytes memory signature = _signAchievement(
            achievement,
            verifierPrivateKey
        );

        vm.prank(player);
        platform.submitAchievement(achievement, signature);

        assertTrue(platform.solved(player, 1));

        assertEq(platform.scores(player), REWARD);
    }

    function testCannotUseWrongVerifier() public {
        uint256 deadline = block.timestamp + 1 hours;

        CTFPlatform.Achievement memory achievement = _createAchievement(
            player,
            1,
            NONCE,
            deadline
        );

        uint256 attackerPrivateKey = 0xBEEF;

        bytes memory signature = _signAchievement(
            achievement,
            attackerPrivateKey
        );

        vm.prank(player);
        vm.expectRevert(CTFPlatform.InvalidSignature.selector);

        platform.submitAchievement(achievement, signature);
    }

    function testCannotSubmitForAnotherPlayer() public {
        uint256 deadline = block.timestamp + 1 hours;

        CTFPlatform.Achievement memory achievement = _createAchievement(
            player,
            1,
            NONCE,
            deadline
        );

        bytes memory signature = _signAchievement(
            achievement,
            verifierPrivateKey
        );

        vm.prank(attacker);
        vm.expectRevert(CTFPlatform.InvalidSignature.selector);

        platform.submitAchievement(achievement, signature);
    }

    function testCannotUseExpiredAuthorization() public {
        uint256 deadline = block.timestamp + 1 hours;

        CTFPlatform.Achievement memory achievement = _createAchievement(
            player,
            1,
            NONCE,
            deadline
        );

        bytes memory signature = _signAchievement(
            achievement,
            verifierPrivateKey
        );

        vm.warp(deadline + 1);

        vm.prank(player);
        vm.expectRevert(CTFPlatform.AuthorizationExpired.selector);

        platform.submitAchievement(achievement, signature);
    }

    function testCannotReplayNonce() public {
        uint256 deadline = block.timestamp + 1 hours;

        CTFPlatform.Achievement memory achievement = _createAchievement(
            player,
            1,
            NONCE,
            deadline
        );

        bytes memory signature = _signAchievement(
            achievement,
            verifierPrivateKey
        );

        vm.startPrank(player);

        platform.submitAchievement(achievement, signature);

        CTFPlatform.Achievement memory secondAchievement = _createAchievement(
            player,
            2,
            NONCE,
            deadline
        );

        bytes memory secondSignature = _signAchievement(
            secondAchievement,
            verifierPrivateKey
        );

        vm.expectRevert(CTFPlatform.NonceAlreadyUsed.selector);

        platform.submitAchievement(secondAchievement, secondSignature);

        vm.stopPrank();
    }

    function testCannotSolveSameChallengeTwice() public {
        uint256 deadline = block.timestamp + 1 hours;

        CTFPlatform.Achievement memory achievement = _createAchievement(
            player,
            1,
            NONCE,
            deadline
        );

        bytes memory signature = _signAchievement(
            achievement,
            verifierPrivateKey
        );

        vm.startPrank(player);

        platform.submitAchievement(achievement, signature);

        CTFPlatform.Achievement memory replay = _createAchievement(
            player,
            1,
            2,
            deadline
        );

        bytes memory replaySignature = _signAchievement(
            replay,
            verifierPrivateKey
        );

        vm.expectRevert(CTFPlatform.ChallengeAlreadySolved.selector);

        platform.submitAchievement(replay, replaySignature);

        vm.stopPrank();
    }

    function testCannotSolveInactiveChallenge() public {
        platform.setChallengeStatus(1, false);

        uint256 deadline = block.timestamp + 1 hours;

        CTFPlatform.Achievement memory achievement = _createAchievement(
            player,
            1,
            NONCE,
            deadline
        );

        bytes memory signature = _signAchievement(
            achievement,
            verifierPrivateKey
        );

        vm.prank(player);
        vm.expectRevert(CTFPlatform.ChallengeInactive.selector);

        platform.submitAchievement(achievement, signature);
    }

    function testCannotSolveUnknownChallenge() public {
        uint256 deadline = block.timestamp + 1 hours;

        CTFPlatform.Achievement memory achievement = _createAchievement(
            player,
            999,
            NONCE,
            deadline
        );

        bytes memory signature = _signAchievement(
            achievement,
            verifierPrivateKey
        );

        vm.prank(player);
        vm.expectRevert(CTFPlatform.ChallengeNotFound.selector);

        platform.submitAchievement(achievement, signature);
    }

    function testSetVerifier() public {
        uint256 newVerifierPrivateKey = 0x12345;
        address newVerifier = vm.addr(newVerifierPrivateKey);

        platform.setVerifier(newVerifier);

        assertEq(platform.verifier(), newVerifier);
    }

    function testCannotSetZeroVerifier() public {
        vm.expectRevert(CTFPlatform.ZeroAddress.selector);

        platform.setVerifier(address(0));
    }

    function testOnlyOwnerCanSetVerifier() public {
        vm.prank(attacker);

        vm.expectRevert();

        platform.setVerifier(attacker);
    }
}

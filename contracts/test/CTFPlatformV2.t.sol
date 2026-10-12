// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Test} from "forge-std/Test.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {CTFPlatform} from "../src/CTFPlatform.sol";

contract CTFPlatformV2Test is Test {
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
        bytes32 digest = platform.getAchievementHash(achievement);
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
        vm.expectRevert(CTFPlatform.InvalidPlayer.selector);

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

    function testConstructorRevertsOnZeroOwner() public {
        vm.expectRevert(
            abi.encodeWithSelector(
                Ownable.OwnableInvalidOwner.selector,
                address(0)
            )
        );
        new CTFPlatform(address(0), verifier);
    }

    function testConstructorRevertsOnZeroVerifier() public {
        vm.expectRevert(CTFPlatform.ZeroAddress.selector);
        new CTFPlatform(address(this), address(0));
    }

    function testOnlyOwnerCanCreateChallenge() public {
        vm.prank(attacker);
        vm.expectRevert(
            abi.encodeWithSelector(
                Ownable.OwnableUnauthorizedAccount.selector,
                attacker
            )
        );
        platform.createChallenge(100);
    }

    function testOnlyOwnerCanSetChallengeStatus() public {
        vm.prank(attacker);
        vm.expectRevert(
            abi.encodeWithSelector(
                Ownable.OwnableUnauthorizedAccount.selector,
                attacker
            )
        );
        platform.setChallengeStatus(1, false);
    }

    function testChallengeStatusChangeNotFound() public {
        vm.expectRevert(CTFPlatform.ChallengeNotFound.selector);
        platform.setChallengeStatus(999, false);
    }

    function testChallengeCreatedEvent() public {
        vm.expectEmit(true, false, false, true);
        emit ChallengeCreated(3, 250);
        platform.createChallenge(250);
    }

    function testChallengeStatusChangedEvent() public {
        vm.expectEmit(true, false, false, true);
        emit ChallengeStatusChanged(1, false);
        platform.setChallengeStatus(1, false);
    }

    function testVerifierChangedEvent() public {
        address newVerifier = vm.addr(0x999);
        vm.expectEmit(true, true, false, false);
        emit VerifierChanged(verifier, newVerifier);
        platform.setVerifier(newVerifier);
    }

    function testChallengeSolvedEvent() public {
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

        vm.expectEmit(true, true, false, true);
        emit ChallengeSolved(player, 1, REWARD);

        vm.prank(player);
        platform.submitAchievement(achievement, signature);
    }

    function testScoreDoesNotChangeOnFailedSubmission() public {
        uint256 scoreBefore = platform.scores(player);

        uint256 deadline = block.timestamp + 1 hours;
        CTFPlatform.Achievement memory achievement = _createAchievement(
            player,
            1,
            NONCE,
            deadline
        );
        bytes memory badSignature = _signAchievement(achievement, 0xBAD);

        vm.prank(player);
        vm.expectRevert(CTFPlatform.InvalidSignature.selector);
        platform.submitAchievement(achievement, badSignature);

        assertEq(platform.scores(player), scoreBefore);
        assertFalse(platform.solved(player, 1));
        assertFalse(platform.usedNonces(player, NONCE));
    }

    function testCannotSubmitWithZeroPlayerAddress() public {
        uint256 deadline = block.timestamp + 1 hours;
        CTFPlatform.Achievement memory achievement = _createAchievement(
            address(0),
            1,
            NONCE,
            deadline
        );
        bytes memory signature = _signAchievement(
            achievement,
            verifierPrivateKey
        );

        vm.prank(address(0));
        vm.expectRevert(CTFPlatform.InvalidPlayer.selector);
        platform.submitAchievement(achievement, signature);
    }

    function testCannotSubmitMalformedSignature() public {
        uint256 deadline = block.timestamp + 1 hours;
        CTFPlatform.Achievement memory achievement = _createAchievement(
            player,
            1,
            NONCE,
            deadline
        );
        bytes memory malformedSig = hex"123456";

        vm.prank(player);
        vm.expectRevert();
        platform.submitAchievement(achievement, malformedSig);
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

        vm.expectRevert(
            abi.encodeWithSelector(
                Ownable.OwnableUnauthorizedAccount.selector,
                attacker
            )
        );

        platform.setVerifier(attacker);
    }

    function testFuzzCreateChallenge(uint256 reward) public {
        uint256 countBefore = platform.challengeCount();
        platform.createChallenge(reward);

        assertEq(platform.challengeCount(), countBefore + 1);
        (uint256 id, uint256 storedReward, bool active) = platform.challenges(
            countBefore + 1
        );
        assertEq(id, countBefore + 1);
        assertEq(storedReward, reward);
        assertTrue(active);
    }

    function testFuzzValidAchievement(
        address randomPlayer,
        uint256 nonce
    ) public {
        vm.assume(randomPlayer != address(0));

        uint256 deadline = block.timestamp + 1 hours;
        CTFPlatform.Achievement memory achievement = _createAchievement(
            randomPlayer,
            1,
            nonce,
            deadline
        );

        bytes memory signature = _signAchievement(
            achievement,
            verifierPrivateKey
        );

        vm.prank(randomPlayer);
        platform.submitAchievement(achievement, signature);

        assertTrue(platform.solved(randomPlayer, 1));
        assertEq(platform.scores(randomPlayer), REWARD);
        assertTrue(platform.usedNonces(randomPlayer, nonce));
    }

    function testFuzzCannotUseExpiredDeadline(uint256 elapsed) public {
        vm.assume(elapsed > 0 && elapsed < 365 days);
        uint256 deadline = block.timestamp + 100;

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

        vm.warp(deadline + elapsed);

        vm.prank(player);
        vm.expectRevert(CTFPlatform.AuthorizationExpired.selector);
        platform.submitAchievement(achievement, signature);
    }

    function testFuzzCannotSubmitForAnotherPlayer(
        address randomPlayer,
        address submitter
    ) public {
        vm.assume(randomPlayer != address(0));
        vm.assume(submitter != address(0));
        vm.assume(randomPlayer != submitter);

        uint256 deadline = block.timestamp + 1 hours;
        CTFPlatform.Achievement memory achievement = _createAchievement(
            randomPlayer,
            1,
            NONCE,
            deadline
        );

        bytes memory signature = _signAchievement(
            achievement,
            verifierPrivateKey
        );

        vm.prank(submitter);
        vm.expectRevert(CTFPlatform.InvalidPlayer.selector);
        platform.submitAchievement(achievement, signature);
    }
}

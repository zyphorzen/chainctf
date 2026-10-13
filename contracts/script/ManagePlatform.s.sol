// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Script} from "forge-std/Script.sol";
import {console2} from "forge-std/console2.sol";
import {CTFPlatform} from "../src/CTFPlatform.sol";

contract ManagePlatform is Script {
    function createChallenge(address platformAddress, uint256 reward) external {
        uint256 deployerKey = vm.envOr("DEPLOYER_PRIVATE_KEY", uint256(0));

        if (deployerKey != 0) {
            vm.startBroadcast(deployerKey);
        } else {
            vm.startBroadcast();
        }

        CTFPlatform platform = CTFPlatform(platformAddress);
        platform.createChallenge(reward);

        vm.stopBroadcast();

        uint256 currentCount = platform.challengeCount();
        console2.log(
            "Created challenge ID:",
            currentCount,
            "with reward:",
            reward
        );
    }

    function setChallengeStatus(
        address platformAddress,
        uint256 challengeId,
        bool active
    ) external {
        uint256 deployerKey = vm.envOr("DEPLOYER_PRIVATE_KEY", uint256(0));

        if (deployerKey != 0) {
            vm.startBroadcast(deployerKey);
        } else {
            vm.startBroadcast();
        }

        CTFPlatform platform = CTFPlatform(platformAddress);
        platform.setChallengeStatus(challengeId, active);

        vm.stopBroadcast();

        console2.log(
            "Set challenge ID:",
            challengeId,
            "active status to:",
            active
        );
    }

    function setVerifier(
        address platformAddress,
        address newVerifier
    ) external {
        uint256 deployerKey = vm.envOr("DEPLOYER_PRIVATE_KEY", uint256(0));

        if (deployerKey != 0) {
            vm.startBroadcast(deployerKey);
        } else {
            vm.startBroadcast();
        }

        CTFPlatform platform = CTFPlatform(platformAddress);
        platform.setVerifier(newVerifier);

        vm.stopBroadcast();

        console2.log("Updated verifier to:", newVerifier);
    }
}

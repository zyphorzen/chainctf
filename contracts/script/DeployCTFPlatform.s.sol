// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {Script} from "forge-std/Script.sol";
import {console2} from "forge-std/console2.sol";
import {CTFPlatform} from "../src/CTFPlatform.sol";

contract DeployCTFPlatform is Script {
    function run() external returns (CTFPlatform platform) {
        uint256 deployerKey = vm.envOr("DEPLOYER_PRIVATE_KEY", uint256(0));
        address verifier = vm.envOr("VERIFIER_ADDRESS", address(0));

        address deployer;
        if (deployerKey != 0) {
            deployer = vm.addr(deployerKey);
        } else {
            deployer = msg.sender;
        }

        if (verifier == address(0) && block.chainid == 31337) {
            uint256 defaultVerifierKey = 0xA11CE;
            verifier = vm.addr(defaultVerifierKey);
            console2.log(
                "Local Anvil detected: using default test verifier",
                verifier
            );
        }

        require(
            verifier != address(0),
            "DeployCTFPlatform: VERIFIER_ADDRESS must be set"
        );

        console2.log("=== ChainCTF Deployment ===");
        console2.log("Chain ID:       ", block.chainid);
        console2.log("Deployer/Owner: ", deployer);
        console2.log("Verifier:       ", verifier);

        if (deployerKey != 0) {
            vm.startBroadcast(deployerKey);
        } else {
            vm.startBroadcast();
        }

        platform = new CTFPlatform(deployer, verifier);

        bool createInitial = vm.envOr(
            "CREATE_INITIAL_CHALLENGES",
            block.chainid == 31337
        );
        if (createInitial) {
            platform.createChallenge(100);
            platform.createChallenge(250);
            console2.log("Initial challenges created: 2");
        }

        vm.stopBroadcast();

        console2.log("CTFPlatform deployed at:", address(platform));
        console2.log("Domain Separator:       ");
        console2.logBytes32(platform.DOMAIN_SEPARATOR());
        console2.log("===========================");
    }
}

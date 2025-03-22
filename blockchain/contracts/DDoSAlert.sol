// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DDoSAlert {
    event MaliciousTrafficDetected(address indexed node, string ipAddress, uint256 timestamp);

    function reportAttack(string memory ipAddress) public {
        emit MaliciousTrafficDetected(msg.sender, ipAddress, block.timestamp);
    }
}
 

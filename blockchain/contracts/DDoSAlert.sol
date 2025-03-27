// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DDoSAlert {
    event MaliciousTrafficDetected(
        address indexed node,
        string ipAddress,
        string method,
        uint256 timestamp
    );

    // Function to report a detected DDoS attack
    function reportAttack(string memory ipAddress, string memory method) public {
        emit MaliciousTrafficDetected(msg.sender, ipAddress, method, block.timestamp);
    }
}

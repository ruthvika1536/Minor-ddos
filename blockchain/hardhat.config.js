/** @type import('hardhat/config').HardhatUserConfig */
require("@nomicfoundation/hardhat-toolbox"); // Combines common plugins like ethers

module.exports = {
  solidity: "0.8.18", // Match with your contract version
  networks: {
    hardhat: {},
    localhost: {
      url: "http://127.0.0.1:8545", // Ensure the local node is running
    },
  },
};

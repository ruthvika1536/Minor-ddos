const { ethers } = require("hardhat");

async function main() {
    const DDoSAlert = await ethers.getContractFactory("DDoSAlert");
    const ddosAlert = await DDoSAlert.deploy(); // Deploy contract

    await ddosAlert.waitForDeployment(); // ✅ FIX: Use `waitForDeployment()`

    console.log(`Contract deployed to: ${await ddosAlert.getAddress()}`); // ✅ FIX: Use `getAddress()`
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });

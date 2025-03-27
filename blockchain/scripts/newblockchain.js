const Web3 = require("web3").Web3;
require("dotenv").config(); // Load environment variables

const web3 = new Web3(process.env.RPC_URL); // Use RPC URL from .env

const contractABI = require("../abi/ddosAlert.json").abi; // Load ABI
const contractAddress = process.env.CONTRACT_ADDRESS; // Store contract address in .env

const account = process.env.WALLET_ADDRESS; // Your wallet address
const privateKey = process.env.PRIVATE_KEY; // Your private key

const contract = new web3.eth.Contract(contractABI, contractAddress);

// Function to report a DDoS attack (log an IP with method used)
async function reportAttack(ipAddress, method) {
    try {
        console.log(`🚨 Reporting attack from IP: ${ipAddress} using ${method.toUpperCase()}...`);
        
        const tx = contract.methods.reportAttack(ipAddress, method);
        const gas = await tx.estimateGas({ from: account });
        const gasPrice = await web3.eth.getGasPrice();
        const data = tx.encodeABI();
        const nonce = await web3.eth.getTransactionCount(account);

        const signedTx = await web3.eth.accounts.signTransaction({
            to: contractAddress,
            data,
            gas,
            gasPrice,
            nonce,
            chainId: 31337 // Hardhat local network (update for mainnet)
        }, privateKey);

        const receipt = await web3.eth.sendSignedTransaction(signedTx.rawTransaction);
        console.log(`✅ Attack reported on blockchain! Tx Hash: ${receipt.transactionHash}`);
    } catch (error) {
        console.error("❌ Error reporting attack:", error);
    }
}

// Function to fetch attack logs from the blockchain
async function getAttackLogs() {
    try {
        console.log("📡 Fetching attack logs from blockchain...");
        
        const events = await contract.getPastEvents("MaliciousTrafficDetected", {
            fromBlock: 0,
            toBlock: "latest",
        });

        console.log("🛑 Malicious Traffic Logs:");
        events.forEach((event, index) => {
            console.log(`
                Attack ${index + 1}:
                Reporter: ${event.returnValues.node}
                IP Address: ${event.returnValues.ipAddress}
                Method: ${event.returnValues.method}
                Timestamp: ${new Date(Number(event.returnValues.timestamp) * 1000)}
            `);
        });
    } catch (error) {
        console.error("❌ Error fetching logs:", error);
    }
}

// // Function to report a DDoS attack (log an IP with method used)
// async function reportAttack(ipAddress, method) {
//     try {
//         console.log(`🚨 Reporting attack from IP: ${ipAddress} using ${method.toUpperCase()}...`);

//         // Fetch existing logs
//         const existingLogs = await getAttackLogs(false); // Fetch logs without printing them
//         const loggedAttacks = existingLogs.map(event => ({
//             ip: event.returnValues.ipAddress,
//             method: event.returnValues.method
//         }));

//         // Prevent duplicate logs
//         if (loggedAttacks.some(log => log.ip === ipAddress && log.method === method)) {
//             console.log(`⏳ Attack from ${ipAddress} using ${method} already logged, skipping...`);
//             return;
//         }

//         const tx = contract.methods.reportAttack(ipAddress, method);
//         const gas = await tx.estimateGas({ from: account });
//         const gasPrice = await web3.eth.getGasPrice();
//         const data = tx.encodeABI();
//         const nonce = await web3.eth.getTransactionCount(account);

//         const signedTx = await web3.eth.accounts.signTransaction({
//             to: contractAddress,
//             data,
//             gas,
//             gasPrice,
//             nonce,
//             chainId: 31337 // Hardhat local network
//         }, privateKey);

//         const receipt = await web3.eth.sendSignedTransaction(signedTx.rawTransaction);
//         console.log(`✅ Attack reported on blockchain! Tx Hash: ${receipt.transactionHash}`);
//     } catch (error) {
//         console.error("❌ Error reporting attack:", error);
//     }
// }

// // Modify `getAttackLogs` to support silent fetching
// async function getAttackLogs(printLogs = true) {
//     try {
//         const events = await contract.getPastEvents("MaliciousTrafficDetected", {
//             fromBlock: 0,
//             toBlock: "latest",
//         });

//         if (printLogs) {
//             console.log("🛑 Malicious Traffic Logs:");
//             events.forEach((event, index) => {
//                 console.log(`
//                     Attack ${index + 1}:
//                     Reporter: ${event.returnValues.node}
//                     IP Address: ${event.returnValues.ipAddress}
//                     Method: ${event.returnValues.method}
//                     Timestamp: ${new Date(Number(event.returnValues.timestamp) * 1000)}
//                 `);
//             });
//         }

//         return events; // Return logs for checking duplicates
//     } catch (error) {
//         console.error("❌ Error fetching logs:", error);
//         return [];
//     }
// }

// Example Usage
(async () => {
    await reportAttack("192.168.1.100", "chi"); // Log attack with Chi-Square
    await reportAttack("192.168.1.101", "rl");  // Log attack with RL

    setTimeout(getAttackLogs, 5000); // Fetch logs after 5 seconds
})();

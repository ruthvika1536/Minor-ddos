import requests
import json
import os
from web3 import Web3

# Blockchain Connection
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# Construct the correct path to the ABI file
abi_path = os.path.join(os.path.dirname(__file__), "../blockchain/abi/ddosAlert.json")

# Ensure the ABI file exists before proceeding
if not os.path.exists(abi_path):
    raise FileNotFoundError(f"ABI file not found at: {abi_path}")

# Load ABI JSON file
with open(abi_path, "r") as abi_file:
    abi_data = json.load(abi_file)

# Extract ABI list
contract_abi = abi_data.get("abi")
if contract_abi is None:
    raise ValueError("Invalid ABI file format: Missing 'abi' key")

# Smart Contract Details
contract_address = "0x5FbDB2315678afecb367f032d93F642f64180aa3"  # Update with actual deployed contract address
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Sample Network Traffic Data
benign_sample = {
    "features": [[1117, 5, 2, 935, 349, 935, 187, 418.1447, 349, 174.5, 246.78027, 1149507.625, 
                  6266.786133, 186.16667, 238.60965, 624, 6, 1117, 279.25, 412.6123, 886, 6, 624, 
                  624, 0, 624, 624, 0, 124, 40, 4476.276, 1790.5103, 935, 160.5, 335.93027, 
                  112849.14, 0, 0, 183.42857, 187, 174.5, 5, 935, 2, 349, 65535, 32768, 1, 20, 
                  0, 0, 0, 0, 0, 0, 0, 0]]
}

ddos_sample = {
    "features": [[27005957, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.074057735, 27000000, 0, 27000000, 
                  27000000, 27000000, 27000000, 0, 27000000, 27000000, 0, 0, 0, 0, 0, 0, 40, 0, 
                  0.074057736, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2049, -1, 0, 20, 0, 0, 
                  0, 0, 27000000, 0, 27000000, 27000000]]
}

# Function to check traffic with Chi-Square or RL method
def check_traffic(sample_data, sample_type, method):
    print(f"\n🔍 Checking {sample_type} traffic using {method.upper()} method...")

    # Add the method type (chi or rl)
    sample_data["method"] = method

    # Send data to ML API for prediction
    try:
        response = requests.post("http://127.0.0.1:5000/predict", json=sample_data)
        response.raise_for_status()
        result = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error contacting ML API: {e}")
        return

    # Extract Predictions
    predictions = result.get("predictions", {})
    is_malicious = any("DDoS" in preds for preds in predictions.values())

    if is_malicious:
        attacker_ip = "192.168.1.100"  # Replace with actual attacker's IP
        print(f"⚠️ DDoS detected from  logging to blockchain...")

        # Log attack to blockchain with method type
        try:
            tx = contract.functions.reportAttack(attacker_ip, method).transact({'from': w3.eth.accounts[0]})
            print(f"✅ Attack logged on blockchain using {method.upper()} method: {tx.hex()}")
        except Exception as e:
            print(f"❌ Blockchain transaction failed: {e}")
    else:
        print(f"✅ No malicious activity detected for {sample_type} traffic using {method.upper()} method.")

# Run tests with both methods
for method in ["chi", "rl"]:
    check_traffic(benign_sample.copy(), "benign_sample", method)
    check_traffic(ddos_sample.copy(), "ddos_sample", method)

const { ethers } = require("ethers");

let VotingContract = null;

let ReadOnlyContract = null;

export async function get_contract(privateKey) {
  console.log("Connecting to blockchain contract...")
  if (VotingContract != null) {
    return VotingContract;
  }
  const r = await fetch('http://127.0.0.1:5000/deployed.json')
  if (!r.ok) throw new Error(`Failed to fetch contract info: ${r.statusText}`);
  const contract_info = await r.json()
  const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
  const signer = new ethers.Wallet(privateKey, provider)
  VotingContract = new ethers.Contract(contract_info.contracts.Voting.address, contract_info.contracts.Voting.abi, signer);
  console.log("Connected to blockchain contract") 
  return VotingContract   
}

export async function getReadOnlyContract() {
  console.log("Connecting to blockchain contract...")
  if (ReadOnlyContract != null) {
    return ReadOnlyContract;
  }
  const r = await fetch('http://127.0.0.1:5000/deployed.json')
  if (!r.ok) throw new Error(`Failed to fetch contract info: ${r.statusText}`);
  const contract_info = await r.json()
  const provider = new ethers.JsonRpcProvider('http://127.0.0.1:8545');
  ReadOnlyContract = new ethers.Contract(contract_info.contracts.Voting.address, contract_info.contracts.Voting.abi, provider);
  console.log("Connected to blockchain contract") 
  return ReadOnlyContract 
  
}
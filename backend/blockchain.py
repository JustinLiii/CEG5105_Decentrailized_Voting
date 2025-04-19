import json
from web3 import Web3

NETWORK_ENDPOINT = "http://127.0.0.1:8545"
w3 = Web3(Web3.HTTPProvider(NETWORK_ENDPOINT))
FUNDER_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
FUNDER_PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"

# def get_txn_gas(sender_address: str) -> int:
#     with open('deployed.json', 'r') as f:
#         contract_info = json.load(f)
#     contract = w3.eth.contract(
#         address=contract_info["contracts"]["Voting"]["address"],
#         abi=contract_info["contracts"]["Voting"]["abi"])
#     tx_for_estimate = {
#         'from': FUNDER_ADDRESS,
#         'value': 0,
#         'nonce': w3.eth.get_transaction_count(sender_address),
#     }
#     tx = contract.functions.vote(0).build_transaction(tx_for_estimate)['data'],
#     gas_estimate = contract.functions.vote(0).estimate_gas(tx)
#     gas_price = w3.eth.gas_price
#     print(f"Estimated ETH {w3.from_wei(gas_estimate * gas_price, 'ether')}")
#     return gas_estimate

def fund_account(address: str, eth: float):
    nonce = w3.eth.get_transaction_count(FUNDER_ADDRESS)
    gas_price = w3.eth.gas_price
    tx_fund = {
        'nonce': nonce,
        'to': address,
        'value': w3.to_wei(eth, 'ether'),
        'gas': 21000,
        'gasPrice': gas_price,
    }
    signed_tx = w3.eth.account.sign_transaction(tx_fund, private_key=FUNDER_PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    w3.eth.wait_for_transaction_receipt(tx_hash)

def create_account(fund = False)-> tuple[str, str]:
    """
    Create a new Ethereum account.
    """
    # Generate a new Ethereum account
    new_acct = w3.eth.account.create()
    fund_account(new_acct.address, 0.1)
    return new_acct.address, Web3.to_hex(new_acct.key)

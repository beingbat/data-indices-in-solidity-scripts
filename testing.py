import json
from web3 import Web3
import math


def main():
	ganache_url = "HTTP://127.0.0.1:7545"
	web3 = Web3(Web3.HTTPProvider(ganache_url))
	web3.eth.defaultAccount = web3.eth.accounts[0]
	contractaddress = web3.toChecksumAddress("0x8C83d90992Cb8c895A79Bed870E9fc99f5B71192")

	for i in [70292108274454579516851078175790635428763821352185596109038418929799371042574,
	          70292108274454579516851078175790635428763821352185596109038418929799371042575]:

		value = web3.toInt(web3.eth.getStorageAt(contractaddress, i))
		sk = web3.toInt(web3.solidityKeccak(['uint256'], [i]))
		hashdata = web3.toInt(web3.eth.getStorageAt(contractaddress, sk))

		print(f"\n\nIndex:\t\t\t\t\t\t\t{hex(i)}.")
		print(f"Storage Value:\t\t\t\t\t\t\t{web3.toBytes(value)}")
		print(f"Storage Value:\t\t\t\t\t\t\t{web3.toHex(value)}")
		print(f"Solidity Keccake of current index:\t\t{web3.toHex(sk)}")
		print(f"Solidity Keccake Hash Contents:\t\t\t{hex(hashdata)}")


if __name__ == "__main__":
	main()

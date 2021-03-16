# solidity-indices
Returns the indices (and byte numbers) of all state variables in a contract, Given a solidity contract's source code and a running contract over a EVM. (Python)

Brief Introduction:
I am using solidity python parser by ConsenSys to convert the source solidity code into a parsed object (which looks like JSON). Link: https://github.com/ConsenSys/python-solidity-parser
Using this and the address of the deployed version of same contract on local EVM with the help Ganache and Remix are used to as inputs in calculating the indices and byte numbers for each kind of state variable declared in a contract.
Compiler version 0.4.22 is used for solidity as it is compatible with the parser used.
For solidity related operations, I've used Web3.py.

How to Run:
-> execute main_v8.py
-> notes.txt are random notes I wrote for myself. they might be helpful in navigating the solidity and parser's functionality.
-> compile the given contract on EVM and put its address in its place in the main_v8.py, also keep the contract file in the same folder as main_v8.py is in. 
-> the mentioned libraries must be installed to run the code obviously.

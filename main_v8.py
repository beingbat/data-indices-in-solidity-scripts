from web3 import Web3
from solidity_parser import parser
import pprint
import math

# TODO: Merge Fixed, Dynamic arrays and allow for complex types: Done Partially
# web3: Used for EVM talking to EVM and hashing
# solidity_parser, pprint used for parsing the contract code

# This is the information required for connecting to the EVM because we want to know the indices of dynamic elements
ganache_url = "HTTP://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
contractaddress = web3.toChecksumAddress("0x8C83d90992Cb8c895A79Bed870E9fc99f5B71192")

# Following are 4 global variables, first is the parsed contract object, globally declared so it can be accessed from
# every function

currentcontractobject = None
spaces = "\t"                   # For adding spaces to printed data with universal uniformity
arraysizes = []                 # Used in arrays as arrays use recursion so a global data structure is used to record
# meta data for arrays
metaarray = []                  # This array contains all the information regarding the indices of the given contract


# To convert hex string into ascii characters for readibility
def hexstringtoasciistring(value):
	value = str(value)[2:]  # truncate the '0x' part of hex string
	i = 0
	for i in range(0, len(value), 2):
		if value[i] == '0' and value[i + 1] == '0':     # check if hex string has ended by detecting two consective 0s
			break
	value = value[:-len(value) + i]
	bytes_object = bytes.fromhex(value)
	return bytes_object.decode("ASCII")


#   All the following functions encompass the complete logic of caluclating the indices of variables, any variable or
#   type unknown or unhandled is raised an exception so we know that code did not understand something while
#   reading the contract

#   Data Types Handled: bools, int, uint, address, byte, bytes, string. Fixed/uFixed types do not compile on the
#   parser compatible compiler so not handled.

#   This calculates properties of single variables, bytes and strings are dynamically sized, Other types have
#   predefined sizes, So, for strings and bytes we could use the information given in the parser which is the initial
#   length of the string/byte. Instead I use a running contract to caluclate its length by finding the contents of
#   the corresponding index and by observing its contents
def elementaryvariables(statevariable, variable_type, storage_index, byte_index):

	print(f"\n\n{spaces}Variable Type:\t{variable_type}")
	hashvalue = 0
	start_index = -1
	end_index = -1
	varprops = []

	if variable_type == 'bool':  # Finding Boolean
		if byte_index < 32:
			byte_index += 1
		else:
			storage_index += 1
			byte_index = 1
		variable_size = 1

	elif variable_type[:3] == 'int' or variable_type[:4] == 'uint':  # Integers

		variable_size = variable_type[3:]
		if variable_type[:4] == 'uint':
			variable_size = variable_type[4:]
		if variable_size == "":
			variable_size = 256
		else:
			variable_size = int(variable_size)

		variable_size = round(variable_size / 8)

		if byte_index + variable_size <= 32:
			byte_index += variable_size
		elif byte_index + variable_size > 32:
			storage_index += 1
			byte_index = variable_size

	elif variable_type == 'address':  # addresses
		variable_size = 20

		if byte_index + variable_size <= 32:
			byte_index += variable_size
		elif byte_index + variable_size > 32:
			storage_index += 1
			byte_index = variable_size

	elif variable_type[:4] == 'byte' and variable_type != 'bytes':  # bytes is shorthand for byte[]
		variable_size = variable_type[4:]
		if variable_size == "":
			variable_size = 1
		else:
			variable_size = variable_size[1:]
			variable_size = int(variable_size)

		if byte_index + variable_size <= 32:
			byte_index += variable_size
		elif byte_index + variable_size > 32:
			storage_index += 1
			byte_index = variable_size

	elif variable_type == 'bytes' or variable_type == 'string':
		if byte_index != 0:
			storage_index += 1
			byte_index = 0

		start_index = storage_index
		end_index = storage_index
		indexvalue = web3.toInt(web3.eth.getStorageAt(contractaddress, start_index))
		hashed = web3.toInt(web3.solidityKeccak(['uint256'], [start_index]))
		hashvalue = web3.toInt(web3.eth.getStorageAt(contractaddress, hashed))
		if hashvalue == 0:
			variable_size = len(hexstringtoasciistring(web3.toHex(web3.eth.getStorageAt(contractaddress, start_index))))
		else:
			stringsize = math.ceil(indexvalue / 2)
			indices_r = math.ceil(stringsize / 32) - 1
			start_index = web3.toInt(web3.solidityKeccak(['uint256'], [storage_index]))
			end_index = start_index
			end_index += indices_r
			variable_size = indexvalue
		byte_index += variable_size

	else:
		raise ValueError("The Elementary Variable Type is not known. Type: " + variable_type)
		return storage_index, byte_index

	if hashvalue == 0:
		print(f"{spaces}Index:\t\t\t{storage_index}\n{spaces}Starting Byte:\t{byte_index - variable_size}\n"
		      f"{spaces}Size:\t\t\t{variable_size} Byte")
		varprops.append(storage_index)
		varprops.append(str(byte_index - variable_size) + " to " + str(byte_index))
		varprops.append(variable_size)
	else:
		print(f"{spaces}Index from (hash of {storage_index}):\n{spaces}{hex(start_index)} to\n"
		      f"{spaces}\t\t\t\t\t\t\t{hex(end_index)}\n{spaces}Size:\t\t\t{variable_size} Bytes")

		varprops.append(str(hex(start_index)) + " to " + str(hex(end_index)))
		varprops.append(None)
		varprops.append(variable_size)

	# Check this...
	if variable_type == 'bytes' or variable_type == 'string':
		storage_index += 1
		byte_index = 0

	return storage_index, byte_index, varprops


#   ------------------------------ UserDefined Types Start --------------------------------


#   Variable Types Handled: ArrayType, Mappings, Elementary Variables and User Defined (Structs and Enums)
#   These are data containers which can have above mentioned variables
def structs(statevariable, variable_type, storage_index, byte_index):
	print(f"\n\tThis is a struct with following Items:")
	if byte_index != 0:
		storage_index += 1
	byte_index = 0

	global spaces
	varprops = []   # used for collecting data
	spaces += "\t"

	members = currentcontractobject.structs[variable_type]['members']
	structsnames = list(currentcontractobject.structs.keys())

	for member in members:
		vp = [member['typeName']['type']]
		if member['typeName']['type'] == 'ArrayTypeName':
			print(f"\n\n{spaces}\t\tName: {member['name']}")
			vp.append(member['name'])
			storage_index, byte_index, vp2 = arraytype(member, storage_index, byte_index)
			vp = vp + vp2
			varprops.append(vp)
			continue

		if member['typeName']['type'] == 'ElementaryTypeName':
			print(f"\n\n{spaces}\t\tName: {member['name']}")
			vp.append(member['name'])
			variable_type = member['typeName']['name']
			vp.append(variable_type)
			storage_index, byte_index, vp2 = elementaryvariables(statevariable, variable_type, storage_index,
			                                                     byte_index)
			vp = vp + vp2
			varprops.append(vp)
			continue

		if member['typeName']['type'] == 'UserDefinedTypeName':

			variable_type = member['typeName']['namePath']
			if variable_type in structsnames:
				print(f"\n{spaces}\t\tStruct Name: {member['name']}")
				print(f"{spaces}\t\tStruct Type: {variable_type}")
				vp.append(member['name'])
				vp.append(variable_type)

				storage_index, byte_index, vp2 = structs(member, variable_type, storage_index, byte_index)
				vp = vp+vp2
				varprops.append(vp)
				continue

			if member['typeName']['namePath'] in list(currentcontractobject.enums.keys()):
				variable_type = member['typeName']['namePath']
				vp.append(member['name'])
				vp.append(variable_type)

				storage_index, byte_index, vp2 = enums(member, variable_type, storage_index, byte_index)
				vp = vp+vp2
				varprops.append(vp)
				continue

		if member['typeName']['type'] == 'Mapping':
			keytype = member['typeName']['keyType']['name']
			if member['typeName']['valueType']['type'] == 'ElementaryTypeName':
				valuetype = member['typeName']['valueType']['name']
			else:
				valuetype = member['typeName']['valueType']['namePath']

			if byte_index != 0:
				storage_index += 1
			byte_index = 0
			print(f"{spaces}Key Type:\t\t{keytype}\n\tValue Type:\t\t"
			      f"{valuetype}\n\tIndex Assigned:\t{storage_index}")
			vp.append(str(keytype) + "=>" + str(valuetype))
			vp.append(storage_index)
			vp.append(None)
			vp.append(32)
			varprops.append(vp)
			storage_index += 1
			continue

		raise ValueError("Type of variable given in struct is not known. Type: " + variable_type)
		return storage_index, byte_index, varprops

	if byte_index != 0:
		storage_index += 1
	byte_index = 0
	spaces = spaces[:-1]

	return storage_index, byte_index, varprops


#   In solidity, a number presents Enum value, so size of enum is maximum value which could be assigned to it,
#   hence they are packed accordingly
def enums(statevariableobject, variable_type, storage_index, byte_index):

	print(f"{spaces}Enum of Type:\t{variable_type}")
	variable_size = math.ceil(len(list(currentcontractobject.enums[variable_type].members))/255)

	if byte_index + variable_size <= 32:
		byte_index += variable_size
	else:
		storage_index += 1
		byte_index = variable_size

	print(f"{spaces}Index:\t\t\t{storage_index}\n{spaces}Starting Byte:\t{byte_index}\n"
	      f"{spaces}Size:\t\t\t{variable_size} Bytes")
	varprops = [storage_index, str(byte_index) + " to " + str(byte_index+variable_size), variable_size]
	return storage_index, byte_index, varprops


#   ------------------------------ UserDefined Types End --------------------------------

#   ------------------------------ Array Types Start --------------------------------

#   As of now, we have only handled dynamic and fixed index arrays seperately and have not implemented complex arrays
#   which look like T[][X][][][Y][Z] this. The basic structure for such arrays has been written Moreover, dynamic and
#   fixed are both almost the same and are implemented using relatively same recusrion techniques. But there is still
#   some work left to bridge the gap and allow inter type arrays

#   For every type of array having size like T[x][y][z] always gets z elements packed together like they would
#   if they are defined as seperate variables. And after first z elements, we start with a brand new index,
#   in this way, if z elements use k indices, we will need total of x*y*k indices. This function contigousarray deals
#   with the case of packing z elements together and increasing the index afterwards
def contigousarray(statevariable, variable_type, storage_index, byte_index, array_size):
	global spaces
	print(f"\n{spaces}Array of Type:\t{variable_type}")
	sizes = 0
	if byte_index != 0:
		storage_index += 1
	byte_index = 0
	start_index = storage_index
	spaces += "\t"
	for i in range(array_size):
		storage_index, byte_index, vp2 = elementaryvariables(statevariable, variable_type, storage_index, byte_index)
		sizes += vp2[2]
	spaces = spaces[:-1]
	end_index = storage_index

	if variable_type != "string" and variable_type != "bytes":   # because they are packed seperately in all cases
		if byte_index != 0:     # Recent
			storage_index += 1
		byte_index = 0

	vp = []
	if start_index != end_index:
		print(f"\n{spaces}Indices:\t\tfrom {hex(start_index)} to {hex(end_index)}")
		vp.append(str(hex(start_index)) + " to " + str(hex(end_index)))
	else:
		print(f"\n{spaces}Index:\t\t{hex(start_index)}")
		vp.append(str(hex(start_index)))

	vp.append(None)
	vp.append(sizes)

	return storage_index, byte_index, vp


#   The arrays in which we know the size of array beforehand and don't need any running contract to dyamically figure
#   out the size of array based on the amount of data stored in it.
#   fixedarrays recusively calls itself until all iterations of data are complete. An easier way would be to multiply
#   indices sizes like T[X][Y][Z]: X*Y*Z and run contigous array X*Y times with loop running Z times, but the reason
#   for doing is this way is so it can support dynamic indices as well (in future)
#   As for Mappings datatype, for dynamic and fixed both, it is handled directly in the parent calling function
#   'arraytype' reason being that the requirement regarding mappings was just to find the declaring indices and not
#   worry about the keys being used so we don't need any extra work to determine indices in use.
#   The left data types which could have arrays are: Elementary Types, User Defined Types (Structs, Enums) which are
#   handled here
def fixedarrays(statevariable, variable_type, storage_index, byte_index, arraydimensions, arrayindices,
                currentdimension=0):
	global spaces
	global arraysizes

	if currentdimension >= len(arraydimensions) - 1:

		if len(arraydimensions) > 1:
			print(f"\n\n{spaces}Current Cell\t{str(arrayindices)[:-4]}]")

		if statevariable['type'] == 'ElementaryTypeName':
			storage_index, byte_index, vp = contigousarray(statevariable, variable_type, storage_index, byte_index,
			                                               arraydimensions[len(arraydimensions) - 1])
			arraysizes.append(vp)
		elif statevariable['type'] == 'UserDefinedTypeName':

			if variable_type in currentcontractobject.structs.keys():
				spaces += "\t"
				for j in range(arraydimensions[len(arraydimensions) - 1]):
					storage_index, byte_index, vp = structs(statevariable, variable_type, storage_index, byte_index)
					arraysizes.append(vp)
				spaces = spaces[:-1]

			elif statevariable['namePath'] in currentcontractobject.enums.keys():
				spaces += "\t"
				for j in range(arraydimensions[len(arraydimensions) - 1]):
					storage_index, byte_index, vp = enums(statevariable, variable_type, storage_index, byte_index)
					arraysizes.append(vp)
				spaces = spaces[:-1]
				byte_index = 0
				storage_index += 1

		return storage_index, byte_index

	for i in range(arraydimensions[currentdimension]):
		arrayindices[currentdimension] = i
		storage_index, byte_index = fixedarrays(statevariable, variable_type, storage_index, byte_index,
		                                        arraydimensions, arrayindices, currentdimension + 1)

	return storage_index, byte_index


#   We have caluclated the dimensions of the array already, the only thing we dont know is the sizes of dimensions,
#   we recursively go to index see the size, go to its hash, see the next dimensions size and so on... In this way we
#   finally land on the real elements and we count their size and indices.
def dynamicarrays(statevariable, variable_type, storage_index, byte_index, arraydimensions, noofelements,
                  currentdimension=0):

	global spaces
	global arraysizes

	if currentdimension >= len(arraydimensions) - 1:

		vp2 = []
		print(f"\n\n{spaces}Variable Count: {noofelements}")
		if statevariable['type'] == 'ElementaryTypeName':
			x, y, vp2 = contigousarray(statevariable, variable_type, storage_index, 0, noofelements)
			arraysizes.append(vp2)

		elif statevariable['type'] == 'UserDefinedTypeName':
			if variable_type in list(currentcontractobject.structs.keys()):
				spaces += "\t"
				for j in range(noofelements):
					storage_index, byte_index, vp2 = structs(statevariable, variable_type, storage_index, byte_index)
					arraysizes.append(vp2)
				spaces = spaces[:-1]
			elif variable_type in list(currentcontractobject.enums.keys()):
				spaces += "\t"
				for j in range(noofelements):
					storage_index, byte_index, vp2 = enums(statevariable, variable_type, storage_index, byte_index)
					arraysizes.append(vp2)
				spaces = spaces[:-1]
				byte_index = 0
				storage_index += 1
		return 0, 0

	for i in range(noofelements):
		newhash = web3.toInt(web3.solidityKeccak(['uint256'], [storage_index + i]))
		noofelements = web3.toInt(web3.eth.getStorageAt(contractaddress, storage_index + i))
		dynamicarrays(statevariable, variable_type, newhash, 0, arraydimensions, noofelements, currentdimension + 1)

	return storage_index, byte_index


def complexarrays(statevariable, variable_type, storage_index, byte_index, arraydimensions, a_current, noofelements,
                  currentdimension=0):

	global spaces
	global arraysizes

	if currentdimension >= len(arraydimensions):
		vp2 = []
		print(f"\n\n{spaces}Variable Count: {noofelements}")
		if statevariable['type'] == 'ElementaryTypeName':
			storage_index, byte_index, vp2 = contigousarray(statevariable, variable_type, storage_index, 0, noofelements)
			arraysizes.append(vp2)

		elif statevariable['type'] == 'UserDefinedTypeName':
			if variable_type in list(currentcontractobject.structs.keys()):
				spaces += "\t"
				for j in range(noofelements):
					storage_index, byte_index, vp2 = structs(statevariable, variable_type, storage_index, byte_index)
					arraysizes.append(vp2)
				spaces = spaces[:-1]
			elif variable_type in list(currentcontractobject.enums.keys()):
				spaces += "\t"
				for j in range(noofelements):
					storage_index, byte_index, vp2 = enums(statevariable, variable_type, storage_index, byte_index)
					arraysizes.append(vp2)
				spaces = spaces[:-1]
				byte_index = 0
				storage_index += 1
		return storage_index, byte_index

	indexr = storage_index
	for i in range(noofelements):
		a_current[currentdimension] = i
		if arraydimensions[currentdimension] is None:
			newhash = web3.toInt(web3.solidityKeccak(['uint256'], [storage_index + i]))
			noofelements = web3.toInt(web3.eth.getStorageAt(contractaddress, storage_index + i))
			complexarrays(statevariable, variable_type, newhash, 0, arraydimensions, a_current, noofelements,
			              currentdimension + 1)
			indexr += 1

		else:
			indexr, byte_index = complexarrays(statevariable, variable_type, storage_index, byte_index,
			                                          arraydimensions, a_current, arraydimensions[
				                                          currentdimension], currentdimension + 1)

	return indexr, byte_index


#   This is the main drver fucntion for the array vairable type, It observes the parser tree and notes down the sizes
#   of array dimensions and their type (dynamic or fixed) it then routes the fixed to the fixed function and dynamic
#   to dynamic, but blocks the complex ones. This function is aso responsible for directly handling the mapping type
#   without going into the fixed or dynamic functions.
def arraytype(statevariableobject, storage_index, byte_index):
	arraydimensions = []
	global spaces
	global arraysizes
	arraysizes = []
	v = []
	currenttype = statevariableobject['typeName']['baseTypeName']
	arraylength = statevariableobject['typeName']['length']
	dynamic = False
	spaces += "\t"
	if arraylength is not None:
		arraydimensions.append(int(arraylength['number']))
	else:
		arraydimensions.append(None)
		dynamic = True

	while currenttype['type'] == 'ArrayTypeName':
		arraylength = currenttype['length']
		currenttype = currenttype['baseTypeName']
		if arraylength is not None:
			arraydimensions.append(int(arraylength['number']))
		else:
			arraydimensions.append(None)
			dynamic = True

	if byte_index != 0:
		storage_index += 1
	byte_index = 0
	print(arraydimensions)
	variable_type = None
	if currenttype['type'] == 'UserDefinedTypeName':
		variable_type = currenttype['namePath']
	elif currenttype['type'] == 'ElementaryTypeName':
		variable_type = currenttype['name']

	print(f"{spaces}Type: {variable_type}")

	alldynamic = True
	for i in arraydimensions:
		if i is not None:
			alldynamic = False
			break

	if currenttype['type'] == 'Mapping':
		variable_type = 'Mapping'
		print(variable_type)
		keytype = currenttype['keyType']['name']
		if currenttype['valueType']['type'] == 'ElementaryTypeName':
			valuetype = currenttype['valueType']['name']
		else:
			valuetype = currenttype['valueType']['namePath']
		v.append("Mapping (" + str(keytype) + "=>" + str(valuetype) + ")")

		size = 1

		for i in arraydimensions:
			if i is None:
				break
			else:
				size *= i

		print(
			f"{spaces}Key Type:\t\t{keytype}\n{spaces}Value Type:\t\t{valuetype}\n{spaces}Index Assigned:\t"
			f"{storage_index} to {storage_index+size-1}")

		v.append(str(storage_index) + " to " + str(storage_index-1+size))
		v.append(None)
		v.append(None)
		storage_index += size

	elif not dynamic:
		print(f"{spaces}Fixed Array having dimensions:\t\t\t\t\t{arraydimensions}")

		v.append(variable_type)
		arrayindices = []
		if len(arraydimensions) > 1:
			for i in range(len(arraydimensions)):
				arrayindices.append(0)
		storage_index, byte_index = fixedarrays(currenttype, variable_type, storage_index, byte_index,
		                                        arraydimensions, arrayindices)
		v.append(arraysizes)

	elif alldynamic:     # only dynamic: all dimensions are none

		v.append(variable_type)
		noofelements = web3.toInt(web3.eth.getStorageAt(contractaddress, storage_index))
		hashval = web3.toInt(web3.solidityKeccak(['uint256'], [storage_index]))
		dynamicarrays(currenttype, variable_type, hashval, 0, arraydimensions, noofelements)
		v.append(arraysizes)
		# Added next two lines recently
		if byte_index != 0:
			storage_index += 1

		storage_index += 1
		byte_index = 0

	else:   # meaning complex arrays
		c_dim = arraydimensions[0]
		v.append(variable_type)
		arrayindices = []
		if len(arraydimensions) > 1:
			for i in range(len(arraydimensions)):
				arrayindices.append(0)

		if c_dim is None:
			noofelements = web3.toInt(web3.eth.getStorageAt(contractaddress, storage_index))
			hashval = web3.toInt(web3.solidityKeccak(['uint256'], [storage_index]))
			complexarrays(currenttype, variable_type, hashval, 0, arraydimensions, arrayindices, noofelements, 1)
			storage_index += 1
			byte_index = 0
		else:
			storage_index, byte_index = complexarrays(currenttype, variable_type, storage_index, byte_index,
			                                          arraydimensions, arrayindices, c_dim, 1)

		v.append(arraysizes)

		# raise ValueError("Complex Arrays are not handled (as of yet).")

	spaces = spaces[:-1]
	return storage_index, byte_index, v


#   ------------------------------ Array Types Start --------------------------------

#   This is the main driver code which first reads the source file and coverts it into a parsed object of contracts
#   using the parser library suggested by RA. Also establishes connection with EVM and the provided contract address
#   and given port number. It then iterates each contract and find the indices for each of its variables in memory.
#   This is responbile for directly calling elementary, arrays, and userdefined types functions
#   varprops, metaarray, v, v2 all of these are used for collecting data in an array data structure as per
#   requirement of project
def main():
	global currentcontractobject
	global spaces

	parsedtree = parser.parse_file("samplecontract.sol")  # Contracts written in local file
	parsedtreeobject = parser.objectify(parsedtree)
	pprint.pprint(parsedtree)
	all_contracts_names = parsedtreeobject.contracts.keys()  # get all contract names
	all_contracts_names = list(all_contracts_names)

	for contract_name in all_contracts_names:

		print(f"\n\n-------------------\tInformation of Contract: {contract_name}\t-------------------\n")
		currentcontractobject = parsedtreeobject.contracts[contract_name]
		state_variables_names = list(parsedtreeobject.contracts[contract_name].stateVars.keys())
		print(f"All State Variables Are:\n{state_variables_names}")

		global metaarray
		metaarray = []
		storage_index = 0
		byte_index = 0

		for variable_name in state_variables_names:
			print("Storage Index: " + str(storage_index))
			varprops = []
			print(f"\n\n{spaces}Properties of a Variable:\n\n{spaces}Name:\t\t\t{variable_name}")
			statevariableobject = parsedtreeobject.contracts[contract_name].stateVars[variable_name]
			varprops.append(statevariableobject['typeName']['type'])
			varprops.append(variable_name)

			if statevariableobject['typeName']['type'] == 'ElementaryTypeName':
				variable_type = statevariableobject['typeName']['name']
				varprops.append(variable_type)
				storage_index, byte_index, v2 = elementaryvariables(statevariableobject, variable_type,
				                                                    storage_index, byte_index)
				varprops = varprops + v2

				metaarray.append(varprops)
				continue

			if statevariableobject['typeName']['type'] == 'UserDefinedTypeName':
				# Check if struct
				if statevariableobject['typeName']['namePath'] in list(
						parsedtreeobject.contracts[contract_name].structs.keys()):

					variable_type = statevariableobject['typeName']['namePath']
					varprops.append(variable_type)

					storage_index, byte_index, v2 = structs(statevariableobject, variable_type, storage_index,
					                                        byte_index)
					varprops = varprops + v2
					metaarray.append(varprops)
					continue

				if statevariableobject['typeName']['namePath'] in list(
						parsedtreeobject.contracts[contract_name].enums.keys()):
					variable_type = statevariableobject['typeName']['namePath']
					varprops.append(variable_type)
					storage_index, byte_index, v2 = enums(statevariableobject, variable_type, storage_index, byte_index)
					varprops = varprops + v2
					metaarray.append(varprops)
					continue

			if statevariableobject['typeName']['type'] == 'ArrayTypeName':
				storage_index, byte_index, v2 = arraytype(statevariableobject, storage_index, byte_index)
				varprops = varprops + v2
				metaarray.append(varprops)
				continue

			if statevariableobject['typeName']['type'] == 'Mapping':
				variable_name = statevariableobject['name']
				keytype = statevariableobject['typeName']['keyType']['name']
				if statevariableobject['typeName']['valueType']['type'] == 'ElementaryTypeName':
					valuetype = statevariableobject['typeName']['valueType']['name']
				else:
					valuetype = statevariableobject['typeName']['valueType']['namePath']
				st = str(keytype) + "=>" + str(valuetype)
				varprops.append(st)
				if byte_index != 0:
					storage_index += 1
				byte_index = 0
				print(f"{spaces}Key Type:\t\t{keytype}\n\tValue Type:\t\t"
				      f"{valuetype}\n\tIndex Assigned:\t{storage_index}")
				varprops.append(storage_index)
				varprops.append(None)
				varprops.append(32)
				storage_index += 1
				metaarray.append(varprops)
				continue

			print(f"{spaces}The State Variable given is of Unhandled Type. Type:"
			      f" {statevariableobject['typeName']['type']}")
			break

		print("\n\n==================================================================\nGeneral:\tVariable Type | Name | "
		      "Data "
		      "Type | Storage Index | Byte Index | Size\nArrays:\t\tVariable Type | Name | Data "
		      "Type | [ 1st Packed Patch: [Storage Index | Byte Index | Size], ...]\n\n")
		for row in metaarray:
			print(row)


if __name__ == "__main__":
	main()

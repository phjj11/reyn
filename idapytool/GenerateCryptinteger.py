import idautils
import idc
import idaapi
import zlib

def processEncrypt(ea, name, CRYPTSTART_PATTERN, CRYPTEND_PATTERN, EPILOGUE_PATTERN, PROLOGUE_PATTERN):
	prologue = idc.FindBinary(ea, SEARCH_UP, PROLOGUE_PATTERN) if len(PROLOGUE_PATTERN) != 0 else idc.GetFunctionAttr(ea, FUNCATTR_START)
	epilogue = idc.FindBinary(ea, SEARCH_DOWN, EPILOGUE_PATTERN) if len(EPILOGUE_PATTERN) != 0 else idc.GetFunctionAttr(ea, FUNCATTR_END)
	
	idc.MakeFunction(prologue, epilogue + EPILOGUE_PATTERN.count(' ') + 1);

	cryptStart = idc.FindBinary(ea, SEARCH_DOWN if name != "BYTE" else SEARCH_UP, CRYPTSTART_PATTERN)
	cryptEnd = idc.FindBinary(ea, SEARCH_DOWN, CRYPTEND_PATTERN)

	# Generate Encrypt
	ea = cryptStart + CRYPTSTART_PATTERN.count(' ') + 1

	opStr = ""

	while ea < cryptEnd:

		if idc.GetMnem(ea) != 'mov':
			result = {
			  'add': lambda x: "new Add({0})".format(idc.GetOperandValue(x, 1)),
			  'sub': lambda x: "new Sub({0})".format(idc.GetOperandValue(x, 1)),
			  'xor': lambda x: "new Xor({0})".format(idc.GetOperandValue(x, 1)),
			  'ror': lambda x: "new Ror({0})".format(idc.GetOperandValue(x, 1)),
			  'rol': lambda x: "new Rol({0})".format(idc.GetOperandValue(x, 1)),
			  'not': lambda x: "new Not()",
			  'inc': lambda x: "new Inc()",
			  'dec': lambda x: "new Dec()",
			}[idc.GetMnem(ea)](ea)
			opStr += str("{0}{1}".format(result, ", " if idc.NextNotTail(ea) != cryptEnd else ""))
			
		ea = idc.NextNotTail(ea)
	
	print "CryptOperations.Add(0x{0:X}, new Operations({1}));".format(zlib.crc32(opStr) & 0xffffffff, opStr)

	idc.MakeNameEx(prologue, "Encrypt_{0}_{1:X}".format(name, zlib.crc32(opStr) & 0xffffffff), SN_NOCHECK | SN_NOWARN)

	return;


def ScanFunctions(name, ENCRYPT_PATTERN, PROLOGUE_PATTERN, EPILOGUE_PATTERN, CRYPTSTART_PATTERN, CRYPTEND_PATTERN):	
	ea = FindBinary(INF_BASEADDR, SEARCH_DOWN, ENCRYPT_PATTERN)

	while ea != BADADDR:
		processEncrypt(ea, name, CRYPTSTART_PATTERN, CRYPTEND_PATTERN, EPILOGUE_PATTERN, PROLOGUE_PATTERN)
		ea = FindBinary(ea + 4, SEARCH_DOWN, ENCRYPT_PATTERN)

	return 0;


INT32_ENCRYPT_PATTERN = "8B 4E 04 8D 55 FF 8A D8"
INT32_PROLOGUE_PATTERN = "8B FF 55 8b ec"
INT32_EPILOGUE_PATTERN = "c3 68 ? ? ? ? e8 ? ? ? ?"
INT32_CRYPTSTART_PATTERN = "80 CB 80"
INT32_CRYPTEND_PATTERN = "88 5D FF 3B D1"

ScanFunctions("INT32", INT32_ENCRYPT_PATTERN, INT32_PROLOGUE_PATTERN, INT32_EPILOGUE_PATTERN, INT32_CRYPTSTART_PATTERN, INT32_CRYPTEND_PATTERN)

BYTE_ENCRYPT_PATTERN = "88 45 FF 8D 45 FF 50 e8 ? ? ? ? 8B E5 5D c3"
BYTE_PROLOGUE_PATTERN = "8B FF 55 8B EC"
BYTE_EPILOGUE_PATTERN = "8B E5 5D C3"
BYTE_CRYPTSTART_PATTERN = "8A 02"
BYTE_CRYPTEND_PATTERN = "88 45 FF"

ScanFunctions("BYTE", BYTE_ENCRYPT_PATTERN, BYTE_PROLOGUE_PATTERN, BYTE_EPILOGUE_PATTERN, BYTE_CRYPTSTART_PATTERN, BYTE_CRYPTEND_PATTERN)

STRING_ENCRYPT_PATTERN = "8D 9B 00 00 00 00  83 7E 14 10 72 04 8b 06 eb 02 8b c6 8a 04 18"
STRING_CRYPTSTART_PATTERN = "8A 04 18"
STRING_CRYPTEND_PATTERN = "88 45 FF"

STRING2_ENCRYPT_PATTERN = "90 83 78 14 10 72 02 8B 00"
STRING2_CRYPTSTART_PATTERN = "8B 46 04"
STRING2_CRYPTEND_PATTERN = "88 5D FF"

STRING3_ENCRYPT_PATTERN = "8D 49 00 83 7F 14 10 72 04 8b 07 eb 02 8b c7 8a 1c 10"
STRING3_CRYPTSTART_PATTERN = "8B 46 04"
STRING3_CRYPTEND_PATTERN = "88 5D FF"

ScanFunctions("STRING", STRING_ENCRYPT_PATTERN, "", "", STRING_CRYPTSTART_PATTERN, STRING_CRYPTEND_PATTERN)
ScanFunctions("STRING", STRING2_ENCRYPT_PATTERN, "", "", STRING2_CRYPTSTART_PATTERN, STRING2_CRYPTEND_PATTERN)
ScanFunctions("STRING", STRING3_ENCRYPT_PATTERN, "", "", STRING3_CRYPTSTART_PATTERN, STRING3_CRYPTEND_PATTERN)

INT16_ENCRYPT_PATTERN = "8A 5D F8 8D 55 FF 8B 4E 04"
INT16_CRYPTSTART_PATTERN = "80 CB 80"
INT16_CRYPTEND_PATTERN = "88 5D FF"
INT16_PROLOGUE_PATTERN = "8B FF 55 8b ec"
INT16_EPILOGUE_PATTERN = "c3 68 ? ? ? ? e8 ? ? ? ?"

ScanFunctions("INT16", INT16_ENCRYPT_PATTERN, INT16_PROLOGUE_PATTERN, INT16_EPILOGUE_PATTERN, INT16_CRYPTSTART_PATTERN, INT16_CRYPTEND_PATTERN)

FLOAT_ENCRYPT_PATTERN = "8D 9B 00 00 00 00 8A 18 8D 45 FF 8B 4E 04"
FLOAT_CRYPTSTART_PATTERN = "8B 4E 04"
FLOAT_CRYPTEND_PATTERN = "88 5D FF"
FLOAT_PROLOGUE_PATTERN = "8B FF 55 8b ec"
FLOAT_EPILOGUE_PATTERN = "c3 68 ? ? ? ? e8 ? ? ? ?"

ScanFunctions("FLOAT", FLOAT_ENCRYPT_PATTERN, FLOAT_PROLOGUE_PATTERN, FLOAT_EPILOGUE_PATTERN, FLOAT_CRYPTSTART_PATTERN, FLOAT_CRYPTEND_PATTERN)
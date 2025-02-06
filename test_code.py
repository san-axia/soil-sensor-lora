# Test code
import soil_data_parse as parser
hex_data = 'fedc016772c91a963900000005030020000000000000012200000000000000000000000000000000000002bc0000000000fedc012e3f'
# hex_data = 'fedc016f8be929963c0000000a0300100000011a00000001000002bc0000000000'
# hex_data = 'fedc012b6768622b64000000010300040000000000'
# Convert hex string to bytes
binary_data = bytes.fromhex(hex_data)
# print(binary_data)
print(parser.auto_parse(binary_data))
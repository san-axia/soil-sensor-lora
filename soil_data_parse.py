from datetime import datetime, timezone
# Input Hex Data and Segment Lengths
# hex_data = (
#     "fedc016772c91a96390000000d030020000000000000011c000000fa0000004a00000066000000cf000003100000041e00"
# )
hex_data = 'fedc016772c91a963900000005030020000000000000012200000000000000000000000000000000000002bc0000000000fedc012e3f'

labels = ['device_id','session_id','moisture','temperature','conductivity','ph','n','p','k','salinity','dissolved_solids_tds','dateutc']
header = bytes.fromhex('fedc')
byte_segment = {
    # 'header':2, 
    'fixed_value':1, 
    'device_id':6, 
    'session_id':4,
    'fixed_cmd': 1, 
    'byte_length':2, 
    'registration_status':4,
    'temperature': 4,
    'moisture': 4,
    'n': 4,
    'p': 4,
    'k': 4,
    'ph': 4,
    'conductivity': 4,
    'crc': 1}  # Lengths in bytes

def segment_binary_data(binary_data, byte_segment):

    # Segment data
    segments = {}
    # Validate total length
    total_length = sum(byte_segment.values())
    if len(binary_data) != total_length:
        print(f"Data length mismatch: Expected {total_length} bytes, got {len(binary_data)} bytes")
        return None
    
    start = 0
    for key in byte_segment:
        end = start + byte_segment[key]
        value = binary_data[start:end]
        segments[key]=value
        start = end

    return segments

def parse_data(binary_data,byte_segment=byte_segment):
    # Process and Display Segments
    data = {}
    try:
        segments = segment_binary_data(binary_data, byte_segment)
        if segments:
            for key in segments:
                if key in ['temperature','moisture','n','p','k','ph','conductivity']:
                    if key == 'temperature':
                        # print(f"{key} : {int.from_bytes(segments[key], byteorder='big',signed=True)/10}")
                        data[key] = int.from_bytes(segments[key], byteorder='big',signed=True)/10
                    elif key == 'moisture':
                        # print(f"{key} : {int.from_bytes(segments[key], byteorder='big',signed=False)/10}")
                        data[key] = int.from_bytes(segments[key], byteorder='big',signed=False)/10
                    elif key == 'ph':
                        # print(f"{key} : {int.from_bytes(segments[key], byteorder='big',signed=False)/100}")
                        data[key] = int.from_bytes(segments[key], byteorder='big',signed=False)/100
                    else:
                        # print(f"{key} : {int.from_bytes(segments[key], byteorder='big',signed=False)}")
                        data[key] = int.from_bytes(segments[key], byteorder='big',signed=False)
                else:
                    # print(f"{key} : {segments[key].hex()}")
                    data[key] = str(segments[key].hex())
        else:
            # print(segments)
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None
    return data

def cleaned_data (data):
    clean_data = {}
    if data:
        for label in labels:
            if label in data.keys():
                clean_data[label] = data[label]
            elif label == 'dateutc':
                clean_data[label] = str(datetime.now(timezone.utc))
            else:
                clean_data[label] = 0
    else:
        return None
    return clean_data

def auto_parse(binary_data):
    b_datas = binary_data.split(header)
    c_datas = []
    for b_data in b_datas:
        if len(b_data)>0:
            data = parse_data(b_data,byte_segment)
            c_data = cleaned_data(data)
            if c_data:
                c_datas += [c_data]
    return c_datas


# Test code
# Convert hex string to bytes
# binary_data = bytes.fromhex(hex_data)
# print(binary_data)
# print(auto_parse(binary_data))
from datetime import datetime, timezone
# Input Hex Data and Segment Lengths
# With NPK -  "fedc016772c91a96390000000d030020000000000000011c000000fa0000004a00000066000000cf000003100000041e00"
# NO-NPK - fedc016f8be929963c0000000a0300100000011a00000001000002bc0000000000
# UV - fedc012b6768622b64000000010300040000000000
# 
# fedc 01 6f8be929963c 0000000a 03 0010 0000011a 00000001 000002bc 00000000 00
# fedc 01 2b6768622b64 00000001 03 0004 00000000 00



labels = ['device_id','session_id','moisture','temperature','conductivity','ph','n','p','k','salinity','dissolved_solids_tds','dateutc','uv']
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

# def segment_binary_data(binary_data, byte_segment):

#     # Segment data
#     segments = {}
#     # Validate essential length
#     total_length = sum(byte_segment.values())
#     if len(binary_data) != total_length:
#         # print(binary_data)
#         print(f"Data length mismatch: Expected {total_length} bytes, got {len(binary_data)} bytes")
#         return None
    
#     start = 0
#     for key in byte_segment:
#         end = start + byte_segment[key]
#         value = binary_data[start:end]
#         segments[key]=value
#         start = end

#     return segments
def segment_binary_data(binary_data, byte_segment):

    # Segment data
    segments = {}
    # Validate essential length
    head_length = 5
    single_data_length = 4
    essentil_length = sum(list(byte_segment.values())[:head_length]) + byte_segment['crc']
    total_length = sum(byte_segment.values())
    b_length = len(binary_data)

    data_length = b_length - essentil_length
    if (data_length>0) & ((data_length%4)==0):
        print('Valid Data - ',binary_data.hex())
    else:
        print('Invalid Data - ',binary_data.hex())
        return None

    # remove the essential headers
    start = 0
    for key in list(byte_segment.keys())[:head_length]:
        end = start + byte_segment[key]
        value = binary_data[start:end]
        segments[key]=value
        start = end
    
    #optional reg. status
    if b_length==total_length:
        key = 'registration_status'
        end = start + byte_segment[key]
        value = binary_data[start:end]
        segments[key]=value
        start = end

    # remove the tail (CRC)
    end = b_length
    start = end - byte_segment['crc']
    value = binary_data[start:end]
    segments['crc']=value
    
    start = sum(list(byte_segment.values())[:head_length])
    print (start)
    
    # check UV sensor
    d_length = b_length-start-byte_segment['crc']
    if d_length==single_data_length:
        end = start + single_data_length
        value = binary_data[start:end]
        segments['uv'] = value
        return segments

    # soil data (with or without NPK)    
    for key in list(byte_segment.keys())[(head_length+1):-1]:
        # skip NPK
        if (b_length < total_length) & (key in ['n','p','k']):
            pass
        else:
            end = start + byte_segment[key]
            if end>b_length:
                break
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
                if key in ['temperature','moisture','n','p','k','ph','conductivity','uv']:
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
            # else:
            #     clean_data[label] = 0
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
# hex_data = 'fedc016772c91a963900000005030020000000000000012200000000000000000000000000000000000002bc0000000000fedc012e3f'
# hex_data = 'fedc016f8be929963c0000000a0300100000011a00000001000002bc0000000000'
# hex_data = 'fedc012b6768622b64000000010300040000000000'
# Convert hex string to bytes
# binary_data = bytes.fromhex(hex_data)
# print(binary_data)
# print(auto_parse(binary_data))
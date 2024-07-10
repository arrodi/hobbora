import base64

def encode_to_base64(input_string):
    # Convert the string to bytes
    byte_string = input_string.encode('utf-8')
    
    # Encode the bytes to base64
    base64_bytes = base64.b64encode(byte_string)
    
    # Convert the base64 bytes back to a string
    base64_string = base64_bytes.decode('utf-8')
    
    return base64_string

# Example usage
input_string = "Hello WOrld"
encoded_string = encode_to_base64(input_string)
print(f"Original string: {input_string}")
print(f"Encoded string: {encoded_string}")
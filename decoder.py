def decode_unicode_string(unicode_string):
    decoded_string = ""
    hex_values = unicode_string.split("\\u")[1:]

    for hex_value in hex_values:
        if not hex_value:
            continue
        decimal_value = int(hex_value, 16)
        decoded_string += chr(decimal_value)

    return decoded_string
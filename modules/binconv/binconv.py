import sys

def convert_to_binary(data, base):
    try:
        decimal_value = int(data, base)
        binary_value = bin(decimal_value)[2:]  # '0b' prefix を削除
        return binary_value
    except ValueError:
        return "Invalid input"

def convert_from_binary(binary_value):
    try:
        decimal_value = int(binary_value, 2)
        hex_value = hex(decimal_value)[2:]  # '0x' prefix を削除
        return {
            "decimal": decimal_value,
            "hexadecimal": hex_value
        }
    except ValueError:
        return "Invalid input"

def main():
    if len(sys.argv) != 3:
        print("Usage: python binconv.py <data> <base>")
        print("Example: python binconv.py 1101 2")
        print("Example: python binconv.py A 16")
        sys.exit(1)

    data = sys.argv[1]
    base = int(sys.argv[2])

    if base == 2:
        result = convert_from_binary(data)
    else:
        result = convert_to_binary(data, base)
    print(result)

if __name__ == "__main__":
    main()
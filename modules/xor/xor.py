import sys

def xor_strings(str1, str2):
    return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(str1, str2))

def main():
    if len(sys.argv) != 3:
        print("Usage: python xor.py <string1> <string2>")
        sys.exit(1)

    string1 = sys.argv[1]
    string2 = sys.argv[2]

    # 文字列の長さが異なる場合は短い方に合わせる
    if len(string1) != len(string2):
        min_len = min(len(string1), len(string2))
        string1 = string1[:min_len]
        string2 = string2[:min_len]

    result = xor_strings(string1, string2)
    print(result)

if __name__ == "__main__":
    main()
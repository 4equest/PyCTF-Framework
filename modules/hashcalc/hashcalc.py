import hashlib
import sys

def calculate_hash(file_path, algorithm):
    hash_obj = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()

def main():
    if len(sys.argv) != 3:
        print("Usage: python hashcalc.py <file_path> <algorithm>")
        print("Supported algorithms: MD5, SHA1, SHA256")
        sys.exit(1)

    file_path = sys.argv[1]
    algorithm = sys.argv[2].upper()

    if algorithm in ("MD5", "SHA1", "SHA256"):
        hash_value = calculate_hash(file_path, algorithm)
        print(f"{algorithm}: {hash_value}")
    else:
        print("Invalid algorithm specified.")

if __name__ == "__main__":
    main()
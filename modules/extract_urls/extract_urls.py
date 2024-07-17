import re
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_urls.py <text>")
        sys.exit(1)

    text = sys.argv[1]

    # URLの正規表現パターン
    url_pattern = re.compile(r'https?://[\w/:%#\$&\?\(\)~\.=\+\-]+')

    # テキストからURLを抽出
    urls = url_pattern.findall(text)

    # 結果を出力
    for url in urls:
        print(url)

if __name__ == "__main__":
    main()
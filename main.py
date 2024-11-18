import requests
import MeCab
import re


def fetch_wikipedia_article(title):
    """Wikipedia APIから記事の内容を取得する関数"""
    url = "https://ja.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "format": "json",
        "explaintext": True,
        "titles": title
    }
    response = requests.get(url, params=params)
    data = response.json()
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    return page["extract"] if "extract" in page else ""


def count_mora(word):
    """単語のモーラ数をカウントする関数"""
    processed_word = re.sub(r'[ァィゥェォャュョヮ]', '', word)
    return len(processed_word)


def extract_tankas(words):

    n = len(words)
    result = []
    for start in range(n):
        total = 0
        for end in range(start, n):
            total += words[end][2]
            if total == 31 and (words[start][1] not in ("記号", "補助記号", "助詞", "助動詞")):
                result.append(words[start:end+1])
            elif total > 31:
                break
    return result


def parse(text):
    """与えられたテキストから偶然短歌を抽出する関数"""
    tagger = MeCab.Tagger()
    sentences = text.split("\n")  # 文を改行で分割
    words = []

    # 各文に対して処理を行う
    for sentence in sentences:
        node = tagger.parseToNode(sentence)

        # 各単語の音数をカウントして構造に追加
        while node:
            feature = node.feature.split(",")
            if feature[0] != "BOS/EOS":  # BOS/EOSはスキップ
                if len(feature) > 9:
                    mora = count_mora(feature[9])
                    words.append((node.surface, feature[0], mora))
                elif feature[0] in ("補助記号", "記号"):
                    words.append((node.surface, feature[0], 0))
            node = node.next

    return extract_tankas(words)


if __name__ == '__main__':
    # Wikipediaの記事タイトルを指定して偶然短歌を抽出
    title = "モロカン派"
    article_text = fetch_wikipedia_article(title)
    tankas = parse(article_text)

    for tanka in tankas:
        print("".join(t[0] for t in tanka))
        print(tanka)

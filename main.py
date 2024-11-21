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


def extract_tanka_candidates(words):
    n = len(words)
    results = []
    for start in range(n):
        total = 0
        for end in range(start, n):

            after = total + words[end][2]

            # 句またがりがないように判定する
            if total < 5 and 5 < after:
                break
            elif total < 12 and 12 < after:
                break
            elif total < 17 and 17 < after:
                break
            elif total < 24 and 24 < after:
                break
            elif total < 31 and 31 < after:
                break

            total = after

            if total == 31 and (words[start][1] not in ("記号", "補助記号", "助詞", "助動詞")):
                results.append(words[start:end+1])

    return ["".join(r[0] for r in result) for result in results]


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

    return words


if __name__ == '__main__':
    # Wikipediaの記事タイトルを指定して偶然短歌を抽出
    title = "モロカン派"
    article_text = fetch_wikipedia_article(title)
    tankas = extract_tanka_candidates(parse(article_text))

    for tanka in tankas:
        print(tanka)

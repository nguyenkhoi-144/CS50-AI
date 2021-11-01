import math
import nltk
import os
import sys

def main():
    '''tính toán tần suất thuật ngữ hàng đầu cho 1 kho tài liệu '''

    if len(sys.argv) != 2:
        sys.exit("Usage: python tfidf.py corpus")
    print("Loang data...")
    corpus = load_data(sys.argv[1])

    # nhận tất cả các từ trong kho ngữ liệu
    print('Extracting words from corpus...')
    words = set()
    for filename in corpus:
        words.update(corpus[filename])

    # tính toán TF-IDFs
    print('calculating term frequencies...')
    tfidfs = dict()
    for filename in corpus:
        tfidfs[filename] = []
        for word in corpus[filename]:
            tf = corpus[filename][word]
            tfidfs[filename].append((word, tf))

    # sắp xếp và nhận 5 tần số thuật ngữ hàng đầu cho mỗi tệp
    print("Compute top term...")
    for filename in corpus:
        tfidfs[filename].sort(key= lambda tfidf: tfidf[1], reverse=True)
        tfidfs[filename] = tfidfs[filename][:5]

    # in ket qua
    print()
    for filename in corpus:
        print(filename)
        for term, score in tfidfs[filename]:
            print(f"{term}: {score:.4f}")

def load_data(directory):
    files = dict()
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename)) as f:

            # trích xuất từ
            contents = [
                word.lower() for word in
                nltk.word_tokenize(f.read())
                if word.isalpha()
            ]
            # đếm tần số
            frequencies = dict()
            for word in contents:
                if word not in frequencies:
                    frequencies[word] = 1
                else:
                    frequencies[word] += 1
            files[filename] = frequencies

    return files

if __name__=="__main__":
    main()

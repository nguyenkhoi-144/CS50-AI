from collections import Counter

import  math
import nltk
import os
import sys

def main():
    '''Tính toán tần suất thuật ngữ hàng đầu cho một kho tài liệu.'''
    if len(sys.argv) != 3:
        sys.exit("Usage: python tfidf.py n corpus")
    print("loanding data...")

    n = int(sys.argv[1])
    corpus = load_data(sys.argv[2])

    # Tính n-gram
    ngrams = Counter(nltk.ngrams(corpus, n))

    # In n-gram phổ biến nhất
    for ngram, freq in ngrams.most_common(10): # in ra 10 tu pho bien nhat
        print(f"{freq} : {ngram}")

def load_data():
    contents = []

    # đọc tất cả các file và trích xuất từ
    for filename in os.listdir(directory):
        with open(os.path.join(directory,filename)) as f:
            contents.extend([
                word.lower() for word in
                nltk.word_tokenize(f.read())
                if any(c.isalpha() for c in word)
            ])
    return contents

if __name__ == "__main__":
    main()

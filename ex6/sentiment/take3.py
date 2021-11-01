import nltk
import os
import sys

def main():

    # đọc dữ liệu từ file
    if len(sys.argv) != 2:
        sys.exit("Usage: python setiment.py corpus")
    positives, negatives = load_data(sys.argv[1])

    #tạo 1 bộ tất cả từ
    words = set()
    for document in positives:
        words.update(document)
    for document in negatives:
        words.update(document)

    # Trích xuất các tính năng từ văn bản
    training = []
    training.extend(generate_features(positives, words, "Positive"))
    training.extend(generate_features(negatives, words, "Negative"))

    # Phân loại mẫu mới
    classifier = nltk.NaiveBayesClassifier.train((training))
    s = input("s: ")
    result = (classify(classifier, s, words))
    for key in result.samples():
        print(f"{key}: {result.prob(key):.4f}")

def extract_words(document):
    return set(
        word.lower() for word in nltk.word_tokenize(document)
        if any(c.isalpha() for c in word)
    )
def load_data(directory):
    reusult = []
    for filename in ["positives.txt", "negatives.txt"]:
        with open(os.path.join(directory, filename)) as f:
            reusult.append([
                extract_words(line)
                for line in f.read().splitlines()
            ])
    return reusult

def generate_features(documents, words, lable):
    features = []
    for document in documents:
        features.append(({
            word: (word in document)
            for word in words
        }, lable))
    return features

def classify(classifier, document, words):
    document_words = extract_words(document)
    features = {
        word: (word in document_words)
        for word in words
    }
    return classifier.prob_classify(features)

if __name__=="__main__":
    main()

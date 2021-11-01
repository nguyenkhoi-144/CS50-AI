import os
import string
import math
import nltk
import sys

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    # Kiểm tra đối số dòng lệnh
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    # Tính giá trị IDF trên các tệp
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    # Nhắc người dùng truy vấn
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    # Xác định các kết quả phù hợp tệp hàng đầu theo TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    # Trích xuất các câu từ các tệp hàng đầu

    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    # Tính giá trị IDF qua các câu
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    # Xác định kết quả phù hợp đầu câu
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    Cho một tên thư mục, trả về một từ điển ánh xạ tên tệp của mỗi
    tệp `.txt` bên trong thư mục đó với nội dung của tệp dưới dạng một chuỗi.
    """
    contents = {}
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), "r", encoding="utf8") as file:
            contents[filename] = file.read()
    return contents



def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    Đưa ra một tài liệu (được biểu diễn dưới dạng một chuỗi), hãy trả về một danh sách tất cả
    từ trong tài liệu đó, theo thứ tự.
    Xử lý tài liệu bằng cách chuyển tất cả các từ thành chữ thường và xóa bất kỳ
    dấu chấm câu hoặc từ dừng tiếng Anh.
    """
    # Xoá dấu câu và đổi thành chứ thường
    clearn_string = document.lower().translate(str.maketrans("", "", string.punctuation))
    # chia các từ thành danh sách
    contents = nltk.word_tokenize(clearn_string)
    for item in contents.copy():
        if item in nltk.corpus.stopwords.words("english"):
            contents.remove(item)

    return contents



def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    Đưa ra một từ điển về `tài liệu` ánh xạ tên của tài liệu vào một danh sách
    từ, trả về một từ điển ánh xạ các từ với giá trị IDF của chúng.

    Bất kỳ từ nào xuất hiện trong ít nhất một trong các tài liệu phải nằm trong
    từ điển kết quả.
    """
    # tạo tập hợp các từ trống
    words = set()
    #thêm tất cả các từ trong tài liệu để thiết lập
    for document in documents:
        words.update(documents[document]) # dung update vì có thểm thêm từ trung vào từ điển
    #tạo từ điển idf với các từ làm khoá
    idfs = dict.fromkeys(words, 0)
    # kiểm tra từng từ nếu từ có trong tài liệu
    for word in words:
        for document in documents:
            if word in documents[document]:
                idfs[word] += 1
    # tính toán idf
    for word in idfs:
        idfs[word] = math.log(len(documents) / idfs[word]) #logarit tự nhiên của số tài liệu chia cho số tài liệu mà từ đó xuất hiện.
    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    Đưa ra một `truy vấn` (một tập hợp các từ),` tệp` (một tên ánh xạ từ điển của
    tệp vào danh sách các từ của chúng) và `idfs` (từ điển ánh xạ các từ
    với giá trị IDF của chúng), trả về danh sách các tên tệp của đầu `n`
    các tệp phù hợp với truy vấn, được xếp hạng theo tf-idf.
    """
    def tfidf_calc(word, file):
        words = files[file]
        if word in words:
            tf = words.count(word) / len(words)
            idf = idfs[word]
            #tf-idf cho một thuật ngữ được tính bằng cách nhân số lần thuật ngữ đó xuất hiện trong tài liệu với giá trị IDF của thuật ngữ đó.
            return tf * idf
        return 0
    # tạo từ điển điểm số
    scores = dict.fromkeys(files.keys(), 0)
    # nhận điểm cho mỗi tài liệu
    for file in scores:
        for word in query:
            scores[file] += tfidf_calc(word, file)

    top = []
    # nhận các tệp hàng đầu
    for i in range(n):
        file = max(scores, key=scores.get)
        top.append(file)
        scores.pop(file)
    return top





def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.

    Đưa ra một `truy vấn` (một tập hợp các từ),` câu` (một ánh xạ từ điển
    câu vào danh sách các từ của chúng) và `idfs` (từ điển ánh xạ các từ
    với giá trị IDF của chúng), trả về danh sách `n` câu hàng đầu phù hợp
    truy vấn, được xếp hạng theo idf. Nếu có ràng buộc, ưu tiên nên
    được cung cấp cho các câu có mật độ cụm từ truy vấn cao hơn.
    """
    def get_qtd(sentence):
        qtd = 0
        for word in sentence:
            if word in query:
                qtd += 1
        qtd /= len(sentence)
        return qtd
    scores = []
    for sentence in sentences:
        # nhận giá trị idf
        idf = 0
        for word in query:
            if word in sentences[sentence]:
                idf += idfs[word]

        # Nhận mật độ cụm từ truy vấn
        qtd = get_qtd(sentences[sentence])
        # them du lieu vao danh sach duoi dang tuple
        scores.append((sentence, idf, qtd))
    # sắp xếp điển theo idf, rồi đến qtd
    scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
    # trả lại n câu hàng đầu
    top = []
    for i in range(n):
        top.append(scores[i][0])
    return top



if __name__ == "__main__":
    main()

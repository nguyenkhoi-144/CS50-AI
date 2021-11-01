import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> N V | NP VP | VP NP | S NP | S P NP | S P S | S Conj S|
AA -> Adj | Adv | Adj AA | Adv AA
VP -> V | V P | V AA | Adv V
NP -> N | P NP | Det N | Det N AA | Det AA N | AA N
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    # Nếu tên tệp được chỉ định, hãy đọc câu từ tệp
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    # Nếu không, lấy câu làm đầu vào
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    # Chuyển đầu vào thành danh sách các từ
    s = preprocess(s)

    # Attempt to parse sentence
    # Cố gắng phân tích cú pháp câu
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    # In từng cây với các khối cụm danh từ
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.

    Chuyển đổi `câu` thành một danh sách các từ của nó.
    Xử lý trước câu bằng cách chuyển đổi tất cả các ký tự thành chữ thường
    và xóa bất kỳ từ nào không chứa ít nhất một bảng chữ cái
    tính cách.
    """
    tokens = [word.lower() for word in nltk.word_tokenize(sentence) if word.lower().islower()]
    return tokens


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.

    Trả về danh sách tất cả các cụm danh từ trong cây câu.
    Một cụm danh từ chunk được định nghĩa là bất kỳ cây con nào của câu
    có nhãn là "NP" mà bản thân nó không chứa bất kỳ nhãn nào khác
    cụm danh từ như cây con.
    """
    result = []
    for sub in tree.subtrees():
    # Một cụm danh từ chunk được định nghĩa là bất kỳ cây con nào của câu
    # có nhãn là "NP" bản thân nó không chứa bất kỳ nhãn nào khác
    # cụm danh từ làm cây con.
    # print ("sub:", sub, "label:", sub.label)
        if sub.label() is "NP":
            resulf.append(sub)
    # Trả về danh sách tất cả các cụm danh từ trong cây câu.
    return result




if __name__ == "__main__":
    main()

import markovify
import sys

# doc doan van tu file
if len(sys.argv) != 2:
    sys.exit("Usage: python generator.py sample.txt")
with open(sys.argv[1]) as f:
    text = f.read()

#training model
text_model = markovify.Text(text)

# tạo câu
print()
for i in range(5):
    print(text_model.make_sentence())
    print()


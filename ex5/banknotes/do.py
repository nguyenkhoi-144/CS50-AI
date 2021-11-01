import csv
import tensorflow as tf

from sklearn.model_selection import train_test_split

# đọc dữ liệu
with open("banknotes.csv") as f:
    reader = csv.reader(f)
    next(reader)

    data = []
    for row in reader:
        data.append({
            "evidence":[float(cell) for cell in row[:4]],
            "label": 1 if row[4] == "0" else 0
        })
# phân tích dữ liệu riêng cho đào tạo và thử nghiệm
evidence = [row["evidence"] for row in data]
label = [row["label"] for row in data]
X_training, X_testing, y_training, y_testing = train_test_split(
    evidence, label,test_size=0.4
)
# tạo 1 mạng nơ ron thần kinh
model = tf.keras.models.Sequential()
# Thêm một lớp ẩn với 8 đơn vị, với kích hoạt ReLU
model.add(tf.keras.layers.Dense(8, input_shape=(4,), activation="relu"))
# Thêm lớp đầu ra với 1 đơn vị, với kích hoạt sigmoid
model.add(tf.keras.layers.Dense(1, activation="sigmoid"))
# Huấn luyện mạng thần kinh
model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)
model.fit(X_training,y_training, epochs=20)
# Đánh giá mô hình hoạt động tốt như thế nào
model.evaluate(X_testing, y_testing, verbose=2)
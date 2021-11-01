import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 10
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    # Get image arrays and labels for all image files
    # Nhận mảng hình ảnh và nhãn cho tất cả các tệp hình ảnh
    images, labels = load_data(sys.argv[1])

    # Split data into training and testing sets
    # Chia dữ liệu thành các tập huấn luyện và thử nghiệm
    labels = tf.keras.utils.to_categorical(labels)
    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE
    )

    # Get a compiled neural network
    # Nhận một mạng nơ-ron đã biên dịch
    model = get_model()

    # Fit model on training data
    # Phù hợp với mô hình trên dữ liệu đào tạo
    model.fit(x_train, y_train, epochs=EPOCHS)

    # Evaluate neural network performance
    # Đánh giá hiệu suất mạng nơ-ron
    model.evaluate(x_test, y_test, verbose=2)

    # Save model to file
    # Lưu mô hình vào tệp
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    Tải dữ liệu hình ảnh từ thư mục `data_dir`.

    Giả sử `data_dir` có một thư mục được đặt tên theo mỗi danh mục, được đánh số
    0 đến NUM_CATEGORIES - 1. Bên trong mỗi thư mục danh mục sẽ có một số
    số lượng tệp hình ảnh.

    Trả về tuple `(hình ảnh, nhãn)`. `hình ảnh` phải là một danh sách tất cả
    của các hình ảnh trong thư mục dữ liệu, nơi mỗi hình ảnh được định dạng là
    numpy ndarray với kích thước IMG_WIDTH x IMG_HEIGHT x 3. `nhãn` nên
    là danh sách các nhãn số nguyên, đại diện cho các danh mục cho mỗi
    `hình ảnh` tương ứng.
    """

    # Init result
    # Kết quả Init
    images = []
    labels = []

    # Assume `data_dir` has one directory named after each category, numbered
    #     0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    #     number of image files.

    # Giả sử `data_dir` có một thư mục được đặt tên theo mỗi danh mục, được đánh số
    # 0 đến NUM_CATEGORIES - 1. Bên trong mỗi thư mục danh mục sẽ có một số
    # số tệp hình ảnh.
    cats = [cat for cat in os.listdir(data_dir)]
    # print (cat)

    for cat in cats:
        for img_name in os.listdir(os.path.join(data_dir, cat)):
            # print(img_name)
            img = cv2.resize(cv2.imread(os.path.join(data_dir, cat, img_name)), dsize=(IMG_WIDTH, IMG_HEIGHT))

            # Append to result
            images.append(img)
            labels.append(cat)

    # Return tuple `(images, labels)`
    return (images, labels)


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.

    Trả về mô hình mạng nơ-ron tích tụ đã biên dịch. Giả sử rằng
    `input_shape` của lớp đầu tiên là` (IMG_WIDTH, IMG_HEIGHT, 3) `.
    Lớp đầu ra phải có `NUM_CATEGORIES` đơn vị, một đơn vị cho mỗi danh mục.
    """
    # init model,pooling layers
    # init model, gộp các lớp
    mod = tf.keras.models.Sequential()

    # `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    # `input_shape` của lớp đầu tiên là` (IMG_WIDTH, IMG_HEIGHT, 3) `./ 3 ở đây đại cho 3 mau RGB
    mod.add(tf.keras.layers.Conv2D(32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)))
    mod.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))
    mod.add(tf.keras.layers.Conv2D(64, (3, 3), activation="relu"))
    mod.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))
    mod.add(tf.keras.layers.Conv2D(64, (3, 3), activation="relu"))
    mod.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2)))

    # Flatten, add dropout
    # Làm phẳng, thêm học sinh bỏ học
    mod.add(tf.keras.layers.Flatten())
    mod.add(tf.keras.layers.Dropout(0.2))

    # The output layer should have `NUM_CATEGORIES` units, one for each category.
    # Lớp đầu ra phải có `NUM_CATEGORIES` đơn vị, một đơn vị cho mỗi danh mục.
    mod.add(tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax"))

    # Compile model, print
    # Biên dịch mô hình, in
    mod.compile(optimizer="adam",
                loss="categorical_crossentropy",
                metrics=["accuracy", "categorical_hinge"])

    return mod


if __name__ == "__main__":
    main()

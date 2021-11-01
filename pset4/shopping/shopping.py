import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

import numpy as np
import pandas as pd

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    # Tải dữ liệu từ bảng tính và chia thành các tập huấn luyện và thử nghiệm
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.

    Tải dữ liệu mua sắm từ tệp CSV `tên tệp` và chuyển đổi thành danh sách
    danh sách bằng chứng và danh sách các nhãn. Trả lại một bộ giá trị (bằng chứng, nhãn).

    bằng chứng phải là một danh sách các danh sách, trong đó mỗi danh sách chứa
    các giá trị sau, theo thứ tự:
        - Hành chính, một số nguyên
        - Administration_Duration, một số dấu phẩy động
        - Thông tin, một số nguyên
        - Informational_Duration, một số dấu phẩy động
        - ProductRelated, một số nguyên
        - ProductRelated_Duration, một số dấu phẩy động
        - BounceRates, một số dấu phẩy động
        - ExitRates, một số dấu phẩy động
        - PageValues, một số dấu phẩy động
        - Ngày đặc biệt, một số dấu phẩy động
        - Tháng, chỉ số từ 0 (tháng 1) đến 11 (tháng 12)
        - Hệ điều hành, một số nguyên
        - Trình duyệt, một số nguyên
        - Vùng, một số nguyên
        - TrafficType, một số nguyên
        - VisitorType, một số nguyên 0 (không trả về) hoặc 1 (quay lại)
        - Cuối tuần, một số nguyên 0 (nếu sai) hoặc 1 (nếu đúng)

    các nhãn phải là danh sách các nhãn tương ứng, trong đó mỗi nhãn
    là 1 nếu Doanh thu là đúng và bằng 0 nếu ngược lại.
    """
    df = pd.read_csv(filename)
    # Tạo ánh xạ tháng và loại khách truy cập
    months = {"Jan": 0,
              "Feb": 1,
              "Mar": 2,
              "Apr": 3,
              "May": 4,
              "June": 5,
              "Jul": 6,
              "Aug": 7,
              "Sep": 8,
              "Oct": 9,
              "Nov": 10,
              "Dec": 11}
    visitors = {"New_Visitor": 0,
                "Returning_Visitor": 1,
                "Other": 0}
    # Nhận nhãn cho các điểm dữ liệu riêng lẻ
    labels = df['Revenue'].astype(int).tolist()
    # Tạo các điểm dữ liệu dưới dạng danh sách giá trị được
    # định dạng, số thực được làm tròn thành hai số thập phân
    df['Administrative'] = df['Administrative'].astype(int)
    df['Administrative_Duration'] = df['Administrative_Duration'].astype(float).round(2)
    df['Informational'] = df['Informational'].astype(int).round(2)
    df['Informational_Duration'] = df['Informational_Duration'].astype(float).round(2)
    df['ProductRelated'] = df['ProductRelated'].astype(int)
    df['ProductRelated_Duration'] = df['ProductRelated_Duration'].astype(float).round(2)
    df['BounceRates'] = df['BounceRates'].astype(float).round(2)
    df['ExitRates'] = df['ExitRates'].astype(float).round(2)
    df['PageValues'] = df['PageValues'].astype(float).round(2)
    df['SpecialDay'] = df['SpecialDay'].astype(float).round(2)
    df['Month'] = df['Month'].map(months)
    df['OperatingSystems'] = df['OperatingSystems'].astype(int)
    df['Browser'] = df['Browser'].astype(int)
    df['Region'] = df['Region'].astype(int)
    df['TrafficType'] = df['TrafficType'].astype(int)
    df['VisitorType'] = df['VisitorType'].map(visitors)
    df['Weekend'] = df['Weekend'].astype(int)
    del df['Revenue']
    # ket qua
    evidence = df.values.tolist()
    result = [evidence, labels]
    # Trả lại một tuple (bằng chứng, nhãn).
    return result




def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.

    Đưa ra một danh sách các danh sách bằng chứng và một danh sách các nhãn, hãy trả về một
    được đào tạo trên k-mô hình láng giềng gần nhất (k = 1) trên dữ liệu.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.

    Đưa ra danh sách các nhãn thực tế và danh sách các nhãn được dự đoán,
    trả về một bộ giá trị (độ nhạy, đặc điểm).

    Giả sử mỗi nhãn là 1 (dương) hoặc 0 (âm).

    `độ nhạy` phải là một giá trị dấu phẩy động từ 0 đến 1
    đại diện cho "tỷ lệ dương thực sự": tỷ lệ của
    các nhãn dương tính thực tế đã được xác định chính xác.

    `cụ thể` phải là một giá trị dấu phẩy động từ 0 đến 1
    đại diện cho "tỷ lệ âm thực sự": tỷ lệ của
    các nhãn phủ định thực tế đã được xác định chính xác.
    """
    # Số lượng xác định dương tính và dương tính
    pos = 0
    posid = 0
    #Số lượng xác định âm tính và dương tính
    neg = 0
    negid = 0

    for label, pred in zip(labels, predictions):
        if label == 1:
            pos += 1
            if pred == 1:
                posid += 1
        elif label == 0:
            neg += 1
            if pred == 0:
                negid += 1
        else:
            raise ValueError
        # `độ nhạy` phải là một giá trị dấu phẩy động từ 0 đến 1
        # đại diện cho "tỷ lệ dương thực sự": tỷ lệ của
        # nhãn dương tính thực tế đã được xác định chính xác.
    sens = float(posid / pos)

        # `cụ thể` phải là một giá trị dấu phẩy động từ 0 đến 1
        # đại diện cho "tỷ lệ âm thực sự": tỷ lệ của
        # nhãn phủ định thực tế đã được xác định chính xác.
    spec = float(negid / neg)
    return (sens, spec)

'''def clean_datasheet(df):
    assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
    df.dropna(inplance=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].astype(np.float64)'''



if __name__ == "__main__":
    main()

import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene/Xác suất vô điều kiện để có gen
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene// Tính xác suất của tính trạng đã cho hai bản sao của gen
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene// Xác suất của tính trạng cho một bản sao của gen
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene// Tính xác suất của tính trạng không có gen
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability// Xác suất đột biến
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.

    Tải dữ liệu gen và tính trạng từ tệp vào từ điển.
    Tệp được giả định là CSV chứa tên trường, mẹ, cha, đặc điểm.
    mẹ, cha đều phải để trống hoặc cả hai đều là tên hợp lệ trong CSV.
    đặc điểm phải là 0 hoặc 1 nếu đặc điểm đã biết, nếu không thì để trống.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    Trả về danh sách tất cả các tập con có thể có của tập hợp s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.

        Tính toán và trả về một xác suất chung.

    Xác suất trả về phải là xác suất mà
        * mọi người trong tập hợp `one_gene` đều có một bản sao của gen và
        * mọi người trong tập hợp `hai_genes` có hai bản sao của gen, và
        * tất cả mọi người không thuộc `one_gene` hoặc` two_gene` đều không có gen này, và
        * mọi người trong tập hợp `have_trait` đều có đặc điểm, và
        * tất cả mọi người không trong set` have_trait` không có đặc điểm.
    """
    # tinh toan xac suat rieng biet cho cha me va con, chia lam 2 nhom
    parent = set()
    children = set()

    for person in people:
        # neu nguoi do khong co me va cha thi nguoi do lam cha me
        if people[person] ["mother"] == None:
            parent.add(person)
        else:
            children.add(person)
    # tinh xac xuat cua cha me
    antes = 1
    for person in parent:
        num = 1 * (person in one_gene) + 2 * (person in two_genes)
        have = (person in have_trait)

        # dung tu dien PROBS de danh gia xac suat cho cha, me
        antes *= PROBS['gene'][num] * PROBS['trait'][num][have]
    conses = 1
    # tinh xac suat cho con cai
    for person in children:
        # lay me va cha cua dua be tu tu dien
        mom = people[person]['mother']
        dad = people[person]['father']
        # danh gia so luong gen cua cha me va con cai
        num = 1 * (person in one_gene) + 2 * (person in two_genes)
        num_mom = 1 * (mom in one_gene) + 2 * (mom in two_genes)
        num_dad = 1 * (dad in one_gene) + 2 * (dad in two_genes)
        have = (person in have_trait)
        # lay gia tri cua xac suat doc bien
        mutation = PROBS['mutation']
        # neu dua tre khong co gen
        if num == 0:
            # neu ca bo va me deu khong co gen va sau do khong trai qua dot bien
            if num_dad == 0 and num_mom == 0:
                effect = (1 - mutation) * (1 - mutation)

            elif (num_dad == 2 and num_mom == 2):
                effect = mutation * mutation

            # neu mot trong hai bo me co 2 gen va nguoi kia co 0 gen
            # nguoi con 1 gen co 2 gen phai trai qua dot bien va gen kia khong duoc
            elif (num_dad == 2 and num_mom == 0) or \
                    (num_dad == 0 and num_mom == 2):
                effect = mutation * (1 - mutation)

            # neu mot trong hai bo me co 1 gen va nguoi kia co 0 gen
            # gen co 1 khong duoc truyen voi prob 0,5
            # cai kia khong duoc dot bien

            elif(num_dad == 0 and num_mom == 1) or \
                    (num_dad == 1 and num_mom == 0):
                effect = (1 - mutation) * 0.5

            # neu 1 trong 2 bo me co 2 gen va nguoi kia co 1 gen
            #nguoi co 2 gen phai bi dot bien va khac khong duoc truyen voi prob 0.5
            elif (num_dad == 2 and num_mom == 1) or \
                    (num_dad == 1 and num_mom == 2):
                effect = mutation * 0.5

            # neu ca ba me deu co gen 1 , moi nguoi truyen voi prob 0.5
            else:
                effect = 0.5 * 0.5
        #neu dua tre co 1 gen
        elif num == 1:
            # neu ca bo va me deu khong co gen thi 1 trong so chung phai dot bien
            # de truyen 1 va con lai khong duoc
            # neu ca bo va me mang 2 gen 1 trong so chung truyen tu nhien
            # va cai kia khong phai do dot bien
            if (num_dad == 0 and num_mom == 0) or \
                 (num_dad == 2 and num_mom == 2):
                effect = mutation * (1 - mutation)

            # neu 1 trong 2 bo me co nguoi co 2 gen nguoi kia khong co gen
            # nguoi co 2 gen truyen va nguoi kia khong hoac nguoc lai
            elif (num_dad == 2 and num_mom == 0) or \
                    (num_dad == 0 and num_mom == 2):
                effect = (1 - mutation) * (1 - mutation) + mutation * mutation

            # neu ca bo va me deu co 1 gen thi 1 trong so chung truyen voi prob 0.5
            # cai kia khong co prob 0.5
            # va nguoc lai
            elif (num_dad == 1 and num_mom == 1):
                effect = 2 * 0.5 * 0.5

            # trong phần còn lại của các trường hợp
            # hoặc truyền do đột biến (0) hoặc không do đột biến (2)
            # hoặc truyền tự nhiên (2) hoặc không tự nhiên (0)
            # 50% cơ hội truyền hoặc không truyền (1)
            # (0, 1) (1, 0) (2, 1) (1, 2)
            else:
                effect = mutation * 0.5 + (1 - mutation) * 0.5
            # neu dua tre co 2 gen thi giong nhu doi voi 0 gen
            # nhung dot bien tro thanh (1- dot bien)
            # va nguoc lai
            # boi vi 0 va 2 la truong hop nguoc nhau
            # 0 khong bao gio truyen va 2 luon truyen
        else:

            if num_dad == 0 and num_mom == 0:
                effect = mutation * mutation

            elif num_dad == 2 and num_mom == 2:
                effect = (1 - mutation) * (1 - mutation)

            elif (num_dad == 2 and num_mom == 0) or \
                    (num_dad == 0 and num_mom == 2):
                effect = mutation * (1 - mutation)

            elif (num_dad == 0 and num_mom == 1) or \
                    (num_dad == 1 and num_mom == 0):
                effect = mutation * 0.5

            elif (num_dad == 2 and num_mom == 1) or \
                    (num_dad == 1 and num_mom == 2):
                effect = (1 - mutation) * 0.5
            # (1,1)
            else:
                effect = 0.5 * 0.5
        conses *= effect * PROBS['trait'][num][have]
    return antes * conses


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.

    Thêm vào `xác suất` một xác suất chung mới` p`.
    Mỗi người nên được cập nhật phân bố "gen" và "đặc điểm" của họ.
    Giá trị nào cho mỗi phân phối được cập nhật phụ thuộc vào việc
    người đó ở trong `have_gene` và` have_trait`, tương ứng.
    """
    for person in probabilities:
        num = 1 * (person in one_gene) + 2 * (person in two_genes)
        have = (person in have_trait)
        probabilities[person]["gene"][num] += p
        probabilities[person]["trait"][have] += p

    return


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).

    Cập nhật `xác suất` sao cho mỗi phân phối xác suất
    được chuẩn hóa (nghĩa là tổng bằng 1, với tỷ lệ tương đối giống nhau).
    """
    for person in probabilities:
        sum = 0
        for i in range(3):
            sum += probabilities[person]["gene"][i]

        for i in range(3):
            probabilities[person]["gene"][i] = \
                probabilities[person]["gene"][i] / sum

        sum = probabilities[person]["trait"][True] + \
              probabilities[person]["trait"][False]

        probabilities[person]["trait"][True] = \
            probabilities[person]["trait"][True] / sum

        probabilities[person]["trait"][False] = \
            probabilities[person]["trait"][False] / sum

    return



if __name__ == "__main__":
    main()

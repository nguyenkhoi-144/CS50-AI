import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
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
    """
    # for clarity, compute the joint probability for parents and children separately
    # ergo, two sets of people are defined: parents and children

    # để rõ ràng, hãy tính toán xác suất chung cho cha mẹ và con cái riêng biệt
    # ergo, hai nhóm người được xác định: cha mẹ và con cái
    parents = set()
    children = set()

    for person in people:

        # if a person has no mother, the person has no father
        # this is based on the dataset in 'data/'
        # the person who has no mother (and father) is a parent

        # nếu một người không có mẹ, người đó không có cha
        # điều này dựa trên tập dữ liệu trong 'data /'
        # người không có mẹ (và cha) là cha mẹ
        if people[person]['mother'] == None:
            parents.add(person)
        else:
            children.add(person)

    # 'antes' computes probabilities of antecedents (parents)
    # this is not strictly required for calculation
    # single variable may have sufficed

    # 'antes' tính toán xác suất của tiền nhân (cha mẹ)
    # điều này không hoàn toàn bắt buộc để tính toán
    # biến đơn có thể đã đủ
    antes = 1
    for person in parents:
        # neat trick to calculate no. of genes
        # any person can have one or two genes but not both
        # if the person is in 'one_gene', it evaluates to True i.e., 1 and yields 1
        # if the person is in 'two_gene', it evaluates to True i.e., 1 and yields 2
        # when 'one_gene' evaluates to True, the other evaluates to False i.e., 0
        # and vice-versa
        # have is simply the boolean representing whether the person
        # has the trait or not, based on his/her presence in 'have_trait'

        # mẹo gọn gàng để tính toán không. gen
        # bất kỳ người nào cũng có thể có một hoặc hai gen nhưng không phải cả hai
        # nếu một người ở trong 'one_gene', nó sẽ đánh giá là True, tức là 1 và cho ra kết quả là 1
        # nếu một người ở trong 'two_gene', nó sẽ đánh giá là True, tức là 1 và cho kết quả là 2
        # khi 'one_gene' đánh giá là True, cái kia đánh giá là False, tức là 0
        # và ngược lại
        # have chỉ đơn giản là boolean đại diện cho việc người đó
        # có đặc điểm hay không, dựa trên sự hiện diện của anh ấy / cô ấy trong 'have_trait'


        num = 1 * (person in one_gene) + 2 * (person in two_genes)
        have = (person in have_trait)

        # PROBS dictionary is used to evaluate probabilities for the parents
        # Từ điển PROBS được sử dụng để đánh giá xác suất cho cha mẹ
        antes *= PROBS["gene"][num] * PROBS["trait"][num][have]

    # the consequences are the children, and their joint probability is present in conses
    # this is not strictly necessary either
    # hậu quả là những đứa trẻ, và xác suất chung của chúng xuất hiện ở các khuyết điểm
    # điều này cũng không cần thiết
    conses = 1
    for person in children:

        # get the child (person) 's mom and dad from the people dictionary
        # lấy mẹ và cha của đứa trẻ (người) từ từ điển mọi người
        mom = people[person]["mother"]
        dad = people[person]["father"]

        # as before, evaluate the number of genes for the parents and the child
        # also evaluate whether the child has a trait
        # như trước đây, đánh giá số lượng gen của cha mẹ và con
        # cũng đánh giá xem đứa trẻ có đặc điểm
        num = 1 * (person in one_gene) + 2 * (person in two_genes)
        num_mom = 1 * (mom in one_gene) + 2 * (mom in two_genes)
        num_dad = 1 * (dad in one_gene) + 2 * (dad in two_genes)
        have = (person in have_trait)

        # get the value of probability of mutation for ease of use later
        # lấy giá trị xác suất đột biến để tiện sử dụng sau này
        mutation = PROBS["mutation"]

        # if the child has no gene// nếu đứa trẻ không có gen
        if num == 0:

            # if neither dad nor mom has the gene
            # then, neither must undergo mutation
            # nếu cả bố và mẹ đều không có gen/ sau đó, không phải trải qua đột biến
            if num_dad == 0 and num_mom == 0:
                effect = (1 - mutation) * (1 - mutation)

            # if both dad and mom have 2 genes/nếu cả bố và mẹ đều có 2 gen
            # both must undergo mutatino so that none is transmitted
            # cả hai đều phải trải qua mutatino để không có gì được truyền đi
            elif (num_dad == 2 and num_mom == 2):
                effect = mutation * mutation

            # if either one of the parents has 2 genes and the other has 0 genes
            # the one with 2 genes must undergo mutation and the other must not
            # nếu một trong hai bố mẹ có 2 gen và người kia có 0 gen
            # anh ta một gen có 2 gen phải trải qua đột biến và gen kia không được
            elif (num_dad == 2 and num_mom == 0) or \
                    (num_dad == 0 and num_mom == 2):
                effect = mutation * (1 - mutation)

            # if either one fo the parents has 1 gene and the other has 0 genes
            # the one with the 1 gene must not transmit with prob 0.5
            # the other must not undergo mutation

            # nếu một trong hai bố mẹ có 1 gen và người kia có 0 gen
            # gen có 1 không được truyền với prob 0,5
            # cái kia không được đột biến

            elif (num_dad == 0 and num_mom == 1) or \
                    (num_dad == 1 and num_mom == 0):
                effect = (1 - mutation) * 0.5

            # if either one of the parents has 2 genes and the other has 1 gene
            # the one with 2 genes must undergo mutation
            # and other must not transmit with prob 0.5

            # nếu một trong hai bố mẹ có 2 gen và người kia có 1 gen
            # người có 2 gen phải bị đột biến
            # và khác không được truyền với prob 0.5
            elif (num_dad == 2 and num_mom == 1) or \
                    (num_dad == 1 and num_mom == 2):
                effect = mutation * 0.5

            # else both have 1 gene each and
            # must each not transmit with prob 0.5

            # nếu không, cả hai đều có 1 gen và
            # mỗi người không được truyền với prob 0.5
            else:
                effect = 0.5 * 0.5

        # if the child has one gene/nếu đứa trẻ có một gen
        elif num == 1:

            # if both parents have no genes
            # one of them must go mutation to transmit 1 and the other must not
            # if both parents have 2 genes
            # one of them transmits naturally and the other mustn't by mutation
            # nếu cả bố và mẹ đều không có gen
            # một trong số chúng phải đột biến để truyền 1 và còn lại không được
            # nếu cả bố và mẹ đều có 2 gen
            # một trong số chúng truyền tự nhiên và cái kia không phải do đột biến
            if (num_dad == 0 and num_mom == 0) or \
                    (num_dad == 2 and num_mom == 2):
                effect = mutation * (1 - mutation)

            # if one of the parents has 2 genes and the other has no genes
            # the one with 2 can transmit and the other can't, naturally
            # or
            # the one with 2 can't transmit and the other can, by mutation

            # nếu một trong hai bố mẹ có 2 gen và người kia không có gen
            # cái có 2 cái có thể truyền và cái kia không thể, tự nhiên
            # hoặc
            # người có 2 không thể truyền và người kia có thể, do đột biến
            elif (num_dad == 2 and num_mom == 0) or \
                    (num_dad == 0 and num_mom == 2):
                effect = (1 - mutation) * (1 - mutation) + mutation * mutation

            # if both the parents have 1 gene
            # one of them transmits with prob 0.5
            # the other doesn't with prob 0.5
            # and vice-versa

            # nếu cả bố và mẹ đều có 1 gen
            # một trong số chúng truyền với prob 0.5
            # cái kia không có prob 0.5
            # và ngược lại
            elif (num_dad == 1 and num_mom == 1):
                effect = 2 * 0.5 * 0.5

            # in the rest of the cases
            # either transmit by mutation(0) or don't by mutation(2)
            # either transmit naturally(2) or don't naturally(0)
            # 50% chance of transmitting or not transmitting(1)
            # (0, 1) (1, 0) (2, 1) (1, 2)

            # trong phần còn lại của các trường hợp
            # hoặc truyền do đột biến (0) hoặc không do đột biến (2)
            # hoặc truyền tự nhiên (2) hoặc không tự nhiên (0)
            # 50% cơ hội truyền hoặc không truyền (1)
            # (0, 1) (1, 0) (2, 1) (1, 2)
            else:
                effect = mutation * 0.5 + (1 - mutation) * 0.5

        # if the child has 2 genes
        # same as for 0 genes
        # but mutation becomes (1 - mutation)
        # and vice-versa
        # because 0 and 2 are opposite cases
        # 0 never transmits and 2 always transmits

        # nếu đứa trẻ có 2 gen
        # giống như đối với 0 gen
        # nhưng đột biến trở thành (1 - đột biến)
        # và ngược lại
        # bởi vì 0 và 2 là trường hợp ngược nhau
        # 0 không bao giờ truyền và 2 luôn truyền
        else:

            if num_dad == 0 and num_mom == 0:
                effect = mutation * mutation

            elif (num_dad == 2 and num_mom == 2):
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

            # (1, 1)
            else:
                effect = 0.5 * 0.5

        conses *= effect * PROBS["trait"][num][have]

    return antes * conses


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
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

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

    # ????? r?? r??ng, h??y t??nh to??n x??c su???t chung cho cha m??? v?? con c??i ri??ng bi???t
    # ergo, hai nh??m ng?????i ???????c x??c ?????nh: cha m??? v?? con c??i
    parents = set()
    children = set()

    for person in people:

        # if a person has no mother, the person has no father
        # this is based on the dataset in 'data/'
        # the person who has no mother (and father) is a parent

        # n???u m???t ng?????i kh??ng c?? m???, ng?????i ???? kh??ng c?? cha
        # ??i???u n??y d???a tr??n t???p d??? li???u trong 'data /'
        # ng?????i kh??ng c?? m??? (v?? cha) l?? cha m???
        if people[person]['mother'] == None:
            parents.add(person)
        else:
            children.add(person)

    # 'antes' computes probabilities of antecedents (parents)
    # this is not strictly required for calculation
    # single variable may have sufficed

    # 'antes' t??nh to??n x??c su???t c???a ti???n nh??n (cha m???)
    # ??i???u n??y kh??ng ho??n to??n b???t bu???c ????? t??nh to??n
    # bi???n ????n c?? th??? ???? ?????
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

        # m???o g???n g??ng ????? t??nh to??n kh??ng. gen
        # b???t k??? ng?????i n??o c??ng c?? th??? c?? m???t ho???c hai gen nh??ng kh??ng ph???i c??? hai
        # n???u m???t ng?????i ??? trong 'one_gene', n?? s??? ????nh gi?? l?? True, t???c l?? 1 v?? cho ra k???t qu??? l?? 1
        # n???u m???t ng?????i ??? trong 'two_gene', n?? s??? ????nh gi?? l?? True, t???c l?? 1 v?? cho k???t qu??? l?? 2
        # khi 'one_gene' ????nh gi?? l?? True, c??i kia ????nh gi?? l?? False, t???c l?? 0
        # v?? ng?????c l???i
        # have ch??? ????n gi???n l?? boolean ?????i di???n cho vi???c ng?????i ????
        # c?? ?????c ??i???m hay kh??ng, d???a tr??n s??? hi???n di???n c???a anh ???y / c?? ???y trong 'have_trait'


        num = 1 * (person in one_gene) + 2 * (person in two_genes)
        have = (person in have_trait)

        # PROBS dictionary is used to evaluate probabilities for the parents
        # T??? ??i???n PROBS ???????c s??? d???ng ????? ????nh gi?? x??c su???t cho cha m???
        antes *= PROBS["gene"][num] * PROBS["trait"][num][have]

    # the consequences are the children, and their joint probability is present in conses
    # this is not strictly necessary either
    # h???u qu??? l?? nh???ng ?????a tr???, v?? x??c su???t chung c???a ch??ng xu???t hi???n ??? c??c khuy???t ??i???m
    # ??i???u n??y c??ng kh??ng c???n thi???t
    conses = 1
    for person in children:

        # get the child (person) 's mom and dad from the people dictionary
        # l???y m??? v?? cha c???a ?????a tr??? (ng?????i) t??? t??? ??i???n m???i ng?????i
        mom = people[person]["mother"]
        dad = people[person]["father"]

        # as before, evaluate the number of genes for the parents and the child
        # also evaluate whether the child has a trait
        # nh?? tr?????c ????y, ????nh gi?? s??? l?????ng gen c???a cha m??? v?? con
        # c??ng ????nh gi?? xem ?????a tr??? c?? ?????c ??i???m
        num = 1 * (person in one_gene) + 2 * (person in two_genes)
        num_mom = 1 * (mom in one_gene) + 2 * (mom in two_genes)
        num_dad = 1 * (dad in one_gene) + 2 * (dad in two_genes)
        have = (person in have_trait)

        # get the value of probability of mutation for ease of use later
        # l???y gi?? tr??? x??c su???t ?????t bi???n ????? ti???n s??? d???ng sau n??y
        mutation = PROBS["mutation"]

        # if the child has no gene// n???u ?????a tr??? kh??ng c?? gen
        if num == 0:

            # if neither dad nor mom has the gene
            # then, neither must undergo mutation
            # n???u c??? b??? v?? m??? ?????u kh??ng c?? gen/ sau ????, kh??ng ph???i tr???i qua ?????t bi???n
            if num_dad == 0 and num_mom == 0:
                effect = (1 - mutation) * (1 - mutation)

            # if both dad and mom have 2 genes/n???u c??? b??? v?? m??? ?????u c?? 2 gen
            # both must undergo mutatino so that none is transmitted
            # c??? hai ?????u ph???i tr???i qua mutatino ????? kh??ng c?? g?? ???????c truy???n ??i
            elif (num_dad == 2 and num_mom == 2):
                effect = mutation * mutation

            # if either one of the parents has 2 genes and the other has 0 genes
            # the one with 2 genes must undergo mutation and the other must not
            # n???u m???t trong hai b??? m??? c?? 2 gen v?? ng?????i kia c?? 0 gen
            # anh ta m???t gen c?? 2 gen ph???i tr???i qua ?????t bi???n v?? gen kia kh??ng ???????c
            elif (num_dad == 2 and num_mom == 0) or \
                    (num_dad == 0 and num_mom == 2):
                effect = mutation * (1 - mutation)

            # if either one fo the parents has 1 gene and the other has 0 genes
            # the one with the 1 gene must not transmit with prob 0.5
            # the other must not undergo mutation

            # n???u m???t trong hai b??? m??? c?? 1 gen v?? ng?????i kia c?? 0 gen
            # gen c?? 1 kh??ng ???????c truy???n v???i prob 0,5
            # c??i kia kh??ng ???????c ?????t bi???n

            elif (num_dad == 0 and num_mom == 1) or \
                    (num_dad == 1 and num_mom == 0):
                effect = (1 - mutation) * 0.5

            # if either one of the parents has 2 genes and the other has 1 gene
            # the one with 2 genes must undergo mutation
            # and other must not transmit with prob 0.5

            # n???u m???t trong hai b??? m??? c?? 2 gen v?? ng?????i kia c?? 1 gen
            # ng?????i c?? 2 gen ph???i b??? ?????t bi???n
            # v?? kh??c kh??ng ???????c truy???n v???i prob 0.5
            elif (num_dad == 2 and num_mom == 1) or \
                    (num_dad == 1 and num_mom == 2):
                effect = mutation * 0.5

            # else both have 1 gene each and
            # must each not transmit with prob 0.5

            # n???u kh??ng, c??? hai ?????u c?? 1 gen v??
            # m???i ng?????i kh??ng ???????c truy???n v???i prob 0.5
            else:
                effect = 0.5 * 0.5

        # if the child has one gene/n???u ?????a tr??? c?? m???t gen
        elif num == 1:

            # if both parents have no genes
            # one of them must go mutation to transmit 1 and the other must not
            # if both parents have 2 genes
            # one of them transmits naturally and the other mustn't by mutation
            # n???u c??? b??? v?? m??? ?????u kh??ng c?? gen
            # m???t trong s??? ch??ng ph???i ?????t bi???n ????? truy???n 1 v?? c??n l???i kh??ng ???????c
            # n???u c??? b??? v?? m??? ?????u c?? 2 gen
            # m???t trong s??? ch??ng truy???n t??? nhi??n v?? c??i kia kh??ng ph???i do ?????t bi???n
            if (num_dad == 0 and num_mom == 0) or \
                    (num_dad == 2 and num_mom == 2):
                effect = mutation * (1 - mutation)

            # if one of the parents has 2 genes and the other has no genes
            # the one with 2 can transmit and the other can't, naturally
            # or
            # the one with 2 can't transmit and the other can, by mutation

            # n???u m???t trong hai b??? m??? c?? 2 gen v?? ng?????i kia kh??ng c?? gen
            # c??i c?? 2 c??i c?? th??? truy???n v?? c??i kia kh??ng th???, t??? nhi??n
            # ho???c
            # ng?????i c?? 2 kh??ng th??? truy???n v?? ng?????i kia c?? th???, do ?????t bi???n
            elif (num_dad == 2 and num_mom == 0) or \
                    (num_dad == 0 and num_mom == 2):
                effect = (1 - mutation) * (1 - mutation) + mutation * mutation

            # if both the parents have 1 gene
            # one of them transmits with prob 0.5
            # the other doesn't with prob 0.5
            # and vice-versa

            # n???u c??? b??? v?? m??? ?????u c?? 1 gen
            # m???t trong s??? ch??ng truy???n v???i prob 0.5
            # c??i kia kh??ng c?? prob 0.5
            # v?? ng?????c l???i
            elif (num_dad == 1 and num_mom == 1):
                effect = 2 * 0.5 * 0.5

            # in the rest of the cases
            # either transmit by mutation(0) or don't by mutation(2)
            # either transmit naturally(2) or don't naturally(0)
            # 50% chance of transmitting or not transmitting(1)
            # (0, 1) (1, 0) (2, 1) (1, 2)

            # trong ph???n c??n l???i c???a c??c tr?????ng h???p
            # ho???c truy???n do ?????t bi???n (0) ho???c kh??ng do ?????t bi???n (2)
            # ho???c truy???n t??? nhi??n (2) ho???c kh??ng t??? nhi??n (0)
            # 50% c?? h???i truy???n ho???c kh??ng truy???n (1)
            # (0, 1) (1, 0) (2, 1) (1, 2)
            else:
                effect = mutation * 0.5 + (1 - mutation) * 0.5

        # if the child has 2 genes
        # same as for 0 genes
        # but mutation becomes (1 - mutation)
        # and vice-versa
        # because 0 and 2 are opposite cases
        # 0 never transmits and 2 always transmits

        # n???u ?????a tr??? c?? 2 gen
        # gi???ng nh?? ?????i v???i 0 gen
        # nh??ng ?????t bi???n tr??? th??nh (1 - ?????t bi???n)
        # v?? ng?????c l???i
        # b???i v?? 0 v?? 2 l?? tr?????ng h???p ng?????c nhau
        # 0 kh??ng bao gi??? truy???n v?? 2 lu??n truy???n
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

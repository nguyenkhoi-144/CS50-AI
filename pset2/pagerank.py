import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    prop_dist = {}

    #kiem tra xem trang co lien ket di khong
    dict_len = len(corpus.keys())
    pages_len = len(corpus[page])

    if len(corpus[page]) < 1:
        #khong co trang chuyen di , chon ngau nhien tu cac trang co the
        for key in corpus.keys():
            prop_dist[key] = 1 / dict_len
    else:
        #co trang gui di thi tinh toan phan phoi
        random_factor = (1 - damping_factor) / dict_len
        even_factor = damping_factor / pages_len

        for key in corpus.keys():
            if key not in corpus[page]:
                prop_dist[key] = random_factor
            else:
                prop_dist[key] = even_factor + random_factor
    return prop_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # chuan bi tu dien voi so luong mau == 0
    samples_dict = corpus.copy()
    for i in samples_dict:
        samples_dict[i] = 0
    sample = None

    # lap lai n lan
    for _ in range(n):
        if sample:
            #mau truoc co san , chon su dung mo hinh chuyen tiep
            dist = transition_model(corpus, sample, damping_factor)
            dist_lst = list(dist.keys())
            dist_weights = [dist[i] for i in dist]
            sample = random.choices(dist_lst, dist_weights, k = 1)[0]
        else:
            #khong co mau truoc , chon ngau nhien
            sample = random.choice(list(corpus.keys()))
        #dem tung mau
        samples_dict[sample] += 1
        #chuyen so luong mau thanh phan tram
    for item in samples_dict:
        samples_dict[item] /= n
    return  samples_dict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages_number = len(corpus)
    old_dict = {}
    new_dict = {}

    # assigning each page a rank of 1/n, where n is total number of pages in the corpus
    # g??n cho m???i trang th??? h???ng l?? 1 / n, trong ???? n l?? t???ng s??? trang trong kho t??i li???u
    for page in corpus:
        old_dict[page] = 1 / pages_number

    # repeatedly calculating new rank values basing on all of the current rank values
    # li??n t???c t??nh to??n c??c gi?? tr??? x???p h???ng m???i d???a tr??n t???t c??? c??c gi?? tr??? x???p h???ng hi???n t???i
    while True:
        for page in corpus:
            temp = 0
            for linking_page in corpus:
                # check if page links to our page
                # ki???m tra xem trang c?? li??n k???t ?????n trang c???a ch??ng t??i kh??ng
                if page in corpus[linking_page]:
                    temp += (old_dict[linking_page] / len(corpus[linking_page]))
                # if page has no links, interpret it as having one link for every other page
                # n???u trang kh??ng c?? li??n k???t, h??y gi???i th??ch n?? l?? c?? m???t li??n k???t cho m???i trang kh??c
                if len(corpus[linking_page]) == 0:
                    temp += (old_dict[linking_page]) / len(corpus)
            temp *= damping_factor
            temp += (1 - damping_factor) / pages_number

            new_dict[page] = temp

        difference = max([abs(new_dict[x] - old_dict[x]) for x in old_dict])
        if difference < 0.001:
            break
        else:
            old_dict = new_dict.copy()

    return old_dict


if __name__ == "__main__":
    main()

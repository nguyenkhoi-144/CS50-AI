import os
import random
import re
import sys
import numpy

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
    # probability-list to initialize weights for random no. generator
    # danh sách xác suất để khởi tạo trọng số cho số ngẫu nhiên. máy phát điện
    p = [damping_factor, 1 - damping_factor]
    model = dict()
    linked = set()
    unlinked = set()

    # from the corpus, get the list of pages that the current page is linked to
    # and the list of pages the current page is not linked to
    # also set the transition model probabiilties to 0.0 initially

    # từ kho tài liệu, lấy danh sách các trang mà trang hiện tại được liên kết đến
    # và danh sách các trang mà trang hiện tại không được liên kết cũng đặt xác
    # suất mô hình chuyển đổi ban đầu là 0,0
    for key, value in corpus.items():

        model[key] = 0.0

        if key != page:
            continue

        linked = value
        unlinked = set()
        for key in corpus:
            if key in linked:
                continue
            unlinked.add(key)

    # each page starts with a base probability of reach of (1 - damping_factor)/total_pages
    # then each page linked to this page gets an additional probability of
    # damping_factor / no_of_links
    # mỗi trang bắt đầu với xác suất tiếp cận cơ bản là (1 - voiding_factor) / total_pages,
    # sau đó mỗi trang được liên kết với trang này sẽ có thêm một xác suất
    # là voiding_factor / no_of_links
    linked_count = len(linked)
    unlinked_count = len(unlinked)
    total = linked_count + unlinked_count
    base_prob = p[1] / total
    for key in model:

        if key in linked:
            model[key] = base_prob + damping_factor / linked_count
        else:
            model[key] = base_prob

    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    rank = dict()

    # initialize rank of each page in the corpus to 0.0
    # khởi tạo thứ hạng của mỗi trang trong kho ngữ liệu thành 0,0
    for key in corpus:
        rank[key] = 0.0

    # start with a random sample page and set its probability to 1/n
    # bắt đầu với một trang mẫu ngẫu nhiên và đặt xác suất của nó thành 1 / n
    # n = no. of samples
    sample = random.choices(list(corpus))[0]
    rank[sample] += (1 / n)

    # based on the transition model generated by this page, go to the next page
    # increment the rank of the next page by 1 / n

    #dựa trên mô hình chuyển đổi được tạo bởi trang này, hãy chuyển đến
    # trang tiếp theo
    # tăng thứ hạng của trang tiếp theo lên 1 / n
    for i in range(1, n):

        model = transition_model(corpus, sample, damping_factor)
        next_pages = []
        probabilities = []
        for key, value in model.items():
            next_pages.append(key)
            probabilities.append(value)

        sample = random.choices(next_pages, weights=probabilities)[0]
        rank[sample] += (1 / n)

    return rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    ranks = dict()

    # set threshold of convergence to be +/- 0.001
    # đặt ngưỡng hội tụ là +/- 0,001
    threshold = 0.0005

    # N = no. of pages // N = không. trong số các trang
    # set the rank of each page to be 1 / N //đặt thứ hạng của mỗi trang là 1 / N
    N = len(corpus)
    for key in corpus:
        ranks[key] = 1 / N

    # for each page, determine which/how many other pages link to it
    # then, apply the PageRank formula
    # if change (new_rank, old_rank) < threshold update counter
    # if by the end of the loop, counter == N,
    # it means that the change in rank for each page in the corpus was within the threshold
    # so end the loop
    # return rank

    # cho mỗi trang, xác định xem / có bao nhiêu trang khác liên kết đến trang đó
    # , sau đó áp dụng công thức Xếp hạng trang.
    # nếu thay đổi (new_rank, old_rank) <ngưỡng cập nhật counter.
    # if đến cuối vòng lặp, counter == N,
    # điều đó có nghĩa là sự thay đổi về thứ hạng cho mỗi trang trong kho tài
    # liệu nằm trong ngưỡng nên kết thúc vòng lặp trả về thứ hạng
    while True:

        count = 0

        for key in corpus:

            new = (1 - damping_factor) / N
            sigma = 0

            for page in corpus:

                if key in corpus[page]:
                    num_links = len(corpus[page])
                    sigma = sigma + ranks[page] / num_links

            sigma = damping_factor * sigma
            new += sigma

            if abs(ranks[key] - new) < threshold:
                count += 1

            ranks[key] = new

        if count == N:
            break

    return ranks


if __name__ == "__main__":
    main()
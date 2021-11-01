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
    Phân tích cú pháp một thư mục các trang HTML và kiểm tra các liên kết đến các trang khác.
    Trả về từ điển trong đó mỗi khóa là một trang và các giá trị là
    danh sách tất cả các trang khác trong kho tài liệu được liên kết với trang.
    """
    pages = dict()

    # Extract all links from HTML files||Trích xuất tất cả các liên kết từ các tệp HTML
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus||Chỉ bao gồm các liên kết đến các trang khác trong kho tài liệu
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
    Trả về phân phối xác suất qua trang sẽ truy cập tiếp theo,
    đưa ra một trang hiện tại.

    Trả về phân phối xác suất qua trang sẽ truy cập tiếp theo,
    đưa ra một trang hiện tại.

    Với xác suất `voiding_factor`, hãy chọn ngẫu nhiên một liên kết
    được liên kết với `trang`. Với xác suất `1 - hệ số giảm chấn`, hãy chọn
    một liên kết được chọn ngẫu nhiên từ tất cả các trang trong kho tài liệu.
    Trả lời về trình phân phối qua trang sẽ truy cập vào,
    đưa ra một hiện trang.
    """

    prop_dist = {}

    # check if page has outgoing links||kiểm tra xem trang có liên kết đi không
    dict_len = len(corpus.keys())
    pages_len = len(corpus[page])

    if len(corpus[page]) < 1:
        # no outgoing pages, choosing randomly from all possible pages
        #không có trang gửi đi, chọn ngẫu nhiên từ tất cả các trang có thể
        for key in corpus.keys():
            prop_dist[key] = 1 / dict_len

    else:
        # there are outgoing pages, calculating distribution
        # có các trang gửi đi, tính toán phân phối
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
    Trả về các giá trị Xếp hạng Trang cho mỗi trang bằng cách lấy mẫu `n` trang
    theo mô hình chuyển tiếp, bắt đầu với một trang ngẫu nhiên.

    Trả lại từ điển trong đó khóa là tên trang và giá trị là
    giá trị Xếp hạng Trang ước tính của họ (giá trị từ 0 đến 1). Tất cả các
    Giá trị Xếp hạng trang phải tổng bằng 1.
    """

    # prepare dictionary with number of samples == 0
    #chuẩn bị từ điển với số lượng mẫu == 0
    samples_dict = corpus.copy()
    for i in samples_dict:
        samples_dict[i] = 0
    sample = None

    # itearting n times
    #lặp lại n lần
    for _ in range(n):
        if sample:
            # previous sample is available, choosing using transition model
            # mẫu trước có sẵn, chọn sử dụng mô hình chuyển tiếp
            dist = transition_model(corpus, sample, damping_factor)
            dist_lst = list(dist.keys())
            dist_weights = [dist[i] for i in dist]
            sample = random.choices(dist_lst, dist_weights, k=1)[0]
        else:
            # no previous sample, choosing randomly
            # không có mẫu trước, chọn ngẫu nhiên
            sample = random.choice(list(corpus.keys()))

        # count each sample
        #đếm từng mẫu
        samples_dict[sample] += 1

    # turn sample count to percentage
    #chuyển số lượng mẫu thành phần trăm
    for item in samples_dict:
        samples_dict[item] /= n

    return samples_dict


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    Trả lại giá trị Xếp hạng trang cho mỗi trang bằng cách cập nhật lặp đi lặp lại
    Các giá trị Xếp hạng trang cho đến khi hội tụ.

    Trả lại từ điển trong đó khóa là tên trang và giá trị là
    giá trị Xếp hạng Trang ước tính của họ (giá trị từ 0 đến 1). Tất cả các
    Giá trị Xếp hạng trang phải tổng bằng 1.
    """
    pages_number = len(corpus)
    old_dict = {}
    new_dict = {}

    # assigning each page a rank of 1/n, where n is total number of pages in the corpus
    #gán cho mỗi trang thứ hạng là 1 / n, trong đó n là tổng số trang trong kho tài liệu
    for page in corpus:
        old_dict[page] = 1 / pages_number

    # repeatedly calculating new rank values basing on all of the current rank values
    # liên tục tính toán các giá trị xếp hạng mới dựa trên tất cả các giá trị xếp hạng hiện tại
    while True:
        for page in corpus:
            temp = 0
            for linking_page in corpus:
                # check if page links to our page
                # kiểm tra xem trang có liên kết đến trang của chúng tôi không
                if page in corpus[linking_page]:
                    temp += (old_dict[linking_page] / len(corpus[linking_page]))
                # if page has no links, interpret it as having one link for every other page
                # nếu trang không có liên kết, hãy giải thích nó là có một liên kết cho mọi trang khác
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

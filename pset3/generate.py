import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate./Tạo tạo ô chữ CSP mới.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment./Trả về mảng 2D đại diện cho một nhiệm vụ đã cho.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal./In bài tập ô chữ vào thiết bị đầu cuối
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file./Lưu bài tập ô chữ vào tệp hình ảnh.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        Thực thi tính nhất quán của nút và vòng cung, sau đó giải quyết CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # cho mỗi biến trong từ điển tên miền
        # lấy tất cả các giá trị dược ánh xạ tới biến đó
        # xoá tất cả các giá trị có độ dài không khớp
        # độ dài của biến bắc buộc
        for variable in self.domains:
            domains = self.domains[variable].copy()
            for value in domains:
                if len(value) != variable.length:
                    self.domains[variable].remove(value)
        return

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.

        Làm cho biến cung `x` nhất quán với biến` y`.
        Để làm như vậy, hãy xóa các giá trị khỏi `self.domains [x]` mà không có
        giá trị tương ứng có thể có cho `y` trong` self.domains [y] `.

        Trả về True nếu một bản sửa đổi được thực hiện cho miền của `x`; trở lại
        Sai nếu không có sửa đổi nào được thực hiện.
        """
        # cho mỗi lần lặp lại của thuật toán AC-3 để duy trì tính nhất quán của cung
        # kiểm tra xem có cần sửa đổi nào không
        # nghĩa là nếu 'miền của x' phải được thu hẹp bằng cách xóa một giá trị
        # vì nó không có giá trị tương ứng thỏa đáng trong 'miền của y'
        '''
        function Revise(csp, X, Y):

            revised = false
            for x in X.domain:
                if no y in Y.domain satisfies constraint for (X,Y):
                    delete x from X.domain
                    revised = true
            return revised'''

        revised = False
        overlap = self.crossword.overlaps[x, y]
        if overlap == None:
            return revised
        i,j = overlap
        X = self.domains[x].copy()
        Y = self.domains[y]
        for x_value in X:
            satisfied = False
            for y_value in Y:
                if x_value != y_value and x_value[i] == y_value[j]
                    satisfied = True
                    break
            if not satisfied:
                self.domains[x].remove(x_value)
                revised = True
        return revised



    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.

        Cập nhật `self.domains` để mỗi biến đều nhất quán.
        Nếu `arcs` là Không, hãy bắt đầu với danh sách ban đầu của tất cả các cung trong bài toán.
        Nếu không, hãy sử dụng `arcs` làm danh sách ban đầu của các cung để tạo sự nhất quán.

        X = self.domains [x] .copy () mpty.
        Trả về True nếu tính nhất quán của vòng cung được thực thi và không có miền nào trống;
        trả về Sai nếu một hoặc nhiều tên miền kết thúc trống.
        """
        # có hai trường hợp:
        # case 1: cung tròn trống vì vậy hãy thực thi tính nhất quán của cung ở đầu
        # khởi tạo bộ hàng đợi bằng cách thêm tất cả các cạnh (cung) vào nó
        # cung (hoặc cạnh) chỉ đơn giản là một bộ (x, y) trong đó
        # x và y là các biến lân cận
        '''function
        AC - 3(csp):

        queue = all
        arcs in csp
        while queue non-empty:
            (X, Y) = Dequeue(queue)
        if Revise(csp, X, Y):
            if size of X.domain == 0:
                return false
        for each Z in X.neighbors - {Y}:
            Enqueue(queue, (Z, X))
        return true'''
        if arcs == None:
            q = set()
            for var in self.crossword.variables:
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    q.add((var, neighbor))
            while len(q) != 0:
                x,y = q.pop()
                if self.revise(x,y):
                    if len(self.domains[x]) == 0:
                        return False
                for x_neighbor in self.crossword.neighbors(x):
                    if x_neighbor != y:
                        q.add((x_neighbor, x))
            return True

        # trường hợp 2: cung không phải là Không có
        # điều này có nghĩa là ac3 được gọi bởi thuật toán backtrack
        # nên ac3 bây giờ sẽ tạo ra các suy luận cho các cung
        # nghĩa là nếu việc gán giá trị var = đã được thực hiện bởi backtrack
        # truy xuất tất cả các cung dẫn từ các vùng lân cận của 'var' đến 'var'
        # sau đó, thực thi tính nhất quán của vòng cung trên những hàng xóm này
        # nếu điều này có thể được thực hiện, sau đó trả lại các bài tập mới
        # nghĩa là những trường hợp miền (hàng xóm) = một giá trị
        # dưới dạng từ điển
        # ngoài ra, thay đổi tên miền self.domain ban đầu
        # nếu không thể duy trì tính nhất quán của hồ quang, trả về Không có
        # và không thay đổi tên miền self.domain ban đầu

        # hàm sửa đổi được viết lại ở đây để
        # việc thực thi 'thử nghiệm' này không làm ảnh hưởng đến các tên miền self.domain ban đầu
        '''function Backtrack(assignment, csp):

        if assignment complete:
            return assignment
        var = Select-Unassigned-Var(assignment, csp)
        for value in Domain-Values(var, assignment, csp):
            if value consistent with assignment:
                add {var = value} to assignment
                result = Backtrack(assignment, csp)
                if result ≠ failure:
                    return result
            remove {var = value} from assignment
        return failure'''
        def inference_revise(domainY, domainX, overlap):
            revise = False
            if overlap == None:
                return revise
            i, j = overlap # chỉ mục có giá trị giống nhau khi giao 2 biến
            Y = domainY.copy()
            for y_value in Y:
                satisfied = False
                for x_value in domainX:
                    if x_value != y_value and y_value[i] == x_value[j]:
                        satisfied = True
                        break
                if not satisfied:
                    domainY.remove(x_value)
                    revise True
            return revise
        q = set(arcs)
        domains = self.domains.copy()
        while len(q) != 0:
            y, x = q.pop()
            domainsX = domains[x]
            domainsY = domains[y]
            overlap = self.crossword.overlaps[y, x]
            if inference_revise(domainsY, domainsX, overlap):
                if len(domainsY) == 0:
                    return None
                for y_neighbor in self.crossword.neighbors(y):
                    if y_neighbor != x:
                        q.add((y_neighbor, y))

        # thực hiện thay đổi nếu nhất quán
        self.domains = domains.copy()
        # nhận nhiệm vụ mới nếu miền của y chỉ có 1 giá trị
        new_assignment = dict()
        for y, x in arcs:
            if len(self.domains[y]) == 1:
                new_assignment = [valua for value in self.domains[y][0]]

        return new_assignment





    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        Trả về True nếu `chỉ định` hoàn tất (tức là chỉ định một giá trị cho mỗi
        ô chữ); trả về False ngược lại.
        """
        # bài tập hoàn tất nếu
        # mỗi biến trong self.crossword.variables
        # đã được gán cho một giá trị trong từ điển phép gán
        # từ điển chỉ định chỉ lưu trữ một giá trị duy nhất
        # để xung đột không cần phải được kiểm tra ở đây
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        Trả về True nếu `bài tập` nhất quán (nghĩa là các từ phù hợp với ô chữ
        câu đố không có các nhân vật xung đột); trả về False ngược lại.
        """
        # kiểm tra xem mỗi giá trị được chỉ định có khác biệt không
        # đó là một giá trị duy nhất cho mỗi biến
        # đó là tổng số không. của các giá trị khác biệt == tổng số không. trong số các biến
        # cũng kiểm tra tính nhất quán của nút
        distinct = set()
        for variable in assignment:
            value = assignment[variable]
            distinct.add(value)
            if len(value) != variable.length:
                return False
        if len(distinct) != len(assignment):  #tổng số từ được thêm vào không bằng tổng số từ dòng cần điền
            return False
        # kiểm tra tính nhất quán của hồ quang, một cách riêng biệt
        # vì yêu cầu tính toán nhiều hơn
        # để có tính nhất quán cung:
        # ký tự thứ i của biến1 = ký tự thứ j của biến2
        # trong đó (i, j) là phần chồng chéo của biến1 và biến2
        for variable1 in assignment:
            for variable2 in assignment:
                if variable1 == variable2:
                    continue
                overlaps = self.crossword.overlaps[variable1, variable2]
                if overlaps == None:
                    continue
                i, j = overlaps
                if assignment[variable1][i] != assignment[variable2][j]:
                    return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        Trả về danh sách các giá trị trong miền của `var`, theo thứ tự
        số lượng giá trị mà họ loại trừ cho các biến lân cận.
        Ví dụ: giá trị đầu tiên trong danh sách phải là giá trị
        điều đó loại trừ các giá trị ít nhất trong số các hàng xóm của `var`.
        """
        # đầu tiên lấy những biến đó
        # chưa xuất hiện trong bài tập (chưa được chỉ định)
        # và cũng là hàng xóm của var (vavriable đang được xem xét)
        unassigned = set()
        neighbors = self.crossword.neighbors(var)
        for variable in self.crossword.variables:
            if variable not in assignment and variable in neighbors:
                unassigned.add(variable)
        # sau đó tạo một từ điển ánh xạ
        # một biến thành heuristic giá trị ít ràng buộc nhất của nó
        # đây, heuristic =
        # (số lượng biến bị ảnh hưởng) +
        # 90% trong số
        # có bao nhiêu giá trị riêng lẻ bị ảnh hưởng như một phần của
        # tất cả các giá trị trong miền
        cnt = dict()
        for value in self.domains[var]:
            constraint = 0.0
            for variable in unassigned:
                count = 0.0
                i, j = self.crossword.overlaps[var, variable]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        raise NotImplementedError


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

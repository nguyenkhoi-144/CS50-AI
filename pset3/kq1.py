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
        Return 2D array representing a given assignment.
        Trả về mảng 2D đại diện cho một nhiệm vụ đã cho.
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
        Print crossword assignment to the terminal.
        in gán ô chữ cho thiết bị đầu cuối.
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
        Save crossword assignment to an image file.
        Lưu bài tập ô chữ vào tệp hình ảnh.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas/Tạo một canvas trống
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
        Thực thi tính nhất quán của nút và vòng cung, sau đó giải quyết CSP
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
         Cập nhật `self.domains` để mỗi biến đều có nút nhất quán.
        (Xóa bất kỳ giá trị nào không nhất quán với một biến số
         hạn chế; trong trường hợp này là độ dài của từ.)
        """
        # For all variables: /Đối với tất cả các biến:
        for var in self.crossword.variables:
            # For each word length:/Đối với mỗi độ dài từ:
            for word in self.crossword.words:
                # Remove any values that are inconsistent with a variable's unary constraints;
                # in this case, the length of the word.
                # Loại bỏ bất kỳ giá trị nào không phù hợp với các ràng buộc một bậc của một biến;
                # trong trường hợp này là độ dài của từ.
                if len(word) is not var.length:
                    self.domains[var].remove(word)

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

        # var to keep track of revised words
        # var để theo dõi các từ đã sửa đổi
        revisions = []
        # Fetch overlaps for two arches
        # Tìm nạp chồng chéo cho hai vòm
        overlap = self.crossword.overlaps[x, y]

        # If the variables do not overlap, no revision needed
        # Nếu các biến không trùng lặp, không cần sửa đổi
        if overlap is None:
            return False

        # For each word combinations that fit into domains of variables
        # Đối với mỗi tổ hợp từ phù hợp với miền của các biến
        for word_x in self.domains[x].copy():
            can_combine = False
            for word_y in self.domains[y]:
                # Check that the words overlap with the same letter
                # Kiểm tra xem các từ có trùng lặp với cùng một chữ cái không
                if word_x is not word_y and word_x[overlap[0]] is word_y[overlap[1]]:
                    can_combine = True
                    break
            # If cannot be combined, remove values from `self.domains[x]` for which there is no
            # possible corresponding value for `y` in `self.domains[y]`.
            # Nếu không thể kết hợp, hãy xóa các giá trị khỏi `self.domains [x]` mà không có
            # giá trị tương ứng có thể có cho `y` trong` self.domains [y] `.
            if not can_combine:
                revisions.append(word_x)
                self.domains[x].remove(word_x)

        # Return True if a revision was made to the domain of `x`;
        # return False if no revision was made.
        # Trả về True nếu bản sửa đổi được thực hiện cho miền của `x`;
        # return False nếu không có bản sửa đổi nào được thực hiện.
        if len(revisions) > 0:
            return True
        return False

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
        Trả về True nếu tính nhất quán của vòng cung được thực thi và không có miền nào trống;
        trả về Sai nếu một hoặc nhiều tên miền kết thúc trống.
        """

        # If `arcs` is None, begin with initial list of all arcs in the problem.
        # Nếu `arcs` là Không, hãy bắt đầu với danh sách ban đầu của tất cả các cung trong bài toán.
        if arcs is None:
            arcs = []
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    arcs.append((x, y))

        # Otherwise, use `arcs` as the initial list of arcs to make consistent.
        # Nếu không, hãy sử dụng `arcs` làm danh sách ban đầu của các cung để tạo sự nhất quán.
        for x, y in arcs:
            # Update `self.domains` such that each variable is arc consistent.
            # Cập nhật `self.domains` sao cho mỗi biến đều nhất quán.
            if self.revise(x, y):
                for neighbor in self.crossword.neighbors(x):
                    arcs.append((x, neighbor))

        # Return True if arc consistency is enforced and no domains are empty;
        # return False if one or more domains end up empty.
        # Trả về True nếu tính nhất quán của cung được thực thi và không có miền nào trống;
        # return False nếu một hoặc nhiều tên miền trống.
        return len(self.domains[x]) > 0

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        Trả về True nếu `chỉ định` hoàn tất (tức là chỉ định một giá trị cho mỗi
        ô chữ); trả về False ngược lại.
        """

        # For each variable, check if it is in keys or in words in crosswords
        # Đối với mỗi biến, hãy kiểm tra xem nó nằm trong các phím hay trong các từ trong trò chơi ô chữ
        for var in self.crossword.variables:
            if var not in assignment.keys() or assignment[var] not in self.crossword.words:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        Trả về True nếu `bài tập` nhất quán (nghĩa là các từ phù hợp với ô chữ
        câu đố không có các nhân vật xung đột); trả về False ngược lại.
        """

        # For each variable check all consistency problems
        # Đối với mỗi biến, hãy kiểm tra tất cả các vấn đề về tính nhất quán
        for var_1 in assignment:
            word_1 = assignment[var_1]

            # If length does not match
            # Nếu độ dài không khớp
            if var_1.length is not len(word_1):
                return False

            # Two variable combination checks
            # Kiểm tra kết hợp hai biến
            for var_2 in assignment:
                word_2 = assignment[var_2]
                if var_1 != var_2:
                    # If two words are the same/# Nếu hai từ giống nhau
                    if word_1 is word_2:
                        return False

                    overlap = self.crossword.overlaps[var_1, var_2]
                    if overlap is not None:
                        x, y = overlap
                        # If overlapping letters are wrong/# Nếu các chữ cái chồng lên nhau là sai
                        if word_1[x] is not word_2[y]:
                            return False

        # Return True if `assignment` is consistent (i.e., words fit in crossword
        # puzzle without conflicting characters)
        # Trả về True nếu `bài tập` nhất quán (tức là các từ vừa với ô chữ
        # câu đố không có các ký tự xung đột)
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
        # Can be returned as is due to way of adding domains
        # Có thể được trả lại do cách thêm tên miền
        return self.domains[var]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        Trả về một biến chưa được gán chưa phải là một phần của `gán`.
        Chọn biến có số giá trị còn lại nhỏ nhất
        trong miền của nó. Nếu hòa, hãy chọn biến có giá trị cao nhất
        trình độ. Nếu có sự ràng buộc, bất kỳ biến số ràng buộc nào đều có thể chấp nhận được
        trả về giá trị.
        """
        # Return any variable remaining to be assigned (not in keys)
        # Trả lại bất kỳ biến nào còn lại sẽ được gán (không phải trong các khóa)
        for var in self.crossword.variables:
            if var not in assignment.keys():
                return var
        return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        Sử dụng Tìm kiếm theo dấu vết lùi, coi như đầu vào một nhiệm vụ một phần cho
        ô chữ và trả lại một bài tập hoàn chỉnh nếu có thể để làm như vậy.
        `gán` là một ánh xạ từ biến (khóa) thành từ (giá trị).
        Nếu không thể chỉ định, hãy trả về Không.
        """

        # Check if it is complete to end recursion
        # Kiểm tra xem nó đã hoàn tất chưa để kết thúc đệ quy
        if self.assignment_complete(assignment):
            return assignment

        # For each unassigned variable left
        # Đối với mỗi biến chưa được gán còn lại
        var = self.select_unassigned_variable(assignment)
        # Get values possible in domain
        # Nhận các giá trị có thể có trong miền
        for val in self.order_domain_values(var, assignment):
            # Try to assign value and check consistency
            # Cố gắng gán giá trị và kiểm tra tính nhất quán
            assignment[var] = val
            if self.consistent(assignment):
                # Recursion to find solution - if assignment makes solution impossible, cancel and pop from solution
                # Đệ quy để tìm giải pháp - nếu phép gán khiến giải pháp không thể thực hiện được, hãy hủy và bật khỏi giải pháp
                solution = self.backtrack(assignment)
                if solution is None:
                    assignment[var] = None
                else:
                    return solution

        # If no assignment is possible, return None.
        # Nếu không thể chuyển nhượng, trả về Không có.
        return None


def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments/# Phân tích cú pháp đối số dòng lệnh
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword/# Tạo ô chữ
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result/In kết quả
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
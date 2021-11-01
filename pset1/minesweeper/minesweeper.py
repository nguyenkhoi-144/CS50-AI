import copy
import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation//Đại diện trò chơi Minesweeper
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines//Đặt chiều rộng, chiều cao và số lượng mỏ ban đầu
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines//Khởi tạo một trường trống không có mỏ
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly//Thêm mỏ một cách ngẫu nhiên
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines//Lúc đầu, người chơi không tìm thấy mỏ
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        In bản trình bày dựa trên văn bản
        nơi đặt mỏ.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        Trả về số lượng mỏ được
        trong một hàng và cột của một ô nhất định,
        không bao gồm chính ô.
        """

        # Keep count of nearby mines//Giữ số lượng các mỏ lân cận
        count = 0

        # Loop over all cells within one row and column//Vòng qua tất cả các ô trong một hàng và cột
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself//Bỏ qua chính ô
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine/Cập nhật số lượng nếu ô trong giới hạn và là của tôi
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.//Kiểm tra xem tất cả các mỏ đã được gắn cờ hay chưa.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    Tuyên bố logic về trò chơi Minesweeper
    Một câu bao gồm một tập hợp các ô bảng,
    và đếm số lượng các ô đó là mỏ.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.//Trả về tập hợp tất cả các ô trong self.cells được biết là mỏ.
        """
        if self.count == len(self.cells):
            return self.cells


    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.//Trả về tập hợp tất cả các ô trong self.cells được biết là an toàn.
        """
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        Cập nhật trình bày tri thức nội bộ với thực tế là
        một tế bào được biết là một hầm mỏ.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        else:
            pass

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        Cập nhật trình bày tri thức nội bộ với thực tế là
        một tế bào được biết là an toàn.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        else:
            pass



class MinesweeperAI():
    """
    Minesweeper game player//Người chơi trò chơi Minesweeper
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width//Đặt chiều cao và chiều rộng ban đầu
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on/Theo dõi những ô nào đã được nhấp vào
        self.moves_made = set()

        # Keep track of cells known to be safe or mines//Theo dõi các ô được biết là an toàn hoặc có mỏ
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true//Danh sách các câu về trò chơi được biết là đúng
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        Đánh dấu ô là mỏ và cập nhật tất cả kiến thức
        để đánh dấu ô đó là của tôi.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        Đánh dấu một ô là an toàn và cập nhật tất cả kiến thức
        để đánh dấu ô đó là an toàn.

        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        Được gọi khi hội đồng quản trị Minesweeper cho chúng tôi biết, với một
        ô an toàn, có bao nhiêu ô lân cận có mìn.

        Hàm này nên:
            1) đánh dấu ô là một nước đi đã được thực hiện
            2) đánh dấu ô là an toàn
            3) thêm một câu mới vào cơ sở kiến ​​thức của AI
               dựa trên giá trị của `ô` và` số lượng`
            4) đánh dấu bất kỳ ô bổ sung nào là an toàn hoặc như mỏ
               nếu nó có thể được kết luận dựa trên cơ sở kiến ​​thức của AI
            5) thêm bất kỳ câu mới nào vào cơ sở kiến ​​thức của AI
               nếu chúng có thể được suy ra từ kiến ​​thức hiện có
        """
        # danh dau o la mot trong nhung nuoc di duoc thuc hien trong tro choi
        self.moves_made.add(cell)
        # danh dau o la o an toan, cap nhat bat ki trinh tu nao chua o do
        self.mark_safe(cell)
        # them cau moi vao co so kien thuc AI dua tren gia tri cua o vaf so luong
        cells = set()
        count_cpy = copy.deepcopy(count)
        #tra ve cac o hang xom
        close_cells = self.return_close_cells(cell)
        for cl in close_cells:
            if cl not in self.mines:
                count_cpy -= 1
            if cl not in self.mines | self.safes:
                # chi them cac o co trang thai khong xac dinh
                cells.add(cl)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        Trả về một ô an toàn để chọn trên bảng Minesweeper.

        Việc di chuyển phải được biết là an toàn, và chưa phải là một bước đi
        điều đó đã được thực hiện.

        Hàm này có thể sử dụng kiến ​​thức trong self.mines, self.safes
        và self.moves_made, nhưng không nên sửa đổi bất kỳ giá trị nào trong số đó.
        """
        raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        Trả về một nước đi cần thực hiện trên bảng Minesweeper.
        Nên chọn ngẫu nhiên trong số các ô:
            1) vẫn chưa được chọn, và
            2) không được biết là mỏ
        """
        raise NotImplementedError

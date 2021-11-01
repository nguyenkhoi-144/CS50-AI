import sys
import math

from PIL import Image, ImageFilter


# Đảm bảo sử dụng đúng
if len(sys.argv) != 2:
    sys.exit("Usage: Python do1.py filename")
# mở hình ảnh
image = Image.open(sys.argv[1]).convert("RGB")
# Lọc hình ảnh theo nhân phát hiện cạnh
filtered = image.filter(ImageFilter.Kernel(
    size=(3,3),
    kernel=[-1, -1, -1, -1, 8, -1, -1, -1, -1],
    scale=1
))
# hiểu thị kết quả hình ảnh
filtered.show()



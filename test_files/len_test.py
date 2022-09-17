from PIL import Image
from io import BytesIO
import hashlib



# file = '../UDP/__client__/default.png'
# f = open(file, 'rb').read()
# byteImg = BytesIO(f)
# img = Image.open(byteImg)

# for i, j in enumerate(range(100)):
#     print(i, j)
#     break

a = {'112', '21221'}
b = {'112', '21221'}
c = a.difference(b)
print(c)

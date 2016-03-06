import sys
import numpy as np
import cv2

img = np.zeros((200, 200, 3), np.uint8)
img[:,0.5*200:200] = (0,255,0)
cv2.line(img, (0, 0), (100, 100), (255, 0, 0), 1)
cv2.imshow('Show', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
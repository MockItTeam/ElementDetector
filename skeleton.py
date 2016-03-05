import cv2
import numpy as np
 
img = cv2.imread('img/test1.jpg',0)
size = np.size(img)
skel = np.zeros(img.shape,np.uint8)
 
ret,img = cv2.threshold(img,127,255,0)
element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
done = False
 
while( not done):
  eroded = cv2.erode(img,element)
  print ".."
  cv2.imshow("skel",erode)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

  temp = cv2.dilate(eroded,element)

  cv2.imshow("skel",temp)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

  temp = cv2.subtract(img,temp)

  cv2.imshow("skel",temp)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

  skel = cv2.bitwise_or(skel,temp)

  cv2.imshow("skel",skel)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

  img = eroded.copy()

  cv2.imshow("skel",img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
  
  if cv2.countNonZero(img) == size:
    done = True




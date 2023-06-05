# импортирование необходимых библиотек
import numpy as np
import cv2
import imutils
from PIL import Image
import math


# параметр для сканируемого изображения
#args_image = '1ugvyWqLmw0.jpg'

# прочитать изображение
#image = cv2.imread(args_image)
def scan(image):
    orig = image.copy()

    # конвертация изображения в градации серого. Это уберёт цветовой шум
    grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # размытие картинки, чтобы убрать высокочастотный шум
    # это помогает определить контур в сером изображении
    grayImageBlur = cv2.blur(grayImage,(3,3))

    # теперь производим определение границы по методу Canny
    edgedImage = cv2.Canny(grayImage, 100, 300, 3)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(edgedImage, cv2.MORPH_CLOSE, kernel)

    # найти контуры на обрезанном изображении, рационально организовать область
    # оставить только большие варианты
    allContours = cv2.findContours(closed.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    allContours = imutils.grab_contours(allContours)

    # сортировка контуров области по уменьшению и сохранение топ-1
    allContours = sorted(allContours, key=cv2.contourArea, reverse=True)[:1]
    # aппроксимация контура
    perimeter = cv2.arcLength(allContours[0], True)
    ROIdimensions = cv2.approxPolyDP(allContours[0], 0.1*perimeter, True)
    i = 4
    # изменение массива координат
    ROIdimensions = ROIdimensions.reshape(i,2 )

    # список удержания координат ROI
    rect = np.zeros((i,2), dtype='float32')

    # наименьшая сумма будет у верхнего левого угла,
    # наибольшая — у нижнего правого угла
    s = np.sum(ROIdimensions, axis=1)
    rect[0] = ROIdimensions[np.argmin(s)]
    rect[2] = ROIdimensions[np.argmax(s)]

    # верх-право будет с минимальной разницей
    # низ-лево будет иметь максимальную разницу
    diff = np.diff(ROIdimensions, axis=1)
    rect[1] = ROIdimensions[np.argmin(diff)]
    rect[3] = ROIdimensions[np.argmax(diff)]

    # верх-лево, верх-право, низ-право, низ-лево
    (tl, tr, br, bl) = rect

    # вычислить ширину ROI
    widthA = np.sqrt((tl[0] - tr[0])**2 + (tl[1] - tr[1])**2 )
    widthB = np.sqrt((bl[0] - br[0])**2 + (bl[1] - br[1])**2 )
    maxWidth = max(int(widthA), int(widthB))

    # вычислить высоту ROI
    heightA = np.sqrt((tl[0] - bl[0])**2 + (tl[1] - bl[1])**2 )
    heightB = np.sqrt((tr[0] - br[0])**2 + (tr[1] - br[1])**2 )
    maxHeight = max(int(heightA), int(heightB))

    # набор итоговых точек для обзора всего документа
    # размер нового изображения
    dst = np.array([
        [0,0],
        [maxWidth-1, 0],
        [maxWidth-1, maxHeight-1],
        [0, maxHeight-1]], dtype="float32")

    # вычислить матрицу перспективного преобразования и применить её
    transformMatrix = cv2.getPerspectiveTransform(rect, dst)

    # преобразовать ROI
    scan = cv2.warpPerspective(orig, transformMatrix, (maxWidth, maxHeight))

    # конвертация в серый
    scanGray = cv2.cvtColor(scan, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(scanGray, 170, 255, cv2.THRESH_BINARY)
    img_erode = cv2.erode(thresh, np.ones((10, 10), np.uint16), iterations=1)

    # получение контуров
    contours, hierarchy = cv2.findContours(img_erode, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    output = scan.copy()

    height, width = output.shape[:2]
    x1 = 32
    y1 = int(height*0.87)

    for idx, contour in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        if hierarchy[0][idx][3] == 0 and y > height*0.7:
            print(x, y, w, h)
            if x1 > x:
                x1 = x
            if y1 > y:
                y1 = y
    print(x1, y1)
    print(height, width)
    cv2.rectangle(output, (x1, y1), (width-1,height-1), (10, 0, 0), 1)
    area = scanGray[y1:height-1 , x1:width-1]
    return area


















































import cv2
import easygui
import numpy as np
import pandas as pd
from tkinter import messagebox as tkmsg
from tkinter import Tk as tK
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Button as tkbtn
import tkinter.font as tkFont
excel_dots = []


def single_counter():  # single well counter
    try:
        # grayscale filter, file explorer gui
        image = cv2.imread(easygui.fileopenbox(), cv2.IMREAD_GRAYSCALE)

        # apply a binary threshold. Pixels higher than 150 are black, lower than 150 are white
        thresh = 150
        bw = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)[1]
        # find contours (edges) in the black and white image. "Detects" dots
        cnts = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        dots = 0

        # loops through all counts that are detected
        # dots are small white contours
        for c in cnts:
            # calculates area that is enclosed by each contour detected
            area = cv2.contourArea(c)
            # if the contour area is bigger than this value (ie. Edge of wells) it will not count it as a dot,
            # and will colour it black
            if area > 250:
                cv2.drawContours(bw, [c], 0, 0, -1)
            elif 0 <= area <= 250:
                dots += 1

        plt.subplot(121), plt.imshow(image, cmap='gray')
        plt.title('Original Image', fontsize=25), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(bw, cmap='gray')
        plt.title('Counted Image, Counts ' + str(dots), fontsize=25), plt.xticks([]), plt.yticks([])
        plt.show()

    except:
        tkmsg.showinfo(title='Error', message='Not able to count dots')


def well_detector(in_image):  # for plate counter, detects wells
    green = np.uint8([[[0, 0, 108]]])
    hsv = cv2.cvtColor(green, cv2.COLOR_BGR2HSV)
    # turn yellow circles into dark red so that when gray scaling it will be a darker colour
    in_image[np.all(in_image == (0, 255, 255), axis=-1)] = (185, 0, 0)

    # convert image to HSV and remove areas where there are bright green spots caused by glare
    hsv_image = cv2.cvtColor(in_image, cv2.COLOR_BGR2HSV)
    green_low = np.array([50, 255, 0])
    green_high = np.array([70, 255, 255])
    green_mask = cv2.inRange(hsv_image, green_low, green_high)

    # convert image to HSV and remove areas where there are bright blue spots caused by glare
    blue_low = np.array([0, 255, 0])
    blue_high = np.array([0, 255, 255])
    blue_mask = cv2.inRange(hsv_image, blue_low, blue_high)

    # areas that are bright green and bright blue turned black
    in_image[green_mask > 0] = (0, 0, 0)
    in_image[blue_mask > 0] = (0, 0, 0)

    # turn image into grayscale from RGB
    gray = cv2.cvtColor(in_image, cv2.COLOR_BGR2GRAY)
    # set the settings for Hough Circles detection
    height, width = gray.shape[:2]
    min_r = int(width / 45)
    max_r = int(width / 11)
    min_dist = int(width / 7)
    # refer to hough circles document https://docs.opencv.org/3.4/d4/d70/tutorial_hough_circle.html
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 0.8, minDist=min_dist, param1=14, param2=25,
                               minRadius=min_r, maxRadius=max_r)
    # return coordinates and radius for each circle detected
    return circles


def dot_detector(in_image):  # for plate counter, detects dots
    try:
        # apply a binary threshold. Pixels higher than 150 are black, lower than 150 are white
        thresh = 150
        bw = cv2.threshold(in_image, thresh, 255, cv2.THRESH_BINARY)[1]
        # find contours (edges) in the black and white image. "Detects" dots
        cnts = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        dots = 0

        # loops through all counts that are detected
        # dots are small white contours
        for c in cnts:
            area = cv2.contourArea(c)
            if 1 <= area <= 25:# original 25
                dots += 1
            #elif 10 < area <= 25:
                #dots += 2
            else:
                cv2.drawContours(bw, [c], 0, 0, -1)
        # returns number of dots detected
        return dots, bw
    except:
        tkmsg.showinfo(title='Error', message='Not able to count plates')


def plate_counter():  # black background
    try:
        # selects image from file explorer
        image = cv2.imread(easygui.fileopenbox())
        # put image into well detector function to find wells aka "circles"
        circles = well_detector(image)
        list_dots = []
        excel_dots.clear()
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            circles = circles[np.argsort(circles[:, 0])]

            for i in range(0, circles.shape[0], 4):
                index = np.argsort(circles[i:i+4, 1])
                circles[i:i+4] = circles[i:i+4, :][index]

            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in circles:
                # create a mask of the original image with everything black
                mask = np.zeros_like(image)
                # draw a filled white circle at detected circle coordinates on mask
                cv2.circle(mask, (x, y), r, (255, 255, 255), -1)
                # draw a green circle at detected circle coordinates on final output image
                cv2.circle(image, (x, y), r, (0, 255, 0), 1)

                # XY Coordinates for numbers of counts to be put on image
                xc = x
                yc = y

                # Compare image and mask, takes pixels that are common to both
                roi = cv2.bitwise_and(image, mask)

                # turn mask into grayscale from RGB
                mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                # cropping the well, excluding all other background
                x, y, w, h = cv2.boundingRect(mask)
                result = roi[y:y + h, x:x + w]
                mask = mask[y:y + h, x:x + w]
                # turns the background black
                result[mask == 0] = (0, 0, 0)
                # final cropped image of the detected well
                result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

                # get number of dots from dot detector function
                dots, bw = dot_detector(result)
                list_dots.append(dots)

                # putting number of counts on plates
                cv2.putText(image, str(dots), (xc - 5, yc - 5), cv2.FONT_HERSHEY_SIMPLEX, 3, (36, 255, 12), 6)

                # for debugging
                # plt.subplot(121), plt.imshow(result, cmap='gray')
                # plt.subplot(122), plt.imshow(bw, cmap='gray')
                # plt.title(str(dots), fontsize=25), plt.xticks([]), plt.yticks([])

            # show the output image
            for i in range(0, len(list_dots), 4):
                sublist = list_dots[i:i + 4]
                excel_dots.append(sublist)
            display_image(image)
        # no wells detected error message box
        else:
            tkmsg.showinfo(title='Error', message='No wells detected')
    except:
        tkmsg.showinfo(title='Error', message='Not able to count plates')


def export_image():
    # button for exporting counted image to an excel file
    try:
        data_sheet = pd.DataFrame(np.transpose(excel_dots))
        data_sheet.to_excel(easygui.filesavebox(default='*.xlsx'))
        tkmsg.showinfo(title='Saved Successfully', message='Numbers exported to Excel')
    except:
        tkmsg.showinfo(title='Error', message='Not able to Export')


def display_image(in_image):
    # create a window for counted image to be displayed as well as buttons
    try:
        helv36 = tkFont.Font(family='Helvetica', size=30, weight=tkFont.BOLD)

        window = tK()
        window.title('Counted Picture')
        window.state('zoomed')

        fig = plt.figure(figsize=(7, 7),dpi=100)
        plt.imshow(in_image, cmap='gray')
        plt.xticks([]), plt.yticks([])

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        btn_close = tkbtn(window, text='Close!', command=window.destroy, width=50, font=helv36)
        btn_close.pack(side='bottom')
        btn_close.configure(width=50)

        btn_export = tkbtn(window, text='Export to Excel!', command= lambda: export_image(), width=50, font=helv36)
        btn_export.pack(side='bottom')
        btn_export.configure(width=50)

        window.mainloop()
    except:
        tkmsg.showinfo(title='Error', message='Not able to display picture')
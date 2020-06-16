import paho.mqtt.publish as publish
import cv2
import numpy as np
import math
import urllib.request

last_motion = 0  # 0: drop, 1: catch
send_flag = 0  # 0: send, 1: unsend

# smartphone's ip location, shot.jpg cannot be changed
URL = "http://LAN_ip:8080/shot.jpg"

def main():
    # Check what kind of colors of hand's stickers in the frame
    yellow_exist = 0
    blue_exist = 0
    green_exist = 0

    # globalize both variables
    global last_motion
    global send_flag

    while True:
        # request smartphone's cam(check smartphone's server on)
        img_arr = np.array(bytearray(urllib.request.urlopen(URL).read()),dtype=np.uint8)
        frame = cv2.imdecode(img_arr,-1)

        # initialize drop circle's position
        X = 0
        Y = 0

        # clone the frame for website location check
        frame1 = frame.copy()


        ## hand's catch and drop recognition
        # get the height and width of the frame
        (height, width) = frame.shape[:2]

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Mask for the color detection(yellow)
        lower_yellow = np.array([11, 91, 130])
        upper_yellow = np.array([37, 255, 255])

        # blue0611 = Low_[76, 88, 109], Upper_[125, 225, 255]
        lower_blue = np.array([76, 88, 109])
        upper_blue = np.array([125, 255, 255])

        # green0611 = Low_[38, 74, 57], Upper_[89, 255, 255]
        lower_green = np.array([38, 74, 57])
        upper_green = np.array([89, 255, 255])

        # Put on the color filter mask on frame
        mask_yellow = cv2.inRange(frame, lower_yellow, upper_yellow)
        mask_blue = cv2.inRange(frame, lower_blue, upper_blue)
        mask_green = cv2.inRange(frame, lower_green, upper_green)

        # Show the result of color filtering
        result_yellow = cv2.bitwise_and(frame, frame, mask=mask_yellow)
        result_blue = cv2.bitwise_and(frame, frame, mask=mask_blue)
        result_green = cv2.bitwise_and(frame, frame, mask=mask_green)
        frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)

        # draw contour and find point of catch location ------------------------------------------------------------
        # Draw the contours of YELLOW dots
        contours, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:
            cnt_max_yellow = max(contours, key=cv2.contourArea)
            # find blue contours (x,y,w,h) coordinate values
            (x_r, y_r, w_r, h_r) = cv2.boundingRect(cnt_max_yellow)

            if cv2.contourArea(cnt_max_yellow) < 500:
                yellow_exist = 0
            else:
                central_yellow = (int(x_r + w_r / 2), int(y_r + h_r / 2))
                cv2.rectangle(frame, (x_r, y_r), (x_r + w_r, y_r + h_r), (0, 0, 255), 2)
                cv2.circle(frame, central_yellow, 2, (255, 0, 0), 2)
                yellow_exist = 1

        # Draw the contours of BLUE dots
        contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:
            cnt_max_blue = max(contours, key=cv2.contourArea)
            # find blue contours (x,y,w,h) coordinate values
            (x_b, y_b, w_b, h_b) = cv2.boundingRect(cnt_max_blue)
            
            if cv2.contourArea(cnt_max_blue) < 500:
                blue_exist = 0
            else:
                central_blue = (int(x_b + w_b / 2), int(y_b + h_b / 2))
                cv2.rectangle(frame, (x_b, y_b), (x_b + w_b, y_b + h_b), (0, 0, 255), 2)
                cv2.circle(frame, central_blue, 2, (255, 0, 0), 2)
                blue_exist = 1

        if blue_exist == 1 and yellow_exist == 1:
            cv2.line(frame, central_blue, central_yellow, (255, 0, 0), 2)

        # # Draw the contours of BLUE dots
        contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:
            cnt_max_green = max(contours, key=cv2.contourArea)
            # find blue contours (x,y,w,h) coordinate values
            (x_g, y_g, w_g, h_g) = cv2.boundingRect(cnt_max_green)

            if cv2.contourArea(cnt_max_green) < 500:
                green_exist = 0
            else:
                central_green = (int(x_g + w_g / 2), int(y_g + h_g / 2))
                cv2.rectangle(frame, (x_g, y_g), (x_g + w_g, y_g + h_g), (0, 0, 255), 2)
                cv2.circle(frame, central_green, 2, (255, 0, 0), 2)
                green_exist = 1

        # Draw the line between green and blue spots
        if green_exist == 1 and blue_exist == 1:
            cv2.line(frame, central_blue, central_green, (255, 0, 0), 2)

        # 抓取設定---------------------------------------------------------------------
        # To ensure we has detected our hand
        # Find the angle between two lines
        # determine the range of angle which should be catch and drop
        if green_exist == 1 and blue_exist == 1 and yellow_exist == 1:
            print("it's your hand")
            cv2.line(frame, central_yellow, central_green, (255, 0, 0), 2)
            angle = det_angle(point_yellow=central_yellow, point_blue=central_blue, point_green=central_green)

            if angle > 15 and angle < 50:
                print('catch')
                circle_ini = (int((central_yellow[0] + central_green[0]) / 2), int((central_yellow[1] + central_green[1]) / 2))
                # circle_ini = (int(len(frame[1]) * 0.2), int(len(frame[0]) *0.2))
                cv2.circle(frame, circle_ini, 30, (255, 0, 0), -1)
                last_motion = 0
            elif angle > 50 and angle < 90:
                if last_motion == 0:
                    last_motion = 1
                    send_flag = 1
                    X = int((central_yellow[0] + central_green[0])/2)
                    Y = int((central_yellow[1] + central_green[1])/2)
                    pass
                print('drop')
            else:
                print('nothing')


        ## locate website four corners 
        # mask red's rgb
        L_black = np.array([0, 0, 125])
        M_black = np.array([100, 100, 255])
        mask = cv2.inRange(frame1, L_black, M_black)

        # filter
        k = np.ones((3, 3))
        eroded = cv2.erode(mask, k, iterations=2)
        dilated = cv2.dilate(eroded, k, iterations=2)
        edges = cv2.Canny(dilated, 70, 220)
        circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 80, param2=16, minRadius=10, maxRadius=100)

        try:
            for i in circles[0][:]:
                cv2.circle(frame, (i[0], i[1]), i[2], (255, 0, 0), 5)
        except:
            pass
        if send_flag == 1:
            try:
                calculate_pos(circles, X, Y)
                print(X)
                print(Y)
                print(circles)
                cv2.imshow("moment", frame)
            except:
                pass

        cv2.circle(frame, (X, Y), 3, (0, 255, 0), -1)
        cv2.imshow('img', frame)
        if cv2.waitKey(100) & 0xff == ord('q'):
            break
    cv2.destroyAllWindows()
    cap.release()


# 找到3點的夾角，並用來判斷是抓取或放開
def det_angle(point_yellow, point_blue, point_green):
    point_yellow = list(point_yellow)
    point_blue = list(point_blue)
    point_green = list(point_green)

    vector_1 = (point_yellow[0] - point_blue[0], point_yellow[1] - point_blue[1])
    vector_2 = (point_green[0] - point_blue[0], point_green[1] - point_blue[1])

    unit_vector_1 = vector_1 / np.linalg.norm(vector_1)
    unit_vector_2 = vector_2 / np.linalg.norm(vector_2)
    dot_product = np.dot(unit_vector_1, unit_vector_2)
    angle = np.arccos(dot_product)
    angle = math.degrees(angle)
    return angle


# calculate website's four corners's location
def calculate_pos(circles, X, Y):
    global send_flag
    if circles.shape[1] == 4:
        x = np.zeros(4)
        y = np.zeros(4)
        for i in range(0, 4):
            x[i] = circles[0][i][0] - X
            y[i] = circles[0][i][1] - Y
        for i in range(0, 4):
            for j in range(i + 1, 4):
                if x[i] < x[j]:
                    xtmp = x[i]
                    x[i] = x[j]
                    x[j] = xtmp
                if y[i] < y[j]:
                    ytmp = y[i]
                    y[i] = y[j]
                    y[j] = ytmp
        x = abs(x)
        y = abs(y)
        xr = (x[0] + x[1]) / 2
        xl = (x[2] + x[3]) / 2
        yt = (y[0] + y[1]) / 2
        yb = (y[2] + y[3]) / 2
        xrp = xr / (xr + xl)
        xlp = xl / (xr + xl)
        ytp = yt / (yt + yb)
        ybp = yb / (yt + yb)
        print('xl=%f  xr=%f  yt=%f  yb=%f' % (xlp, xrp, ytp, ybp))

        # send message to broker of mqtt
        mqtt_send(xlp, ybp)
        # close send's flag
        send_flag = 0



def mqtt_send(xRatio, yRatio):
    # publish a message then disconnect.
    host = "mqtt_broker_ip"
    topic = "topic_you_want_to_name"
    payload = str(xRatio) + ", " + str(yRatio)

    # If broker asks user/password.
    auth = {'username': "XXX", 'password': "XXX"}

    # If broker asks client ID.
    client_id = "XXX"

    publish.single(topic, payload, qos=1, hostname=host, auth=auth, client_id=client_id)


if __name__ == "__main__":
    main()

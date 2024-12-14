import os
import cvzone
import cv2
from cvzone.PoseModule import PoseDetector

# Setup
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Video file not found!")
    exit()

detector = PoseDetector()

shirtFolderPath = "Resources/Shirts"
listShirts = os.listdir(shirtFolderPath)
fixedRatio = 262 / 190
shirtRatioHeightWidth = 581 / 440
imageNumber = 0
imgButtonRight = cv2.imread("Resources/button.png", cv2.IMREAD_UNCHANGED)
imgButtonLeft = cv2.flip(imgButtonRight, 1)
counterRight = 0
counterLeft = 0
selectionSpeed = 10

while True:
    success, img = cap.read()
    if not success or img is None:
        print("End of video or read failure")
        break

    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)
    if lmList and len(lmList) > 16:
        lm11 = lmList[11][1:3]  # Left shoulder
        lm12 = lmList[12][1:3]  # Right shoulder

        # Load shirt image
        imgShirt = cv2.imread(os.path.join(shirtFolderPath, listShirts[imageNumber]), cv2.IMREAD_UNCHANGED)
        if imgShirt is None:
            print(f"Error: Could not load shirt image {listShirts[imageNumber]}")
            continue

        # Calculate shirt dimensions
        widthOfShirt = int((lm11[0] - lm12[0]) * fixedRatio)
        if widthOfShirt > 0:
            print(f"widthOfShirt: {widthOfShirt}, lm11: {lm11}, lm12: {lm12}")
            try:
                imgShirt = cv2.resize(imgShirt, (widthOfShirt, int(widthOfShirt * shirtRatioHeightWidth)))
                currentScale = (lm11[0] - lm12[0]) / 190
                offset = int(44 * currentScale), int(48 * currentScale)
                print(f"Offset: {offset}")
                img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
            except Exception as e:
                print(f"Error resizing or overlaying shirt: {e}")
        else:
            print(f"Invalid widthOfShirt: {widthOfShirt}")

    # Overlay buttons
    img = cvzone.overlayPNG(img, imgButtonRight, (1074, 293))
    img = cvzone.overlayPNG(img, imgButtonLeft, (72, 293))

    # Handle right button selection
    if lmList and len(lmList) > 16 and lmList[16][1] < 300:
        counterRight += 1
        cv2.ellipse(img, (139, 360), (66, 66), 0, 0, counterRight * selectionSpeed, (0, 255, 0), 20)
        if counterRight * selectionSpeed > 360:
            counterRight = 0
            if imageNumber < len(listShirts) - 1:
                imageNumber += 1
    # Handle left button selection
    elif lmList and len(lmList) > 15 and lmList[15][1] > 900:
        counterLeft += 1
        cv2.ellipse(img, (1138, 360), (66, 66), 0, 0, counterLeft * selectionSpeed, (0, 255, 0), 20)
        if counterLeft * selectionSpeed > 360:
            counterLeft = 0
            if imageNumber > 0:
                imageNumber -= 1
    else:
        counterRight = 0
        counterLeft = 0

    # Display frame
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()

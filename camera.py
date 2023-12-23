import cv2

# Open a connection to the webcam (0 represents the default camera)
cap = cv2.VideoCapture(0)

# Check if the webcam is opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Read a frame from the webcam
ret, frame = cap.read()

# Save the frame as an image file (you can use different formats like jpg, png, etc.)
cv2.imwrite('face_capture.png', frame)

# Release the webcam
cap.release()

print("Face capture completed and saved as 'face_capture.png'")

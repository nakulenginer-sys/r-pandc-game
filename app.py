from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import random
import time

app = Flask(__name__)

# =========================
# MediaPipe Setup
# =========================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

# =========================
# Webcam
# =========================

camera = cv2.VideoCapture(0)

# =========================
# Variables
# =========================

player_score = 0
computer_score = 0

player_choice = "Waiting..."
computer_choice = "Waiting..."
winner = "Start Game"

last_round_time = time.time()

# =========================
# Generate Frames
# =========================

def generate_frames():

    global player_score
    global computer_score
    global player_choice
    global computer_choice
    global winner
    global last_round_time

    tips = [4, 8, 12, 16, 20]

    while True:

        success, frame = camera.read()

        if not success:
            break

        frame = cv2.flip(frame, 1)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(rgb)

        finger_count = -1

        # =========================
        # Hand Detection
        # =========================

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                lm = hand_landmarks.landmark

                finger_count = 0

                # Thumb
                if lm[4].x < lm[3].x:
                    finger_count += 1

                # Fingers
                for tip in tips[1:]:

                    if lm[tip].y < lm[tip - 2].y:
                        finger_count += 1

        # =========================
        # Gesture Recognition
        # =========================

        if finger_count == 0:
            player_choice = "Rock"

        elif finger_count == 2:
            player_choice = "Scissors"

        elif finger_count == 5:
            player_choice = "Paper"

        else:
            player_choice = "Unknown"

        # =========================
        # Play Round Every 3 Seconds
        # =========================

        current_time = time.time()

        if current_time - last_round_time > 3:

            computer_choice = random.choice(
                ["Rock", "Paper", "Scissors"]
            )

            # Winner Logic
            if player_choice == computer_choice:

                winner = "Draw"

            elif (
                (player_choice == "Rock" and computer_choice == "Scissors")
                or
                (player_choice == "Paper" and computer_choice == "Rock")
                or
                (player_choice == "Scissors" and computer_choice == "Paper")
            ):

                winner = "You Win!"
                player_score += 1

            elif player_choice == "Unknown":

                winner = "Invalid Gesture"

            else:

                winner = "Computer Wins!"
                computer_score += 1

            last_round_time = current_time

        # =========================
        # OpenCV Text
        # =========================

        cv2.putText(
            frame,
            f'Player: {player_choice}',
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f'Computer: {computer_choice}',
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2
        )

        cv2.putText(
            frame,
            f'Result: {winner}',
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

        # =========================
        # Convert Frame
        # =========================

        ret, buffer = cv2.imencode('.jpg', frame)

        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            + frame +
            b'\r\n'
        )

# =========================
# Routes
# =========================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():

    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/game_data')
def game_data():

    return jsonify({
        "player": player_choice,
        "computer": computer_choice,
        "winner": winner,
        "player_score": player_score,
        "computer_score": computer_score
    })

# =========================
# Run App
# =========================

if __name__ == "__main__":
    app.run(debug=True)
    if __name__ == "__main__":
       app.run(host="0.0.0.0", port=5000)
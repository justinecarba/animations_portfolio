import os
import urllib.request

import cv2
import numpy as np
import mediapipe as mp


# ============================================================
# SETTINGS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MEME_FOLDER = os.path.join(BASE_DIR, "memes")

MODEL_FILE = os.path.join(
    BASE_DIR,
    "pose_landmarker_full.task"
)

# Official MediaPipe model location
MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/pose_landmarker/"
    "pose_landmarker_full/float16/latest/"
    "pose_landmarker_full.task"
)

CAMERA_INDEX = 0

MEME_MAX_SIDE = 800

MIN_VISIBILITY = 0.30


# ============================================================
# MEDIAPIPE TASKS
# ============================================================

BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions


# ============================================================
# DOWNLOAD MODEL IF NEEDED
# ============================================================

def download_model():

    if os.path.exists(MODEL_FILE):
        print("Pose model already exists.")
        return

    print()
    print("Pose model not found.")
    print("Downloading MediaPipe pose model...")
    print()

    try:

        urllib.request.urlretrieve(
            MODEL_URL,
            MODEL_FILE
        )

        print("Pose model downloaded successfully.")

    except Exception as error:

        print()
        print("Could not download the pose model.")
        print("Error:", error)
        print()
        raise


# ============================================================
# MIRROR INDEX
# ============================================================

MIRROR_INDEX = np.arange(33)

pairs = [
    (1, 4),
    (2, 5),
    (3, 6),
    (7, 8),
    (9, 10),
    (11, 12),
    (13, 14),
    (15, 16),
    (17, 18),
    (19, 20),
    (21, 22),
    (23, 24),
    (25, 26),
    (27, 28),
    (29, 30),
    (31, 32)
]

for a, b in pairs:

    MIRROR_INDEX[a] = b
    MIRROR_INDEX[b] = a


# ============================================================
# POSE CONNECTIONS
# ============================================================

POSE_CONNECTIONS = [
    (11, 12),

    (11, 13),
    (13, 15),

    (12, 14),
    (14, 16),

    (11, 23),
    (12, 24),

    (23, 24),

    (23, 25),
    (25, 27),

    (24, 26),
    (26, 28),

    (27, 29),
    (29, 31),

    (28, 30),
    (30, 32),

    (15, 17),
    (15, 19),
    (15, 21),

    (16, 18),
    (16, 20),
    (16, 22),

    (0, 11),
    (0, 12),

    (0, 1),
    (1, 2),
    (2, 3),
    (3, 7),

    (0, 4),
    (4, 5),
    (5, 6),
    (6, 8),

    (9, 10)
]


# ============================================================
# CONVERT MEDIAPIPE LANDMARKS
# ============================================================

def extract_landmarks(pose_landmarks, width, height):

    points = []

    visibility = []

    for landmark in pose_landmarks:

        x = landmark.x * width
        y = landmark.y * height

        points.append([x, y])

        if landmark.visibility is None:
            visibility.append(1.0)
        else:
            visibility.append(landmark.visibility)

    return (
        np.array(points, dtype=np.float32),
        np.array(visibility, dtype=np.float32)
    )


# ============================================================
# NORMALIZE POSE
# ============================================================

def normalize_pose(points):

    # Hip center
    hip_center = (
        points[23] +
        points[24]
    ) / 2

    # Shoulder center
    shoulder_center = (
        points[11] +
        points[12]
    ) / 2

    # Center the whole body
    centered = points - hip_center

    # Torso length
    scale = np.linalg.norm(
        shoulder_center - hip_center
    )

    # Fallback to shoulder width
    if scale < 0.000001:

        scale = np.linalg.norm(
            points[11] - points[12]
        )

    # Prevent division by zero
    if scale < 0.000001:
        scale = 1.0

    return centered / scale


# ============================================================
# MIRROR POSE
# ============================================================

def mirror_pose(points):

    mirrored = points.copy()

    # Flip horizontally
    mirrored[:, 0] *= -1

    # Swap left/right landmarks
    mirrored = mirrored[MIRROR_INDEX]

    return mirrored


# ============================================================
# POSE DISTANCE
# ============================================================

def pose_distance(
    user_points,
    user_visibility,
    meme_points,
    meme_visibility
):

    weights = np.minimum(
        user_visibility,
        meme_visibility
    )

    weights = np.where(
        weights >= MIN_VISIBILITY,
        weights,
        0.0
    )

    total_weight = weights.sum()

    if total_weight < 0.000001:
        return float("inf")

    distances = np.linalg.norm(
        user_points - meme_points,
        axis=1
    )

    weighted_distance = (
        distances * weights
    ).sum() / total_weight

    return float(weighted_distance)


# ============================================================
# CREATE POSE LANDMARKER
# ============================================================

def create_landmarker(running_mode):

    options = PoseLandmarkerOptions(

        base_options=BaseOptions(
            model_asset_path=MODEL_FILE
        ),

        running_mode=running_mode,

        num_poses=1,

        min_pose_detection_confidence=0.5,

        min_pose_presence_confidence=0.5,

        min_tracking_confidence=0.5
    )

    return PoseLandmarker.create_from_options(
        options
    )


# ============================================================
# LOAD MEMES
# ============================================================

def load_memes():

    memes = []

    if not os.path.isdir(MEME_FOLDER):

        os.makedirs(
            MEME_FOLDER,
            exist_ok=True
        )

        print()
        print("Created memes folder:")
        print(MEME_FOLDER)
        print()
        print(
            "Put your meme images inside the folder."
        )

        return memes

    print()
    print("Loading meme images...")
    print()

    image_landmarker = create_landmarker(
        VisionRunningMode.IMAGE
    )

    try:

        filenames = sorted(
            os.listdir(MEME_FOLDER)
        )

        for filename in filenames:

            if not filename.lower().endswith(
                (".jpg", ".jpeg", ".png")
            ):
                continue

            path = os.path.join(
                MEME_FOLDER,
                filename
            )

            image = cv2.imread(path)

            if image is None:

                print(
                    "Could not read:",
                    filename
                )

                continue

            # ------------------------------------------------
            # Resize large image
            # ------------------------------------------------

            height, width = image.shape[:2]

            biggest_side = max(
                height,
                width
            )

            if biggest_side > MEME_MAX_SIDE:

                scale = (
                    MEME_MAX_SIDE /
                    biggest_side
                )

                new_width = int(
                    width * scale
                )

                new_height = int(
                    height * scale
                )

                image = cv2.resize(
                    image,
                    (
                        new_width,
                        new_height
                    ),
                    interpolation=cv2.INTER_AREA
                )

                height, width = image.shape[:2]

            # ------------------------------------------------
            # Convert OpenCV -> MediaPipe
            # ------------------------------------------------

            rgb = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            # ------------------------------------------------
            # Detect pose
            # ------------------------------------------------

            result = image_landmarker.detect(
                mp_image
            )

            if not result.pose_landmarks:

                print(
                    "No pose found:",
                    filename
                )

                continue

            # First detected person
            landmarks = result.pose_landmarks[0]

            points, visibility = extract_landmarks(
                landmarks,
                width,
                height
            )

            normalized = normalize_pose(
                points
            )

            memes.append({

                "name": filename,

                "image": image,

                "points": normalized,

                "visibility": visibility

            })

            print(
                "Loaded:",
                filename
            )

    finally:

        image_landmarker.close()

    return memes


# ============================================================
# FIND BEST MEME
# ============================================================

def find_best_meme(
    user_points,
    user_visibility,
    memes
):

    user_normalized = normalize_pose(
        user_points
    )

    # Also test mirrored version
    user_mirrored = mirror_pose(
        user_normalized
    )

    mirrored_visibility = (
        user_visibility[MIRROR_INDEX]
    )

    best_meme = None

    best_score = float("inf")

    for meme in memes:

        # Normal comparison
        score_normal = pose_distance(

            user_normalized,

            user_visibility,

            meme["points"],

            meme["visibility"]
        )

        # Mirrored comparison
        score_mirrored = pose_distance(

            user_mirrored,

            mirrored_visibility,

            meme["points"],

            meme["visibility"]
        )

        score = min(
            score_normal,
            score_mirrored
        )

        print(
            f'{meme["name"]}: '
            f'{score:.3f}'
        )

        if score < best_score:

            best_score = score

            best_meme = meme

    return (
        best_meme,
        best_score
    )


# ============================================================
# DRAW POSE
# ============================================================

def draw_pose(
    frame,
    landmarks
):

    height, width = frame.shape[:2]

    points = []

    for landmark in landmarks:

        x = int(
            landmark.x * width
        )

        y = int(
            landmark.y * height
        )

        points.append(
            (x, y)
        )

    # Draw lines
    for start, end in POSE_CONNECTIONS:

        if start >= len(points):
            continue

        if end >= len(points):
            continue

        cv2.line(
            frame,
            points[start],
            points[end],
            (0, 255, 255),
            2
        )

    # Draw joints
    for point in points:

        cv2.circle(
            frame,
            point,
            4,
            (255, 0, 255),
            -1
        )


# ============================================================
# SHOW MATCH
# ============================================================

def show_result(
    meme,
    score
):

    image = meme["image"].copy()

    height, width = image.shape[:2]

    scale = min(
        700 / width,
        600 / height
    )

    new_width = int(
        width * scale
    )

    new_height = int(
        height * scale
    )

    image = cv2.resize(
        image,
        (
            new_width,
            new_height
        ),
        interpolation=cv2.INTER_AREA
    )

    # --------------------------------------------------------
    # Add dark area for text
    # --------------------------------------------------------

    text_height = 100

    result = np.zeros(
        (
            new_height + text_height,
            new_width,
            3
        ),
        dtype=np.uint8
    )

    result[
        text_height:
    ] = image

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    cv2.putText(
        result,
        "MATCH FOUND!",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        3
    )

    cv2.putText(
        result,
        f"Pose score: {score:.3f}",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "YOUR MEME MATCH",
        result
    )

    print()
    print("============================")
    print("MATCH FOUND!")
    print("============================")
    print(
        "Meme:",
        meme["name"]
    )
    print(
        "Score:",
        round(score, 3)
    )
    print()


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print()
    print("==============================")
    print("     POSE MEME MATCHER")
    print("==============================")
    print()

    # --------------------------------------------------------
    # Download model
    # --------------------------------------------------------

    download_model()

    # --------------------------------------------------------
    # Load memes
    # --------------------------------------------------------

    memes = load_memes()

    print()
    print(
        "Memes loaded:",
        len(memes)
    )

    if not memes:

        print()
        print(
            "No usable meme images found."
        )

        print(
            "Put images inside:"
        )

        print(
            MEME_FOLDER
        )

        return

    # --------------------------------------------------------
    # Live pose detector
    # --------------------------------------------------------

    live_pose = create_landmarker(
        VisionRunningMode.VIDEO
    )

    # --------------------------------------------------------
    # Camera
    # --------------------------------------------------------

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():

        print(
            "Could not open camera."
        )

        live_pose.close()

        return

    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        640
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        480
    )

    print()
    print("==============================")
    print("Camera started!")
    print("==============================")
    print()
    print("Make a pose.")
    print()
    print("SPACE = Find matching meme")
    print("Q / ESC = Quit")
    print()

    frame_timestamp = 0

    try:

        while True:

            success, frame = camera.read()

            if not success:

                print(
                    "Could not read camera frame."
                )

                break

            # Mirror webcam
            frame = cv2.flip(
                frame,
                1
            )

            height, width = frame.shape[:2]

            # ------------------------------------------------
            # Convert to MediaPipe image
            # ------------------------------------------------

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            # ------------------------------------------------
            # Detect pose
            # ------------------------------------------------

            frame_timestamp += 33

            result = live_pose.detect_for_video(
                mp_image,
                frame_timestamp
            )

            # ------------------------------------------------
            # Draw detected person
            # ------------------------------------------------

            person_detected = False

            if result.pose_landmarks:

                person_detected = True

                landmarks = (
                    result.pose_landmarks[0]
                )

                draw_pose(
                    frame,
                    landmarks
                )

            # ------------------------------------------------
            # UI
            # ------------------------------------------------

            cv2.putText(
                frame,
                "POSE MEME MATCHER",
                (25, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "SPACE = Find meme",
                (25, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2
            )

            cv2.putText(
                frame,
                "Q / ESC = Quit",
                (25, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (200, 200, 200),
                2
            )

            if person_detected:

                cv2.putText(
                    frame,
                    "PERSON DETECTED",
                    (25, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

            else:

                cv2.putText(
                    frame,
                    "NO PERSON DETECTED",
                    (25, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )

            # ------------------------------------------------
            # Show camera
            # ------------------------------------------------

            cv2.imshow(
                "Pose Meme Matcher",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            # ------------------------------------------------
            # SPACE
            # ------------------------------------------------

            if key == 32:

                if result.pose_landmarks:

                    landmarks = (
                        result.pose_landmarks[0]
                    )

                    user_points, user_visibility = (
                        extract_landmarks(
                            landmarks,
                            width,
                            height
                        )
                    )

                    print()
                    print("==============================")
                    print("SEARCHING FOR BEST MEME...")
                    print("==============================")

                    best_meme, score = find_best_meme(
                        user_points,
                        user_visibility,
                        memes
                    )

                    if best_meme is not None:

                        show_result(
                            best_meme,
                            score
                        )

                    else:

                        print(
                            "No matching meme found."
                        )

                else:

                    print(
                        "No person detected!"
                    )

            # ------------------------------------------------
            # Quit
            # ------------------------------------------------

            if key in (
                27,
                ord("q")
            ):

                break

    finally:

        camera.release()

        cv2.destroyAllWindows()

        live_pose.close()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()
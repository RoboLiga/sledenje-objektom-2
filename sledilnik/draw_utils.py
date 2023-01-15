import cv2

from sledilnik.Resources import ResGUIText


def draw_text_centered(frame, text, pos, font, font_scale, color, thickness=None, line_type=None):
    text_size = cv2.getTextSize(text, font, 1, 2)[0]
    text_x = (pos[0] - text_size[0] // 2)
    cv2.putText(frame, text, (text_x, pos[1]), font, font_scale, color, thickness, line_type)


def draw_guide(frame, text):
    draw_text_centered(
        frame,
        text,
        (frame.shape[1] // 2, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        2,
        cv2.LINE_AA
    )


def draw_fps(frame, fps):
    font = cv2.FONT_HERSHEY_SIMPLEX
    # Display FPS
    cv2.putText(frame, ResGUIText.sFps + str(int(fps)), (10, 30), font, 1, (0, 255, 255), 2, cv2.LINE_AA)


def draw_help(frame):
    cv2.putText(
        frame,
        ResGUIText.sHelp,
        (10, frame.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (0, 0, 255),
        1,
        cv2.LINE_AA
    )


def draw_lines(frame, corners):
    for i in range(len(corners)):
        cv2.circle(frame, tuple(corners[i]), 3, (0, 255, 255), 3)

        if i % 4 == 3:
            cv2.line(frame, tuple(corners[i - 1]), tuple(corners[i]), (0, 255, 255), 2)
            cv2.line(frame, tuple(corners[i - 3]), tuple(corners[i]), (0, 255, 255), 2)
        elif i % 4 != 0:
            cv2.line(frame, tuple(corners[i - 1]), tuple(corners[i]), (0, 255, 255), 2)


def create_guide_text(name):
    return [
        'Mark ' + name + ' Top Left Corner',
        'Mark ' + name + ' Field Top Right Corner',
        'Mark ' + name + ' Field Bottom Right Corner',
        'Mark ' + name + ' Field Bottom Left Corner'
    ]

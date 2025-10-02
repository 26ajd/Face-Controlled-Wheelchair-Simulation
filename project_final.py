import cv2
import mediapipe as mp
import pygame
import sys
import time
import numpy as np
import math
import random

# ==============================
# إعدادات أساسية
# ==============================
pygame.init()

# استخدام وضع الشاشة الكاملة
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()
pygame.display.set_caption("Face-Controlled Wheelchair - REALISTIC SIMULATION")

# إعداد الخطوط
font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 18)
title_font = pygame.font.SysFont("Arial", 32, bold=True)

# إعداد الكاميرا
try:
    cap = cv2.VideoCapture("http://192.168.1.2:8080/video")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    CAMERA_AVAILABLE = True
except:
    CAMERA_AVAILABLE = False
    print("Camera not available, using placeholder")

# إعداد Mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ==============================
# إعداد الكرسي المتحرك (حركة واقعية)
# ==============================
class Wheelchair:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 120
        self.height = 160
        self.speed = 5
        self.rotation_speed = 3  # سرعة الدوران حول المركز
        self.color = (70, 130, 180)
        self.direction = 0  # الزاوية بالدرجات (0 = للأعلى)
        self.wheel_rotation = 0
        self.moving = False
        self.trail = []
        self.max_trail_length = 15
        self.is_rotating = False
        self.rotation_direction = 0  # 0 = لا دوران, -1 = يسار, 1 = يمين
        
    def start_rotation(self, direction):
        """بدء الدوران حول المركز (يسار أو يمين)"""
        self.is_rotating = True
        self.rotation_direction = direction
        
    def stop_rotation(self):
        """إيقاف الدوران"""
        self.is_rotating = False
        self.rotation_direction = 0
        
    def move_forward(self):
        """التحرك للأمام في الاتجاه الحالي"""
        self.moving = True
        rad = math.radians(self.direction)
        self.x += math.sin(rad) * self.speed
        self.y -= math.cos(rad) * self.speed
        self.wheel_rotation += self.speed * 2
        
    def move_backward(self):
        """التحرك للخلف في الاتجاه الحالي"""
        self.moving = True
        rad = math.radians(self.direction)
        self.x -= math.sin(rad) * self.speed
        self.y += math.cos(rad) * self.speed
        self.wheel_rotation -= self.speed * 2
        
    def update(self):
        """تحديث حالة الكرسي"""
        # تطبيق الدوران إذا كان نشطاً
        if self.is_rotating:
            self.direction += self.rotation_speed * self.rotation_direction
            # الحفاظ على الزاوية بين 0 و 360
            if self.direction >= 360:
                self.direction -= 360
            elif self.direction < 0:
                self.direction += 360
        
        # تحديث أثر الحركة
        if self.moving and len(self.trail) < self.max_trail_length:
            self.trail.append((self.x, self.y, self.direction))
        
        self.moving = False
        
        # التأكد من بقاء الكرسي داخل الشاشة
        self.x = max(self.width//2, min(WIDTH - self.width//2, self.x))
        self.y = max(self.height//2, min(HEIGHT - self.height//2, self.y))
        
    def draw(self, screen):
        """رسم الكرسي"""
        # رسم أثر الحركة
        for i, (x, y, dir) in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail)))
            size = int(8 * (i / len(self.trail)))
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (70, 130, 180, alpha), (size, size), size)
            screen.blit(s, (int(x)-size, int(y)-size))
        
        # إنشاء سطح للكرسي
        chair_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # رسم هيكل الكرسي الرئيسي
        pygame.draw.rect(chair_surface, self.color, 
                        (0, 0, self.width, self.height), 
                        border_radius=12)
        
        # رسم المقعد
        seat_color = (100, 80, 60)
        pygame.draw.rect(chair_surface, seat_color, 
                        (15, 15, self.width-30, self.height-50), 
                        border_radius=8)
        
        # رسم ظهر الكرسي مع مؤشر اتجاه
        back_color = (90, 70, 50)
        pygame.draw.rect(chair_surface, back_color, 
                        (15, 15, self.width-30, 40), 
                        border_radius=5)
        
        # مؤشر اتجاه واضح (سهم أحمر)
        indicator_color = (255, 50, 50)
        pygame.draw.polygon(chair_surface, indicator_color, [
            (self.width//2, 10),
            (self.width//2 - 15, 35),
            (self.width//2 + 15, 35)
        ])
        
        # رسم العجلات الخلفية
        wheel_color = (30, 30, 30)
        wheel_width = 20
        wheel_height = 40
        
        pygame.draw.ellipse(chair_surface, wheel_color, 
                          (-wheel_width//2, self.height//2 - wheel_height//2, 
                           wheel_width, wheel_height))
        
        pygame.draw.ellipse(chair_surface, wheel_color, 
                          (self.width - wheel_width//2, self.height//2 - wheel_height//2, 
                           wheel_width, wheel_height))
        
        # رسم العجلات الأمامية مع دوران
        front_wheel_size = 25
        front_wheel_color = (40, 40, 40)
        
        wheel_x_left = 30
        wheel_y = self.height - 15
        pygame.draw.circle(chair_surface, front_wheel_color, 
                         (wheel_x_left, wheel_y), front_wheel_size)
        
        wheel_x_right = self.width - 30
        pygame.draw.circle(chair_surface, front_wheel_color, 
                         (wheel_x_right, wheel_y), front_wheel_size)
        
        # خطوط الدوران على العجلات
        line_color = (200, 200, 200)
        angle = self.wheel_rotation
        rad = math.radians(angle)
        
        for wheel_x in [wheel_x_left, wheel_x_right]:
            start_x = wheel_x + math.sin(rad) * front_wheel_size * 0.8
            start_y = wheel_y - math.cos(rad) * front_wheel_size * 0.8
            end_x = wheel_x - math.sin(rad) * front_wheel_size * 0.8
            end_y = wheel_y + math.cos(rad) * front_wheel_size * 0.8
            pygame.draw.line(chair_surface, line_color, 
                           (start_x, start_y), (end_x, end_y), 4)
        
        # تدوير الكرسي حسب الاتجاه
        rotated_chair = pygame.transform.rotate(chair_surface, self.direction)
        rotated_rect = rotated_chair.get_rect(center=(self.x, self.y))
        
        screen.blit(rotated_chair, rotated_rect)
        
        # عرض حالة الدوران
        if self.is_rotating:
            rotation_text = small_font.render(f"Rotating {'Right' if self.rotation_direction == 1 else 'Left'}", 
                                            True, (255, 255, 0))
            screen.blit(rotation_text, (self.x - 50, self.y - 80))

# ==============================
# العقبات والأهداف
# ==============================
class Obstacle:
    def __init__(self, x, y, width, height, obstacle_type="wall"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = obstacle_type
        self.colors = {
            "wall": (120, 80, 40),
            "cone": (255, 165, 0),
            "plant": (50, 150, 50)
        }
        self.color = self.colors.get(obstacle_type, (120, 80, 40))
        
    def draw(self, screen):
        if self.type == "wall":
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        elif self.type == "cone":
            pygame.draw.polygon(screen, self.color, [
                (self.x, self.y + self.height),
                (self.x + self.width//2, self.y),
                (self.x + self.width, self.y + self.height)
            ])
        elif self.type == "plant":
            pygame.draw.rect(screen, (100, 70, 40), 
                           (self.x + self.width//3, self.y + self.height//2, 
                            self.width//3, self.height//2))
            pygame.draw.circle(screen, self.color, 
                             (self.x + self.width//2, self.y + self.height//3), 
                             self.width//3)

class Target:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 25
        self.color = (255, 50, 50)
        self.pulse = 0
        self.pulse_speed = 0.05
        
    def update(self):
        self.pulse += self.pulse_speed
        if self.pulse > 1:
            self.pulse = 0
            
    def draw(self, screen):
        pulse_size = int(8 * math.sin(self.pulse * math.pi))
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius + pulse_size)
        pygame.draw.circle(screen, (255, 200, 200), (self.x, self.y), self.radius - 4)

# ==============================
# دوال التعرف على الإيماءات (مصححة الاتجاهات)
# ==============================
def is_smiling(landmarks):
    left_corner = landmarks[61]
    right_corner = landmarks[291]
    upper_lip = landmarks[13]
    lower_lip = landmarks[14]
    
    mouth_width = abs(right_corner.x - left_corner.x)
    mouth_height = abs(lower_lip.y - upper_lip.y)
    
    if mouth_height < 0.01:
        return False
    
    ratio = mouth_width / mouth_height
    return ratio > 1.6

def are_eyebrows_raised(landmarks):
    left_eyebrow_y = np.mean([landmarks[i].y for i in [70, 63, 105]])
    right_eyebrow_y = np.mean([landmarks[i].y for i in [300, 293, 334]])
    left_eye_top = landmarks[159].y
    right_eye_top = landmarks[386].y
    
    left_diff = left_eye_top - left_eyebrow_y
    right_diff = right_eye_top - right_eyebrow_y
    
    return left_diff > 0.03 or right_diff > 0.03

def get_eye_direction(landmarks):
    left_eye_left = landmarks[33].x
    left_eye_right = landmarks[133].x  
    left_iris = landmarks[468].x
    
    right_eye_left = landmarks[362].x
    right_eye_right = landmarks[263].x
    right_iris = landmarks[473].x
    
    left_ratio = (left_iris - left_eye_left) / (left_eye_right - left_eye_left)
    right_ratio = (right_iris - right_eye_left) / (right_eye_right - right_eye_left)
    
    avg_ratio = (left_ratio + right_ratio) / 2
    
    # تصحيح الاتجاهات: عندما أنظر لليسار، الكرسي يدور لليسار
    if avg_ratio < 0.4:
        return "right"  # تصحيح: النظر لليسار = دوران لليسار
    elif avg_ratio > 0.6:
        return "left"   # تصحيح: النظر لليمين = دوران لليمين
    else:
        return "center"

def is_mouth_open(landmarks):
    upper_lip = landmarks[13].y
    lower_lip = landmarks[14].y
    mouth_openness = lower_lip - upper_lip
    return mouth_openness > 0.05

# ==============================
# الدالة الرئيسية
# ==============================
def main():
    clock = pygame.time.Clock()
    wheelchair = Wheelchair(WIDTH // 4, HEIGHT // 2)
    
    # إنشاء عقبات
    obstacles = [
        Obstacle(600, 200, 150, 25, "wall"),
        Obstacle(800, 400, 25, 150, "wall"),
        Obstacle(400, 500, 40, 40, "cone"),
        Obstacle(900, 300, 50, 50, "plant"),
        Obstacle(300, 100, 50, 50, "plant")
    ]
    
    target = Target(WIDTH - 150, HEIGHT // 2)
    
    # إحصاءات
    frame_count = 0
    detection_count = 0
    start_time = time.time()
    distance_traveled = 0
    last_x, last_y = wheelchair.x, wheelchair.y
    
    simulation_state = "running"
    current_gesture = "neutral"  # تتبع الإيماءة الحالية
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    simulation_state = "paused" if simulation_state == "running" else "running"
                elif event.key == pygame.K_r:
                    wheelchair = Wheelchair(WIDTH // 4, HEIGHT // 2)
                    simulation_state = "running"
                    start_time = time.time()
                    distance_traveled = 0
                    current_gesture = "neutral"
        
        if simulation_state != "running":
            # شاشة الإيقاف
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            pause_text = title_font.render("SIMULATION PAUSED", True, (255, 255, 255))
            continue_text = font.render("Press P to continue or R to reset", True, (200, 200, 200))
            screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 30))
            screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 20))
            pygame.display.flip()
            clock.tick(60)
            continue
            
        # قراءة الإطار من الكاميرا
        if CAMERA_AVAILABLE:
            ret, frame = cap.read()
            if not ret:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "CAMERA NOT AVAILABLE", (150, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
        frame_count += 1
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = face_mesh.process(rgb_frame)
        
        status = "No face detected"
        action = "No movement"
        new_gesture = "neutral"
        
        # التحكم باللوحة المفاتيح (للتجربة)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            wheelchair.move_forward()
            action = "KEY: Forward"
            new_gesture = "forward"
        elif keys[pygame.K_DOWN]:
            wheelchair.move_backward() 
            action = "KEY: Backward"
            new_gesture = "backward"
        elif keys[pygame.K_LEFT]:
            wheelchair.start_rotation(-1)  # دوران لليسار
            action = "KEY: Rotate Left"
            new_gesture = "rotate_left"
        elif keys[pygame.K_RIGHT]:
            wheelchair.start_rotation(1)   # دوران لليمين
            action = "KEY: Rotate Right"
            new_gesture = "rotate_right"
        else:
            wheelchair.stop_rotation()
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                detection_count += 1
                landmarks = face_landmarks.landmark
                
                smiling = is_smiling(landmarks)
                eyebrows_raised = are_eyebrows_raised(landmarks) 
                eye_dir = get_eye_direction(landmarks)  # الاتجاهات مصححة الآن
                mouth_open = is_mouth_open(landmarks)
                
                # تطبيق التحكم بناء على الإيماءات
                if eyebrows_raised:
                    wheelchair.move_forward()
                    action = "EYEBROWS: Forward"
                    status = "Eyebrows raised"
                    new_gesture = "forward"
                    wheelchair.stop_rotation()
                    
                elif smiling:
                    wheelchair.move_backward()
                    action = "SMILE: Backward" 
                    status = "Smile detected"
                    new_gesture = "backward"
                    wheelchair.stop_rotation()
                    
                elif eye_dir == "left":  # تم تصحيح الاتجاه
                    wheelchair.start_rotation(-1)  # دوران لليسار
                    action = "LOOK LEFT: Rotate Left"
                    status = "Looking left"
                    new_gesture = "rotate_left"
                    
                elif eye_dir == "right":  # تم تصحيح الاتجاه
                    wheelchair.start_rotation(1)   # دوران لليمين
                    action = "LOOK RIGHT: Rotate Right" 
                    status = "Looking right"
                    new_gesture = "rotate_right"
                    
                elif mouth_open:
                    wheelchair.stop_rotation()
                    action = "MOUTH OPEN: Stop"
                    status = "Mouth open"
                    new_gesture = "stop"
                else:
                    wheelchair.stop_rotation()
                    action = "NEUTRAL: No movement"
                    status = "Face detected"
                    new_gesture = "neutral"
                
                # تحديث الإيماءة الحالية
                current_gesture = new_gesture
                
                if CAMERA_AVAILABLE:
                    h, w, _ = frame.shape
                    for landmark in landmarks:
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
        
        # إذا لم يكن هناك اكتشاف للوجه، توقف عن الدوران
        if not results.multi_face_landmarks:
            wheelchair.stop_rotation()
            current_gesture = "neutral"
        
        wheelchair.update()
        target.update()
        
        # حساب المسافة المقطوعة
        distance_traveled += math.sqrt((wheelchair.x - last_x)**2 + (wheelchair.y - last_y)**2)
        last_x, last_y = wheelchair.x, wheelchair.y
        
        # التحقق من الوصول إلى الهدف
        target_distance = math.sqrt((wheelchair.x - target.x)**2 + (wheelchair.y - target.y)**2)
        if target_distance < wheelchair.width//2 + target.radius:
            simulation_state = "completed"
        
        # الرسم
        screen.fill((60, 60, 80))
        
        # شبكة أرضية
        for x in range(0, WIDTH, 80):
            pygame.draw.line(screen, (100, 100, 100, 50), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 80):
            pygame.draw.line(screen, (100, 100, 100, 50), (0, y), (WIDTH, y), 1)
        
        # رسم العقبات
        for obstacle in obstacles:
            obstacle.draw(screen)
        
        # رسم الهدف
        target.draw(screen)
        
        # رسم الكرسي
        wheelchair.draw(screen)
        
        # تحويل وعرض فيديو الكاميرا
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        frame_surface = pygame.transform.scale(frame_surface, (280, 210))
        
        cam_bg = pygame.Rect(10, 10, 290, 220)
        pygame.draw.rect(screen, (30, 30, 30), cam_bg)
        pygame.draw.rect(screen, (100, 100, 100), cam_bg, 2)
        screen.blit(frame_surface, (15, 15))
        
        # لوحة المعلومات
        info_bg = pygame.Rect(10, 240, 350, 200)
        pygame.draw.rect(screen, (0, 0, 0, 180), info_bg)
        pygame.draw.rect(screen, (100, 100, 100), info_bg, 2)
        
        title_text = small_font.render("Face Controlled Wheelchair", True, (255, 255, 255))
        status_text = small_font.render(f"Status: {status}", True, (100, 255, 100))
        action_text = small_font.render(f"Action: {action}", True, (100, 100, 255))
        gesture_text = small_font.render(f"Gesture: {current_gesture}", True, (255, 255, 100))
        direction_text = small_font.render(f"Direction: {int(wheelchair.direction)}°", True, (200, 200, 255))
        
        screen.blit(title_text, (20, 250))
        screen.blit(status_text, (20, 280))
        screen.blit(action_text, (20, 305))
        screen.blit(gesture_text, (20, 330))
        screen.blit(direction_text, (20, 355))
        
        # إحصاءات
        elapsed_time = time.time() - start_time
        detection_rate = (detection_count / frame_count * 100) if frame_count > 0 else 0
        
        stats_text = small_font.render(f"Detection: {detection_rate:.1f}%", True, (200, 200, 200))
        time_text = small_font.render(f"Time: {elapsed_time:.1f}s", True, (200, 200, 200))
        distance_text = small_font.render(f"Distance: {distance_traveled:.0f}px", True, (200, 200, 200))
        
        screen.blit(stats_text, (20, 385))
        screen.blit(time_text, (20, 410))
        screen.blit(distance_text, (20, 435))
        
        # رسالة النجاح
        if simulation_state == "completed":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 50, 0, 150))
            screen.blit(overlay, (0, 0))
            
            success_text = title_font.render("MISSION COMPLETED!", True, (100, 255, 100))
            time_taken = small_font.render(f"Time: {elapsed_time:.1f}s - Distance: {distance_traveled:.0f}px", 
                                         True, (200, 255, 200))
            restart_text = small_font.render("Press R to restart", True, (200, 200, 100))
            
            screen.blit(success_text, (WIDTH//2 - success_text.get_width()//2, HEIGHT//2 - 40))
            screen.blit(time_taken, (WIDTH//2 - time_taken.get_width()//2, HEIGHT//2))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    if CAMERA_AVAILABLE:
        cap.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


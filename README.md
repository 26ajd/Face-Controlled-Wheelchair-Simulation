# 🧑‍🦽 Face-Controlled Wheelchair Simulation

محاكاة تفاعلية لكرسي متحرك يتم التحكم فيه بتعابير الوجه باستخدام **Mediapipe** و **OpenCV** و **Pygame**، مع دعم الاصطدام بالعقبات لزيادة الواقعية.

---

## 📦 المتطلبات

قبل تشغيل المشروع تأكد من تثبيت المكتبات التالية:

```bash
pip install opencv-python mediapipe pygame numpy
```

---

## 🚀 التشغيل

```bash
python face_wheelchair.py
```

---

## 🎮 التحكم عبر تعابير الوجه

* **رفع الحواجب** → التحرك للأمام
* **الابتسامة** → الرجوع للخلف
* **النظر يسار/يمين** → دوران يسار/يمين
* **فتح الفم** → توقف

---

## 🏗 المكونات

* **Wheelchair** → الكرسي المتحرك مع حركة العجلات واتجاه الدوران.
* **Obstacle** → عقبات (جدار، مخروط، نبات).
* **Target** → الهدف النهائي مع تأثير نبض.
* **Collision System** → يمنع المرور عبر العقبات.

---

## ⚡️ الكود الأساسي مع الاصطدام

```python
class Wheelchair:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 120
        self.height = 160
        self.speed = 5
        self.direction = 0
        self.moving = False

    def _check_collision(self, new_x, new_y, obstacles):
        rect = pygame.Rect(
            new_x - self.width // 2, 
            new_y - self.height // 2,
            self.width, self.height
        )
        for obs in obstacles:
            obs_rect = pygame.Rect(obs.x, obs.y, obs.width, obs.height)
            if rect.colliderect(obs_rect):
                return True
        return False

    def move_forward(self, obstacles):
        rad = math.radians(self.direction)
        new_x = self.x + math.sin(rad) * self.speed
        new_y = self.y - math.cos(rad) * self.speed
        if not self._check_collision(new_x, new_y, obstacles):
            self.x, self.y = new_x, new_y
            self.moving = True

    def move_backward(self, obstacles):
        rad = math.radians(self.direction)
        new_x = self.x - math.sin(rad) * self.speed
        new_y = self.y + math.cos(rad) * self.speed
        if not self._check_collision(new_x, new_y, obstacles):
            self.x, self.y = new_x, new_y
            self.moving = True
```

---

## 🧪 حالات الاستخدام

* **التدريب على التحكم بدون لمس** (Hands-Free).
* **مساعدة ذوي الاحتياجات الخاصة** عبر محاكاة بيئة واقعية.
* **أبحاث الذكاء الاصطناعي** في التفاعل مع تعابير الوجه.

---

## 📸 مثال تشغيل

* نافذة كاملة الشاشة.
* بث مباشر من الكاميرا (أو IP camera).
* عرض الكرسي، العقبات، الهدف، والكاميرا المصغّرة.
---

## 📝 ملاحظات

* يمكن التبديل بين **تشغيل/إيقاف مؤقت** بالضغط على **P**.
* إعادة المحاكاة بالضغط على **R**.
* الخروج بالضغط على **Esc**.

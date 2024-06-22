# import os
# from django.db import models
# from django.conf import settings

# VIDEO_PATHS = {
#     'السلام عليكم': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video1.mp4'),
#     'مع السلامه': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video2.mp4'),
#     'كيف الحال': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video3.mp4'),
#     'مهندس': os.path.join(settings.BASE_DIR, 'video_app', 'models', 'video4.mp4')
# }

# class Room(models.Model):
#     number = models.PositiveSmallIntegerField()
#     def __str__(self):
#         return f"Room {self.number}"

# class Person(models.Model):
#     name = models.CharField(max_length=64)
#     is_deaf = models.BooleanField(default=False)
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="persons")
#     def __str__(self):
#         return f"{self.name}: {self.Room.number} - {self.is_deaf}"


# class Predicted_Text(models.Model):
#     text = models.CharField(max_length=64)
#     video = models.PositiveSmallIntegerField()
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="persons")
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     def __str__(self):
#         return f"text: {self.text}"

#     def get_vid(self):
#         video_path = VIDEO_PATHS[self.text]
#         if os.path.exists(video_path):
#             return video_path
#         else:
#             return None

        


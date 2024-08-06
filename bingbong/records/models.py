from django.db import models
from django.contrib.auth.models import User  #accounts 개발 전 user 모델 사용을 위한 import

# DOW_CHOICES = (
#   ('MON', 'Monday'),
#   ('TUE', 'Tuesday'),
#   ('WED', 'Wednesday'),
#   ('THUR', 'Thursday'),
#   ('FRI', 'Friday'),
#   ('SAT', 'Saturday'),
#   ('SUN', 'Sunday')
# )

class Record(models.Model):
  user = models.ForeignKey(
    User,
    on_delete=models.CASCADE
  ) # accounts 완성 시, user 모델로 변경 예정
  year  = models.IntegerField()
  month = models.IntegerField()
  day   = models.IntegerField()
  dow   = models.CharField(max_length=50)
  soju_record = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
  beer_record = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
  mak_record  = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
  wine_record = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)

  def __str__(self):
    return str(self.user) +" "+str(self.year)+"년 "+str(self.month)+"월 "+str(self.day)+"일 기록"
import auditlog.registry
from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime
from auditlog.registry import auditlog


User = get_user_model()

class Block(models.Model):
    blocker = models.ForeignKey(User, related_name='blocker', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
auditlog.register(Block)

class FriendRequest(models.Model):
    """To manage Friend Request"""
    status_choices = [('P', 'Pending'), ('A', 'Accepted'), ('R', 'Rejected')] 
    sender = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=status_choices, default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(blank=True,null=True)

    def save(self,*args,**kwargs):
        if self.pk:
            self.modified_at = datetime.now()
        return super().save(*args,**kwargs)
    
    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender} to {self.receiver} - {self.status}"
auditlog.register(FriendRequest)
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.text import slugify

# chat group model
class Chat(models.Model):
	users = models.ManyToManyField(User, related_name='chats', through='UserChatStatus')
	title = models.CharField(max_length=200)
	created_at = models.DateTimeField(auto_now_add=True)
	slug = models.SlugField(unique=True)

	def __str__(self):
		return self.title

	# adds user to the user's list respective of a group
	def add_user(self, user):
		if user:
			print (user)
			user_chat_status = UserChatStatus(user=user, chat=self)
			user_chat_status.save()
			print ('successfully added user',user.username)
			return True
		return None

	# adds message to the group
	def add_message(self, user, message):
		message = Message(chat=self, user=user, message=message)
		message.save()
		return message

# creates slug for the group title which is unique for a chat group.
def create_slug(instance, new_slug=None):
	slug = slugify(instance.title)
	if new_slug is not None:
		slug = new_slug
	qs = Chat.objects.filter(slug=slug).order_by("-id")
	if qs.exists():
		new_slug = "%s-%s" %(slug, qs.first().id)
		return create_slug(instance, new_slug=new_slug)
	return slug

# pre_save signal is defined to create slug, if not exists
def pre_save_post_receiver(sender, instance, *args, **kwargs):
	if not instance.slug:
		instance.slug = create_slug(instance)


pre_save.connect(pre_save_post_receiver, sender=Chat)


# through model between chat and message.Contains it's own attributes to check the status and,
# date of joining for a user in that group
class UserChatStatus(models.Model):

    INACTIVE = 'inactive'
    ACTIVE = 'active'

    CHAT_STATUS_CHOICES = (
        (INACTIVE, 'Inactive'),
        (ACTIVE, 'Active'),
    )

    user = models.ForeignKey(User, related_name='user_chat_statuses')
    chat = models.ForeignKey(Chat, related_name='user_chat_statuses')
    status = models.CharField(max_length=8, choices=CHAT_STATUS_CHOICES, default=ACTIVE)
    joined = models.DateTimeField(editable=False, auto_now_add=True)
    is_owner = models.BooleanField(default=False)

    class Meta:
        unique_together = (('user', 'chat'),)
        verbose_name_plural = 'user chat statuses'

    def __str__(self):
        return "{user} in chat \"{chat}\" ({status})".format(user=self.user, chat=self.chat, status=self.status)

    @property
    def is_active(self):
        return self.status == self.ACTIVE

    @property
    def is_inactive(self):
        return self.status == self.INACTIVE

    def activate(self):
        self.status = self.ACTIVE
        self.save()

    def deactivate(self):
        self.status = self.INACTIVE
        self.save()

	
# message table to store chat group messages 
class Message(models.Model):
	
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	chat = models.ForeignKey(Chat, on_delete = models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	message = models.TextField()
	

	def __str__(self):
		return self.message



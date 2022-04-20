from datetime import datetime
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


def get_avatar_path(instance, filename):
    return 'registration-avatar/{0}/{1}'.format(instance.username, filename)


def get_user_docs_path(instance, filename):
    return 'registration-docs/{0}/{1}'.format(instance.associated_account, filename)


class UserData(models.Model):
    avatar = models.ImageField(upload_to=get_avatar_path, default='no-avatar.png')
    is_verified = models.BooleanField(default=False)
    is_tenant = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} | {self.first_name} {self.last_name}"


class Profile(models.Model):
    username = models.OneToOneField(UserData, on_delete=models.CASCADE)
    phone = PhoneNumberField()
    street_address = models.CharField(max_length=30)
    lga_area = models.CharField(max_length=30)
    state = models.CharField(max_length=30, default='Kenya')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username}'s profile"


class Managers(models.Model):
    VER_STATUS = [
        ('rv', 'Revoked'),
        ('pv', 'Pending Approval'),
        ('ap', 'Approved'),
    ]
    ID_WARNING = 'Must be a valid ID!'
    associated_account = models.OneToOneField(UserData, on_delete=models.CASCADE)
    fullname = models.CharField(max_length=100, null=True, blank=True)
    id_back = models.ImageField(upload_to=get_user_docs_path, help_text=ID_WARNING)
    id_front = models.ImageField(upload_to=get_user_docs_path, help_text=ID_WARNING)
    added_by = models.ForeignKey(UserData, on_delete=models.DO_NOTHING, related_name='added_by')
    active_phone_number = PhoneNumberField()
    whatsapp_number = models.CharField(max_length=14)
    status = models.CharField(max_length=3, choices=VER_STATUS, default='pv')
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.status == 'ap':
            UserData.objects.filter(pk=self.associated_account.pk).update(is_manager=True, is_verified=True)
            Profile.objects.filter(user=self.associated_account.pk).update(phone=self.active_phone_number)
        else:
            UserData.objects.filter(pk=self.associated_account.pk).update(is_manager=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.associated_account.username}"

    class Meta:
        verbose_name_plural = 'Managers'


class Tenants(models.Model):
    associated_account = models.OneToOneField(UserData, on_delete=models.CASCADE, verbose_name='tenant')
    full_name = models.CharField(max_length=100)
    id_number = models.CharField(max_length=10)
    id_front = models.ImageField(upload_to=get_user_docs_path, blank=True)
    id_back = models.ImageField(upload_to=get_user_docs_path, blank=True)
    active_phone_number = PhoneNumberField()
    policy_agreement = models.BooleanField(default=False)
    moved_in = models.BooleanField(default=False)
    move_in_date = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(default=datetime.now)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.moved_in:
            UserData.objects.filter(pk=self.associated_account_id).update(is_tenant=True)
        else:
            UserData.objects.filter(pk=self.associated_account_id).update(is_tenant=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.associated_account.username}"

    class Meta:
        verbose_name_plural = 'Tenants'


def get_related_record_path(instance, filename):
    return 'tenant_records/{0}/{1}'.format(instance.tenant, filename)


class RelatedRecords(models.Model):
    tenant = models.ForeignKey(Tenants, on_delete=models.CASCADE)
    title = models.CharField(max_length=155, null=True, blank=True)
    file = models.FileField(upload_to=get_related_record_path)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Related Records'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.title} - {self.tenant.full_name}"


class UserNotifications(models.Model):
    user_id = models.ForeignKey(UserData, on_delete=models.CASCADE)
    message = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}"

    class Meta:
        verbose_name = "Notifications"
        verbose_name_plural = verbose_name

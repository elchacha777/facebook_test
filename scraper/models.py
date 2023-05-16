from django.db import models


class Account(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class MaxConcurrency(models.Model):
    max_concurrency = models.IntegerField()
    current_concurrency = models.IntegerField()


class Tasks(models.Model):
    file = models.FileField(upload_to='csv_files', help_text="filename.csv file format.\nThe file must include 2 required fields 'city' and 'state_name'")
    keyword = models.CharField(max_length=255, blank=True, null=True)
    run_every_minutes = models.IntegerField()
    next_execution = models.DateTimeField()
    cache_time = models.IntegerField(default=0)
    task_progress = models.CharField(
        max_length=20,
        choices=[
            ('in_progress', 'In Progress'),
            ('finished', 'Finished')
        ],
        default=''
    )


    class Meta:
        verbose_name = 'Tasks'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return f'{self.keyword}  task progress: {self.task_progress}'




class Result(models.Model):
    title = models.CharField(max_length=500, null=True, blank=True)
    phone = models.CharField(max_length=500, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    category = models.CharField(max_length=500, null=True, blank=True)
    followers = models.CharField(max_length=500, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.CharField(max_length=500, null=True, blank=True)
    rating = models.CharField(max_length=500, null=True, blank=True)
    city = models.CharField(max_length=500, null=True, blank=True)
    keyword = models.CharField(max_length=500, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    page_created = models.DateField(null=True, blank=True)
    page_id = models.CharField(null=True, blank=True, max_length=100)
    instagram_url = models.URLField(max_length=100, null=True, blank=True)


    def __str__(self):
        return f'{self.title} --> {self.city}'



class ImportAccountFile(models.Model):
    account_file = models.FileField(upload_to='account_files', help_text="filename.csv file format.\nThe file must include 2 required fields 'username' and 'password'")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)
        file_path = self.account_file.path
        import csv
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                username = row['username']
                password = row['password']
                account = Account(username=username, password=password)
                account.save()

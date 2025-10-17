from django.db import models


class Instructor(models.Model):
    name = models.CharField(max_length=100)
    credentials = models.CharField(max_length=200)

    def __str__(self):
        return self.name

 # Removed rating, review_count, and enrollment_year fields and related methods

class Group(models.Model):
    title = models.CharField(max_length=200)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to="Group_images/", default="Group_images/default.png", verbose_name="Group Image"
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ("python", "Python"),
            ("web-development", "Web Development"),
            ("sql", "SQL"),
            ("php", "PHP"),
        ],
        default="python",
    )

    def __str__(self):
        return self.title

    # Removed rating, review_count, and enrollment_year fields and related methods

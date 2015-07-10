from collections import OrderedDict

from django.db import models
from django.utils import timezone

from accounts.models import User
from rmotr_sis.models import TimeStampedModel
from assignments.models import Assignment


class Course(TimeStampedModel):
    name = models.CharField(max_length=150, blank=False, null=True)
    description = models.TextField(blank=True, null=True)
    code = models.CharField(max_length=45, blank=True, null=True)

    def __str__(self):
        return self.name


class CourseInstance(TimeStampedModel):
    course = models.ForeignKey(Course)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    professor = models.ForeignKey(User, related_name='courseinstance_professor_set')
    lecture_datetime = models.DateTimeField()
    students = models.ManyToManyField(User, blank=True)
    _code = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return '({}) - {} ({} - {})'.format(
            self.code, self.course.name, self.start_date, self.end_date)

    @property
    def code(self):
        return '{}-{}'.format(self.course.code, self._code)

    def is_student(self, student):
        """Returns True if the student is participating in this course
           instance, or False otherwise.
        """
        return student in self.students.all()

    def save(self, *args, **kwargs):
        if self.professor:
            assert self.professor.is_staff
        return super(CourseInstance, self).save(*args, **kwargs)


class Lecture(TimeStampedModel):
    course_instance = models.ForeignKey(CourseInstance)
    title = models.CharField(max_length=150)
    date = models.DateField(default=timezone.now)
    content = models.TextField(blank=True, null=True)
    video_url = models.CharField(max_length=500, blank=True, null=True)
    slides_url = models.CharField(max_length=500, blank=True, null=True)
    assignments = models.ManyToManyField(Assignment, blank=True)
    published = models.BooleanField(default=False)

    def get_assignments_for_user(self, user):
        assignments = self.assignments.all()
        for a in assignments:
            a.status = a.get_status(user)
            a.attempts = a.get_attempts(user)
        return assignments

    def __str__(self):
        return self.title

    def get_assignment_summary(self):
        """"Returns all assignments per student with the current
            assignment status.
        """
        summary = OrderedDict()
        students = self.course_instance.students.all()
        assignments = self.assignments.all()
        for student in students:
            summary.setdefault(student, OrderedDict())
            for a in assignments:
                summary[student][a] = a.get_status(student)
        return summary

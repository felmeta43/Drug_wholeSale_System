from django.contrib.auth.models import AbstractUser
from django.db import models


ETHIOPIAN_REGIONS = [
    ('addis_ababa', 'Addis Ababa'),
    ('afar', 'Afar'),
    ('amhara', 'Amhara'),
    ('benishangul_gumuz', 'Benishangul-Gumuz'),
    ('dire_dawa', 'Dire Dawa'),
    ('gambela', 'Gambela'),
    ('harari', 'Harari'),
    ('oromia', 'Oromia'),
    ('sidama', 'Sidama'),
    ('snnpr', 'SNNPR'),
    ('somali', 'Somali'),
    ('tigray', 'Tigray'),
    ('sw_ethiopia', 'South West Ethiopia'),
]


class UserProfile(AbstractUser):
    ROLES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('sales', 'Sales Rep'),
        ('warehouse', 'Warehouse Staff'),
        ('customer', 'Customer'),
    ]

    role = models.CharField(max_length=20, choices=ROLES, default='sales')
    phone = models.CharField(max_length=20, blank=True)
    region = models.CharField(max_length=30, choices=ETHIOPIAN_REGIONS, blank=True)
    woreda = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    date_joined_company = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['username']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def get_role_display_badge(self):
        colors = {
            'admin': 'danger',
            'manager': 'warning',
            'sales': 'primary',
            'warehouse': 'info',
            'customer': 'secondary',
        }
        return colors.get(self.role, 'secondary')

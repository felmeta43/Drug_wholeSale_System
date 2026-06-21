from django.db import models


class CompanySettings(models.Model):
    """Singleton model — only one row exists. Edit via /settings/ or Django Admin."""

    TIMEZONE_CHOICES = [
        ('Africa/Addis_Ababa', 'Africa/Addis Ababa (EAT)'),
        ('Africa/Nairobi', 'Africa/Nairobi (EAT)'),
        ('Africa/Cairo', 'Africa/Cairo'),
        ('Africa/Lagos', 'Africa/Lagos'),
        ('Africa/Johannesburg', 'Africa/Johannesburg'),
        ('Europe/London', 'Europe/London (GMT/BST)'),
        ('Europe/Paris', 'Europe/Paris (CET)'),
        ('Asia/Dubai', 'Asia/Dubai'),
        ('Asia/Kolkata', 'Asia/Kolkata (IST)'),
        ('America/New_York', 'America/New York (EST)'),
        ('UTC', 'UTC'),
    ]

    DATE_FORMAT_CHOICES = [
        ('d/m/Y', 'DD/MM/YYYY (e.g. 09/06/2026)'),
        ('m/d/Y', 'MM/DD/YYYY (e.g. 06/09/2026)'),
        ('Y-m-d', 'YYYY-MM-DD (e.g. 2026-06-09)'),
        ('d-m-Y', 'DD-MM-YYYY (e.g. 09-06-2026)'),
        ('d M Y', 'DD Mon YYYY (e.g. 09 Jun 2026)'),
    ]

    # ── Identity ──────────────────────────────────────────────────────────────
    name = models.CharField(max_length=200, default='MediWholesale Ethiopia')
    short_name = models.CharField(max_length=50, default='MediWholesale', help_text='Short name shown in sidebar')
    tagline = models.CharField(max_length=200, default='Medical Equipment & Medicine Wholesale System', blank=True)
    logo = models.ImageField(upload_to='company/', null=True, blank=True, help_text='Recommended: 200×60 px PNG with transparent background')
    logo_icon = models.ImageField(upload_to='company/', null=True, blank=True, help_text='Square icon, 64×64 px')

    # ── Contact ───────────────────────────────────────────────────────────────
    address = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, default='Ethiopia')
    phone = models.CharField(max_length=50, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    website = models.URLField(blank=True, default='')

    # ── Legal / Tax ───────────────────────────────────────────────────────────
    tin_number = models.CharField(max_length=50, blank=True, verbose_name='TIN Number', default='')
    vat_number = models.CharField(max_length=50, blank=True, verbose_name='VAT Registration Number', default='')
    business_license = models.CharField(max_length=100, blank=True, default='')
    regulatory_body = models.CharField(max_length=100, default='EFDA', help_text='e.g. EFDA, FDA, WHO, MCA, NAFDAC')
    regulatory_license = models.CharField(max_length=100, blank=True, default='', help_text='License number issued by regulatory body')

    # ── Financial ─────────────────────────────────────────────────────────────
    currency = models.CharField(max_length=10, default='ETB', help_text='ISO 4217 currency code, e.g. ETB, USD, EUR, KES')
    currency_symbol = models.CharField(max_length=10, default='Br', help_text='Symbol shown before amounts, e.g. Br, $, €, KSh')
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00, help_text='VAT percentage, e.g. 15 for 15%')
    vat_label = models.CharField(max_length=30, default='VAT', help_text='e.g. VAT, GST, Sales Tax, TVA')
    withholding_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=2.00, help_text='Withholding tax %')
    enable_vat = models.BooleanField(default=True)

    # ── Numbering Prefixes ────────────────────────────────────────────────────
    invoice_prefix = models.CharField(max_length=20, default='INV-', help_text='e.g. INV-, BILL-')
    po_prefix = models.CharField(max_length=20, default='PO-', help_text='e.g. PO-, ORD-')
    so_prefix = models.CharField(max_length=20, default='SO-', help_text='e.g. SO-, SLS-')
    credit_note_prefix = models.CharField(max_length=20, default='CN-')

    # ── Document Defaults ─────────────────────────────────────────────────────
    invoice_footer = models.TextField(blank=True, default='Thank you for your business.')
    invoice_terms = models.TextField(blank=True, default='Payment is due within the stated payment terms. Late payments may incur interest charges.')
    default_payment_terms_days = models.PositiveIntegerField(default=30)
    expiry_alert_days = models.PositiveIntegerField(default=90, help_text='Warn when items expire within this many days')

    # ── Branding / Theme ──────────────────────────────────────────────────────
    primary_color = models.CharField(max_length=20, default='#006B3F', help_text='Main brand color (hex)')
    secondary_color = models.CharField(max_length=20, default='#FCDD09', help_text='Accent color (hex)')
    accent_color = models.CharField(max_length=20, default='#EF2B2D', help_text='Alert/danger color (hex)')
    sidebar_dark = models.BooleanField(default=True, help_text='Use dark sidebar (recommended)')

    # ── Localisation ─────────────────────────────────────────────────────────
    timezone = models.CharField(max_length=60, choices=TIMEZONE_CHOICES, default='Africa/Addis_Ababa')
    date_format = models.CharField(max_length=20, choices=DATE_FORMAT_CHOICES, default='d/m/Y')
    language_code = models.CharField(max_length=10, default='en-us')

    # ── Feature Flags ─────────────────────────────────────────────────────────
    enable_cold_chain = models.BooleanField(default=True)
    enable_controlled_substances = models.BooleanField(default=True)
    enable_batch_tracking = models.BooleanField(default=True)
    enable_multi_warehouse = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Settings'
        verbose_name_plural = 'Company Settings'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce singleton
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # prevent deletion

    @classmethod
    def get(cls):
        # Read straight from the DB (not cached): this is a single-row,
        # PK lookup, and caching it caused stale values to linger per
        # worker process for up to an hour after a save.
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def vat_rate_decimal(self):
        return self.vat_rate / 100

    @property
    def full_address(self):
        parts = [p for p in [self.address, self.city, self.country] if p]
        return ', '.join(parts)

    @property
    def flag_stripe_css(self):
        """CSS gradient for flag stripe using company colors."""
        return (
            f"linear-gradient(to right, {self.primary_color} 33.3%, "
            f"{self.secondary_color} 33.3%, {self.secondary_color} 66.6%, "
            f"{self.accent_color} 66.6%)"
        )

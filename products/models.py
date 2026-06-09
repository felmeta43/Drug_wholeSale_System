from django.db import models
from django.utils.text import slugify


UNIT_OF_MEASURE_CHOICES = [
    ('piece', 'Piece'),
    ('box', 'Box'),
    ('carton', 'Carton'),
    ('pack', 'Pack'),
    ('bottle', 'Bottle'),
    ('tablet', 'Tablet'),
    ('vial', 'Vial'),
    ('ampoule', 'Ampoule'),
    ('liter', 'Liter'),
    ('ml', 'Milliliter'),
    ('kg', 'Kilogram'),
    ('gram', 'Gram'),
    ('unit', 'Unit'),
    ('set', 'Set'),
    ('pair', 'Pair'),
    ('roll', 'Roll'),
    ('sachet', 'Sachet'),
    ('tube', 'Tube'),
    ('strip', 'Strip'),
    ('inhaler', 'Inhaler'),
]

TAX_CATEGORY_CHOICES = [
    ('vat_exempt', 'VAT Exempt'),
    ('taxable', 'Taxable (15%)'),
]


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_product_count(self):
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    name = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    brand = models.CharField(max_length=200, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    unit_of_measure = models.CharField(max_length=20, choices=UNIT_OF_MEASURE_CHOICES, default='piece')
    efda_registration_number = models.CharField(max_length=100, blank=True, verbose_name='EFDA Registration Number')
    is_controlled_substance = models.BooleanField(default=False)
    requires_cold_chain = models.BooleanField(default=False)
    reorder_level = models.PositiveIntegerField(default=10)
    weight = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True, help_text='Weight in kg')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_default_variant(self):
        return self.variants.filter(is_active=True).first()

    def get_total_stock(self):
        from inventory.models import StockBatch
        result = StockBatch.objects.filter(
            product_variant__product=self
        ).aggregate(total=models.Sum('quantity_available'))
        return result['total'] or 0


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True, blank=True)
    barcode = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    packaging = models.CharField(max_length=200, blank=True)
    strength = models.CharField(max_length=100, blank=True, help_text='For medicines: e.g. 500mg, 250mg/5ml')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    min_selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_category = models.CharField(max_length=20, choices=TAX_CATEGORY_CHOICES, default='taxable')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        ordering = ['product__name', 'strength']

    def __str__(self):
        parts = [self.product.name]
        if self.strength:
            parts.append(self.strength)
        if self.packaging:
            parts.append(self.packaging)
        return ' - '.join(parts)

    def save(self, *args, **kwargs):
        if not self.sku:
            import uuid
            self.sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def get_stock_quantity(self):
        from inventory.models import StockBatch
        result = StockBatch.objects.filter(
            product_variant=self
        ).aggregate(total=models.Sum('quantity_available'))
        return result['total'] or 0


class Medicine(models.Model):
    DOSAGE_FORMS = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('syrup', 'Syrup'),
        ('injection', 'Injection'),
        ('cream', 'Cream'),
        ('ointment', 'Ointment'),
        ('drops', 'Drops'),
        ('inhaler', 'Inhaler'),
        ('suppository', 'Suppository'),
        ('patch', 'Patch'),
        ('powder', 'Powder'),
        ('solution', 'Solution'),
        ('suspension', 'Suspension'),
        ('gel', 'Gel'),
        ('lotion', 'Lotion'),
        ('spray', 'Spray'),
        ('pessary', 'Pessary'),
        ('infusion', 'Infusion'),
        ('effervescent', 'Effervescent Tablet'),
        ('lozenge', 'Lozenge'),
        ('other', 'Other'),
    ]

    ROUTES = [
        ('oral', 'Oral'),
        ('injection_im', 'Injection (IM)'),
        ('injection_iv', 'Injection (IV)'),
        ('injection_sc', 'Injection (SC)'),
        ('topical', 'Topical'),
        ('inhalation', 'Inhalation'),
        ('ophthalmic', 'Ophthalmic'),
        ('otic', 'Otic'),
        ('rectal', 'Rectal'),
        ('vaginal', 'Vaginal'),
        ('sublingual', 'Sublingual'),
        ('transdermal', 'Transdermal'),
        ('nasal', 'Nasal'),
    ]

    STORAGE_CONDITIONS = [
        ('room_temp', 'Room Temperature (15-25°C)'),
        ('cool', 'Cool Place (8-15°C)'),
        ('refrigerate', 'Refrigerate (2-8°C)'),
        ('freeze', 'Freeze (-20°C or below)'),
        ('protect_light', 'Protect from Light'),
        ('protect_moisture', 'Protect from Moisture'),
    ]

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='medicine_info')
    generic_name = models.CharField(max_length=300)
    brand_name = models.CharField(max_length=300, blank=True)
    dosage_form = models.CharField(max_length=30, choices=DOSAGE_FORMS)
    strength = models.CharField(max_length=200, blank=True)
    route_of_administration = models.CharField(max_length=20, choices=ROUTES, default='oral')
    therapeutic_category = models.CharField(max_length=200, blank=True)
    pharmacological_class = models.CharField(max_length=200, blank=True)
    prescription_required = models.BooleanField(default=False)
    is_narcotic = models.BooleanField(default=False)
    is_psychotropic = models.BooleanField(default=False)
    storage_condition = models.CharField(max_length=30, choices=STORAGE_CONDITIONS, default='room_temp')
    shelf_life_months = models.PositiveIntegerField(default=24)
    ethiopian_drug_code = models.CharField(max_length=100, blank=True)
    atc_code = models.CharField(max_length=20, blank=True, verbose_name='ATC Code')
    manufacturer = models.CharField(max_length=300, blank=True)
    country_of_origin = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Medicine'
        verbose_name_plural = 'Medicines'

    def __str__(self):
        return f"{self.generic_name} ({self.dosage_form})"

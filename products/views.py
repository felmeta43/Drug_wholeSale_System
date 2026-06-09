from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Sum
from .models import Category, Product, ProductVariant, Medicine
from .forms import CategoryForm, ProductForm, ProductVariantForm, MedicineForm


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20

    def get_queryset(self):
        qs = Category.objects.filter(parent=None)
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully.')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('category_list')

    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully.')
        return super().form_valid(form)


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 20

    def get_queryset(self):
        qs = Product.objects.select_related('category').order_by('name')
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        is_medicine = self.request.GET.get('is_medicine')
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(brand__icontains=search) |
                           Q(efda_registration_number__icontains=search))
        if category:
            qs = qs.filter(category_id=category)
        if is_medicine == '1':
            qs = qs.filter(medicine_info__isnull=False)
        elif is_medicine == '0':
            qs = qs.filter(medicine_info__isnull=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['total_products'] = Product.objects.filter(is_active=True).count()
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully.')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully.')
        return super().form_valid(form)


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['variants'] = self.object.variants.all()
        context['total_stock'] = self.object.get_total_stock()
        try:
            context['medicine_info'] = self.object.medicine_info
        except Exception:
            context['medicine_info'] = None
        return context


class ProductVariantListView(LoginRequiredMixin, ListView):
    model = ProductVariant
    template_name = 'products/variant_list.html'
    context_object_name = 'variants'
    paginate_by = 30

    def get_queryset(self):
        qs = ProductVariant.objects.select_related('product').order_by('product__name')
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(Q(product__name__icontains=search) | Q(sku__icontains=search) |
                           Q(barcode__icontains=search) | Q(strength__icontains=search))
        return qs


class ProductVariantCreateView(LoginRequiredMixin, CreateView):
    model = ProductVariant
    form_class = ProductVariantForm
    template_name = 'products/variant_form.html'
    success_url = reverse_lazy('variant_list')

    def form_valid(self, form):
        messages.success(self.request, 'Product variant created successfully.')
        return super().form_valid(form)


class ProductVariantUpdateView(LoginRequiredMixin, UpdateView):
    model = ProductVariant
    form_class = ProductVariantForm
    template_name = 'products/variant_form.html'
    success_url = reverse_lazy('variant_list')

    def form_valid(self, form):
        messages.success(self.request, 'Variant updated successfully.')
        return super().form_valid(form)


class MedicineListView(LoginRequiredMixin, ListView):
    model = Medicine
    template_name = 'products/medicine_list.html'
    context_object_name = 'medicines'
    paginate_by = 30

    def get_queryset(self):
        qs = Medicine.objects.select_related('product').order_by('generic_name')
        search = self.request.GET.get('search')
        dosage_form = self.request.GET.get('dosage_form')
        therapeutic = self.request.GET.get('therapeutic')
        if search:
            qs = qs.filter(Q(generic_name__icontains=search) | Q(brand_name__icontains=search) |
                           Q(ethiopian_drug_code__icontains=search))
        if dosage_form:
            qs = qs.filter(dosage_form=dosage_form)
        if therapeutic:
            qs = qs.filter(therapeutic_category__icontains=therapeutic)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dosage_forms'] = Medicine.DOSAGE_FORMS
        return context


class MedicineCreateView(LoginRequiredMixin, CreateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'products/medicine_form.html'
    success_url = reverse_lazy('medicine_list')

    def form_valid(self, form):
        messages.success(self.request, 'Medicine information added successfully.')
        return super().form_valid(form)


class MedicineUpdateView(LoginRequiredMixin, UpdateView):
    model = Medicine
    form_class = MedicineForm
    template_name = 'products/medicine_form.html'
    success_url = reverse_lazy('medicine_list')

    def form_valid(self, form):
        messages.success(self.request, 'Medicine information updated successfully.')
        return super().form_valid(form)


@login_required
def variant_price_api(request, pk):
    """AJAX endpoint: return selling price and stock for a product variant."""
    from django.http import JsonResponse
    variant = get_object_or_404(ProductVariant, pk=pk)
    return JsonResponse({
        'id': variant.pk,
        'sku': variant.sku,
        'selling_price': str(variant.selling_price),
        'cost_price': str(variant.cost_price),
        'tax_category': variant.tax_category,
        'stock': variant.get_stock_quantity(),
        'strength': variant.strength,
        'packaging': variant.packaging,
    })


@login_required
def product_search_api(request):
    """AJAX search: return matching product variants for order forms."""
    from django.http import JsonResponse
    q = request.GET.get('q', '')
    variants = ProductVariant.objects.filter(
        product__name__icontains=q, is_active=True
    ).select_related('product')[:30]
    results = [
        {
            'id': v.pk,
            'text': str(v),
            'price': str(v.selling_price),
            'sku': v.sku,
        }
        for v in variants
    ]
    return JsonResponse({'results': results})

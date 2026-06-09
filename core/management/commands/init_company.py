"""
Create or reset the company settings record.
Usage:
  python manage.py init_company
  python manage.py init_company --name "Medico Supplies Ltd" --country "Kenya" --currency KES --symbol KSh --vat 16
"""
from django.core.management.base import BaseCommand, CommandError
from core.models import CompanySettings


class Command(BaseCommand):
    help = 'Initialize or reset company settings'

    def add_arguments(self, parser):
        parser.add_argument('--name', default='MediWholesale Ethiopia')
        parser.add_argument('--short_name', default='MediWholesale')
        parser.add_argument('--tagline', default='Medical Equipment & Medicine Wholesale System')
        parser.add_argument('--country', default='Ethiopia')
        parser.add_argument('--city', default='Addis Ababa')
        parser.add_argument('--currency', default='ETB')
        parser.add_argument('--symbol', default='Br')
        parser.add_argument('--vat', type=float, default=15.0)
        parser.add_argument('--vat_label', default='VAT')
        parser.add_argument('--timezone', default='Africa/Addis_Ababa')
        parser.add_argument('--regulatory_body', default='EFDA')
        parser.add_argument('--primary_color', default='#006B3F')
        parser.add_argument('--secondary_color', default='#FCDD09')
        parser.add_argument('--accent_color', default='#EF2B2D')
        parser.add_argument('--invoice_prefix', default='INV-')
        parser.add_argument('--po_prefix', default='PO-')
        parser.add_argument('--so_prefix', default='SO-')

    def handle(self, *args, **options):
        obj, created = CompanySettings.objects.get_or_create(pk=1)
        obj.name = options['name']
        obj.short_name = options['short_name']
        obj.tagline = options['tagline']
        obj.country = options['country']
        obj.city = options['city']
        obj.currency = options['currency']
        obj.currency_symbol = options['symbol']
        obj.vat_rate = options['vat']
        obj.vat_label = options['vat_label']
        obj.timezone = options['timezone']
        obj.regulatory_body = options['regulatory_body']
        obj.primary_color = options['primary_color']
        obj.secondary_color = options['secondary_color']
        obj.accent_color = options['accent_color']
        obj.invoice_prefix = options['invoice_prefix']
        obj.po_prefix = options['po_prefix']
        obj.so_prefix = options['so_prefix']
        obj.save()
        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(
            f'{action} company settings: {obj.name} | {obj.currency} | VAT {obj.vat_rate}%'
        ))

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.apps import apps as django_apps
        from .signals import register_audit, connect_auth_signals

        tracked_labels = [
            'products.Product', 'products.ProductVariant', 'products.Category',
            'inventory.StockBatch',
            'warehouse.Warehouse', 'warehouse.StockTransfer',
            'customers.Customer', 'suppliers.Supplier',
            'orders.SalesOrder', 'orders.PurchaseOrder',
            'invoices.Invoice', 'invoices.Payment',
            'accounts.UserProfile',
            'core.CompanySettings',
        ]
        models = []
        for label in tracked_labels:
            try:
                models.append(django_apps.get_model(label))
            except LookupError:
                continue
        register_audit(*models)
        connect_auth_signals()

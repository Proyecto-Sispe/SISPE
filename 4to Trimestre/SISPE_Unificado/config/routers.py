"""Envia cada app a su base de datos."""

APP_DB = {
    "mesas_pedidos": "mesas",
    "base_datos": "sistema",
    "seguimiento_pedidos": "sistema",
    "dashboard": "sistema",
}


class SispeRouter:
    def db_for_read(self, model, **hints):
        return APP_DB.get(model._meta.app_label, "default")

    def db_for_write(self, model, **hints):
        return APP_DB.get(model._meta.app_label, "default")

    def allow_relation(self, obj1, obj2, **hints):
        return obj1._state.db == obj2._state.db

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return APP_DB.get(app_label, "default") == db

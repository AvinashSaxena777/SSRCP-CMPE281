# home/dao/base_dao.py
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

class BaseDAO:
    model = None

    @classmethod
    def get_all_active(cls):
        return cls.model.objects.filter(isActive=True)

    @classmethod
    def get_by_id(cls, obj_id):
        try:
            return cls.model.objects.get(id=obj_id)
        except ObjectDoesNotExist:
            return None

    @classmethod
    @transaction.atomic
    def delete(cls, obj_id):
        obj = cls.get_by_id(obj_id)
        if obj:
            obj.isActive = False
            obj.save()
        return obj

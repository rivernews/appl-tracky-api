from django.core.exceptions import FieldDoesNotExist

def is_instance_field_exist(instance, field_name):
    try:
        instance.__class__._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False

def is_model_field_exist(model, field_name):
    try:
        model._meta.get_field(field_name)
        return True
    except FieldDoesNotExist:
        return False

def get_model_all_field_names(model):
    return [ field.name for field in model._meta.get_fields() ]
    
def update_instance(instance, fields_data: dict, excluded_fields: dict = {}) -> None:
    valid_field_names = get_model_all_field_names(instance.__class__)

    for valid_field_name in valid_field_names:
        # only update fields that are in model's schema
        # any redundent field data provided from frontend will be ignored
        if valid_field_name in fields_data and (not valid_field_name in excluded_fields):
            setattr(instance, valid_field_name, fields_data.get(valid_field_name))
    
    instance.save()
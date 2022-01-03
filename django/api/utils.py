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

def create_instance(model, fields_data: dict, excluded_fields={}) -> None:
    valid_field_names = get_model_all_field_names(model)

    create_instance_kwargs = {}
    for valid_field_name in valid_field_names:
        # only update fields that are in model's schema
        # any redundent field data provided from frontend will be ignored
        # also make sure don't write to uuid
        if valid_field_name != 'uuid' and valid_field_name in fields_data and (not valid_field_name in excluded_fields):

            if any([
                isinstance(fields_data[valid_field_name], dict),
                isinstance(fields_data[valid_field_name], list)
            ]):
                raise ValueError(f'Field `{valid_field_name}:{fields_data[valid_field_name]}` contains complex structure like dict or list. \
                    Such field should be handled by one-to-one or many-to-many logic, and not in `create_instance()`, which only handles primitive values. \
                    You should add this field to `self.one_to_one_fields` or `self.many_to_many_fields` to Serializer of the parent class.')

            # if have no meaningful data, then skip it and don't even pass in into .objects.create()
            if fields_data[valid_field_name] != None and fields_data[valid_field_name] != '':
                create_instance_kwargs[valid_field_name] = fields_data.get(valid_field_name)

    instance = model.objects.create(**create_instance_kwargs)
    instance.save()
    return instance

def update_instance(instance, fields_data: dict, excluded_fields: dict = {}) -> None:
    valid_field_names = get_model_all_field_names(instance.__class__)

    for valid_field_name in valid_field_names:
        # only update fields that are in model's schema
        # any redundent field data provided from frontend will be ignored
        # also make sure don't write to uuid
        if valid_field_name != 'uuid' and valid_field_name in fields_data and (not valid_field_name in excluded_fields):
            setattr(instance, valid_field_name, fields_data.get(valid_field_name))

    instance.save()
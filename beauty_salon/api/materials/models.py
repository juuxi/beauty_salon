from api.models import ModelWithName, CodedModel, ModelWithMeasuringUnit


class Material(ModelWithName, CodedModel, ModelWithMeasuringUnit):

    class Meta:
        db_table = 'materials'

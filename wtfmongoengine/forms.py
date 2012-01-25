from wtforms.form import Form, FormMeta


class DocumentFieldConverter(object):

    def convert(self, model_field):
        return model_field


class DocumentFormMetaClassBase(type):
    """
    Meta-class for generating the actual WTForms class.
    """
    def __new__(cls, name, bases, attrs):
        if 'Meta' in attrs:
            document = attrs['Meta'].document
            fields = getattr(attrs['Meta'], 'fields', None)
            exclude = getattr(attrs['Meta'], 'exclude', None)

            attrs = DocumentFormMetaClassBase.model_fields(
                document, fields, exclude)

        return super(
            DocumentFormMetaClassBase, cls).__new__(cls, name, bases, attrs)

    @classmethod
    def model_fields(cls, document, fields=None, exclude=None):
        """
        Convert the given document into a WTForm fields.

        :param document:
            The Mongoengine document to convert.

        :param fields:
            If given, it will only parse these fields.

        :param exclude:
            If given, it will exclude these fields from parsing.

        """
        field_names = document._fields.keys()

        if fields:
            field_names = (f for f in field_names if f in fields)
        elif exclude:
            field_names = (f for f in field_names if f not in exclude)

        converter = DocumentFieldConverter()
        field_dict = {}

        for field_name in field_names:
            model_field = document._fields[field_name]
            wtf_field = converter.convert(model_field)
            if wtf_field:
                field_dict[field_name] = wtf_field

        return field_dict


class DocumentFormMetaClass(DocumentFormMetaClassBase, FormMeta):
    # This object, combining the two meta classes, is needed to avoid conflicts
    pass


class DocumentForm(Form):
    """
    Baseclass for constructing a WTF form from a Mongoengine Document class.
    """
    __metaclass__ = DocumentFormMetaClass

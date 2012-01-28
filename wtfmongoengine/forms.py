from wtforms import validators, fields
from wtforms.form import Form, FormMeta


class DocumentFieldConverter(object):
    """
    Convert the given ``document`` into WTForm fields.

    :param document:
        The Mongoengine document to convert.

    :param fields:
        If given, it will only parse these fields. (optional)

    :param exclude:
        If given, it will exclude these fields from parsing. (optional)

    """

    def __init__(self, document, fields=None, exclude=None):
        self.document = document
        self.only_fields = fields
        self.exclude_fields = exclude

    @property
    def fields(self):
        """
        Return a ``dict`` containing the WTForms fields.

        :return:
            A ``dict`` with the following as key / value:

            key
                The (internal) field name.

            value
                An object representing the WTForms field.

        """
        field_dict = {}
        field_names = self.document._fields.keys()

        if self.only_fields:
            field_names = (f for f in field_names if f in self.only_fields)
        elif self.exclude_fields:
            field_names = (
                f for f in field_names if f not in self.exclude_fields)

        for field_name in field_names:
            model_field = self.document._fields[field_name]
            wtf_field = self.convert(model_field)
            if wtf_field:
                field_dict[field_name] = wtf_field

        return field_dict

    def convert(self, document_field):
        """
        Convert ``document_field`` into a WTForms field.

        :param document_field:
            Instance of a Mongoengine field class.

        :return:
            Instance of a WTForms instance.

        """
        kwargs = {
            'label': document_field.verbose_name or document_field.name,
            'description': document_field.help_text or '',
            'validators': [],
            'default': document_field.default,
        }

        if document_field.required:
            kwargs['validators'].append(validators.Required())

        if document_field.choices:
            kwargs['choices'] = document_field.choices
            return fields.SelectField(**kwargs)

        document_field_type = type(document_field).__name__

        convert_method_name = 'from_{0}'.format(document_field_type.lower())

        if hasattr(self, convert_method_name):
            return getattr(self, convert_method_name)(document_field, **kwargs)
        else:
            return None

    def set_common_string_kwargs(self, document_field, kwargs):
        """
        Set common string arguments.

        :param document_field:
            Instance of Mongoengine field.

        :param kwargs:
            A ``dict`` that needs to be updated with the new arguments.

        """
        if document_field.max_length or document_field.min_length:
            kwargs['validators'].append(
                validators.Length(
                    max=document_field.max_length or -1,
                    min=document_field.min_length or -1
                )
            )

        if document_field.regex:
            kwargs['validators'].append(
                validators.Regexp(regex=document_field.regex)
            )

    def set_common_number_kwargs(self, document_field, kwargs):
        """
        Set common number arguments.

        :param document_field:
            Instance of Mongoengine field.

        :param kwargs:
            A ``dict`` that needs to be updated with the new arguments.

        """
        if document_field.max_value or document_field.min_value:
            kwargs['validators'].append(
                validators.NumberRange(
                    max=document_field.max_value,
                    min=document_field.min_value
                )
            )

    def from_stringfield(self, document_field, **kwargs):
        """
        Convert ``document_field`` into a ``TextField``.

        :param document_field:
            Instance of Mongoengine field.

        :return:
            Instance of :py:class:`!wtforms.fields.TextField`.

        """
        self.set_common_string_kwargs(document_field, kwargs)
        return fields.TextField(**kwargs)

    def from_urlfield(self, document_field, **kwargs):
        """
        Convert ``document_field`` into a ``TextField`` with URL validation.

        :param document_field:
            Instance of Mongoengine field.

        :return:
            Instance of :py:class:`!wtforms.fields.TextField`.

        """
        kwargs['validators'].append(validators.URL())
        # TODO: cleanyp set_common_string_kwargs?
        self.set_common_string_kwargs(document_field, kwargs)
        return fields.TextField(**kwargs)

    def from_emailfield(self, document_field, **kwargs):
        """
        Convert ``document_field`` into a ``TextField`` with e-mail validation.

        :param document_field:
            Instance of Mongoengine field.

        :return:
            Instance of :py:class:`!wtforms.fields.TextField`.

        """
        kwargs['validators'].append(validators.Email())
        self.set_common_string_kwargs(document_field, kwargs)
        return fields.TextField(**kwargs)

    def from_intfield(self, document_field, **kwargs):
        """
        Convert ``document_field`` into a ``IntegerField``.

        :param document_field:
            Instance of Mongoengine field.

        :return:
            Instance of :py:class:`!wtforms.fields.IntegerField`.

        """
        self.set_common_number_kwargs(document_field, kwargs)
        return fields.IntegerField(**kwargs)

    def from_floatfield(self, document_field, **kwargs):
        """
        Convert ``document_field`` into a ``FloatField``.

        :param document_field:
            Instance of Mongoengine field.

        :return:
            Instance of :py:class:`!wtforms.fields.FloatField`.

        """
        self.set_common_number_kwargs(document_field, kwargs)
        return fields.FloatField(**kwargs)

    def from_decimalfield(self, document_field, **kwargs):
        """
        Convert ``document_field`` into a ``DecimalField``.

        :param document_field:
            Instance of Mongoengine field.

        :return:
            Instance of :py:class:`!wtforms.fields.DecimalField`.

        """
        self.set_common_number_kwargs(document_field, kwargs)
        return fields.DecimalField(**kwargs)

    def from_datetimefield(self, document_field, **kwargs):
        """
        Convert ``document_field`` into a ``DateTimeField``.

        :param document_field:

        :return:
            Instance of :py:class:`!wtforms.fields.DateTimeField`.

        """
        return fields.DateTimeField(**kwargs)

    def from_complexdatetimefield(self, document_field, **kwargs):
        return None

    def from_listfield(self, document_field, **kwargs):
        return None

    def from_sortedlistfield(self, document_field, **kwargs):
        return None

    def from_dictfield(self, document_field, **kwargs):
        return None

    def from_mapfield(self, document_field, **kwargs):
        return None

    def from_objectidfield(self, document_field, **kwargs):
        return None

    def from_referencefield(self, document_field, **kwargs):
        return None

    def from_genericreferencefield(self, document_field, **kwargs):
        return None

    def from_embeddeddocumentfield(self, document_field, **kwargs):
        return None

    def from_genericembeddeddocumentfield(self, document_field, **kwargs):
        return None

    def from_booleanfield(self, document_field, **kwargs):
        """
        Convert ``document_field`` into a ``BooleanField``.

        :param document_field:
            Instance of Mongoengine field.

        :return:
            Instance of :py:class:`!wtforms.fields.BooleanField`.

        """
        return fields.BooleanField(**kwargs)

    def from_filefield(self, document_field, **kwargs):
        return None

    def from_binaryfield(self, document_field, **kwargs):
        return None

    def from_geopointfield(self, document_field, **kwargs):
        return None

    def from_sequencefield(self, document_field, **kwargs):
        return None


class DocumentFormMetaClassBase(type):
    """
    Meta-class for generating the actual WTForms class.
    """
    def __new__(cls, name, bases, attrs):
        if 'Meta' in attrs:
            document = attrs['Meta'].document
            fields = getattr(attrs['Meta'], 'fields', None)
            exclude = getattr(attrs['Meta'], 'exclude', None)

            converter = DocumentFieldConverter(document, fields, exclude)
            attrs = converter.fields

        return super(
            DocumentFormMetaClassBase, cls).__new__(cls, name, bases, attrs)


class DocumentFormMetaClass(DocumentFormMetaClassBase, FormMeta):
    # This object, combining the two meta classes, is needed to avoid conflicts
    pass


class DocumentForm(Form):
    """
    Baseclass for constructing a WTF form from a Mongoengine Document class.
    """
    __metaclass__ = DocumentFormMetaClass

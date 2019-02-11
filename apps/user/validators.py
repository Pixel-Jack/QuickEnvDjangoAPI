from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class GenericInternationalPhoneNumberValidator(RegexValidator):
    regex = r'\+(9[976]\d|8[987530]\d|6[987]\d|5[90]\d|42\d|3[875]\d|2[98654321]\d|9[8543210]|8[6421]|6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)\d{1,14}$'
    message = _(
        'Enter a phone number. This number must in be the generic international format.'
    )
    flags = 0


@deconstructible
class NotEmailValidator(EmailValidator):
    message = _("You can't use an email address for this field.")

    def __call__(self, value):
        # we negate the result of EmailValidator
        try:
            super().__call__(value)
        except ValidationError:
            return

        raise ValidationError(self.message, code=self.code)


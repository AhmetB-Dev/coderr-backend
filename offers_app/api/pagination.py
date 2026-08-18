from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"

    def get_page_size(self, request):
        """Return a positive page size or reject an invalid value."""
        value = request.query_params.get(self.page_size_query_param)
        if value is None:
            return self.page_size
        try:
            page_size = int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError("page_size must be an integer.") from exc
        if page_size < 1:
            raise ValidationError("page_size must be greater than zero.")
        return page_size

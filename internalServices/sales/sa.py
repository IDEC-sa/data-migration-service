from django.core.paginator import Paginator, EmptyPage

class MyPaginator(Paginator):
    def validate_number(self, number):
        try:
            return super().validate_number(number)
        except EmptyPage:
            if int(number) > 1:
                return self.num_pages
            elif int(number) < 1:
                return 1
            else:
                raise

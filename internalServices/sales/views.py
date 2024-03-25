from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView, FormView, CreateView, UpdateView, ListView, DetailView
from .forms import UploadForm, StaticDataForm, ProductsForm
import io
from django.urls import reverse
from .services import convert_xlsx, createProdsFromQuoteRequest, validate, draften, create_prods
from .models import QuoteRequest, Product
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .permissions import SalesManPermissionMixin, OwnershipMixin, OwnerPermissionMixin
from django.db import transaction
from django.contrib.auth.mixins import PermissionRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

class DashboardView(LoginRequiredMixin,SalesManPermissionMixin, TemplateView):
    template_name = "dashboard.html"

class excelUploader(LoginRequiredMixin, SalesManPermissionMixin, CreateView):
    template_name = 'xlsxuopload.html'
    form_class = UploadForm

    def get_success_url(self) -> str:
        return reverse("reviewquote", kwargs={
             "quoteId": self.get_form().instance.id
        })

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
         self.object = form.save(commit=False)
         self.object.user = self.request.user
         self.object = form.save()
         return super().form_valid(form)

class ReviewProducts(LoginRequiredMixin, SalesManPermissionMixin, OwnerPermissionMixin, TemplateView):
    template_name = 'convert_prods.html'

    def get_object(self):
        return get_object_or_404(QuoteRequest, pk=self.kwargs["quoteId"])

    def get_context_data(self, **kwargs) -> dict[str, ]:
        print(self.request.user)
        context =  super().get_context_data(**kwargs)
        quoteRequest = self.get_object()
        excel = quoteRequest.excel
        df = convert_xlsx(excel)
        context['table_data'] = df
        context["create_url"] = quoteRequest.getCreateUrl()
        return context

#handle creation and errors when creating the model important!!!!
## handle if the quote is of certain state "draft   "
class CreateProducts(LoginRequiredMixin, SalesManPermissionMixin, OwnerPermissionMixin,
                     UserPassesTestMixin,
                      TemplateView):

    def test_func(self) -> bool | None:
        quoteRequest = self.get_object()
        return self.request.user == quoteRequest.user
    
    def get_object(self):
        return get_object_or_404(QuoteRequest, pk=self.kwargs["quoteId"])

    def get(self, request, *args, **kwargs):
        quoteRequest = QuoteRequest.objects.get(pk = self.kwargs["quoteId"])
        erros = createProdsFromQuoteRequest(quoteRequest)
        if erros:
            self.template_name = "failure.html"
            context = self.get_context_data(**kwargs)
            context["errors"] = erros
            context["review_url"] = quoteRequest.getRewviewUrl()
            return self.render_to_response(context)
        else:
            return redirect(reverse("detail-quote", kwargs={
                 "pk":quoteRequest.id
            }))

class AllQuotesView(LoginRequiredMixin, ListView):
    model = QuoteRequest
    template_name = "allquotes.html"

    def get_queryset(self):
        return QuoteRequest.objects.filter(user = self.request.user).order_by('-date_created', 'id')

class InProcessQuotesView(AllQuotesView):
    def get_queryset(self):
        return QuoteRequest.objects.filter(user = self.request.user).exclude(state="dra").order_by('-date_created', 'id')

class DraftQuotesView(AllQuotesView):
        def get_queryset(self):
            return QuoteRequest.objects.filter(user = self.request.user, state="dra").order_by('-date_created', 'id')

class QuoteDetailView(LoginRequiredMixin, OwnerPermissionMixin, DetailView):
    model = QuoteRequest
    template_name = "quote.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: io) -> HttpResponse:
        quoteReq = get_object_or_404(QuoteRequest, pk = self.kwargs["pk"])
        if not quoteReq.productsAdded:
              return redirect(reverse("reviewquote", kwargs={
                   "quoteId": self.kwargs["pk"]
              }))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict[str, ]:
        context =  super().get_context_data(**kwargs)
        return context

class QuoteUpdateView(LoginRequiredMixin, SalesManPermissionMixin, OwnerPermissionMixin, UpdateView):
    model = QuoteRequest  
    fields = [
          "priceUnit",
          "contract",
          "excel"
     ]

    exclude = ["excel"]
    success_url  = "/"
    template_name = "updatequote.html"

    def get(self, request: HttpRequest, *args: str, **kwargs: io) -> HttpResponse:
         obj = self.get_object()
         if obj:
              if obj.state != "dra":
                   self.fields = ["priceUnit","contract"]
         return super().get(request, *args, **kwargs)


class staticDataView(LoginRequiredMixin, SalesManPermissionMixin, CreateView):

    template_name = 'add_static_data.html'
    form_class = StaticDataForm

    def get_success_url(self) -> str:
        return reverse("detail-quote", kwargs={
             "pk": self.kwargs["quoteId"]
        })
    
    @transaction.atomic
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save(commit=False)
        quoteReq = get_object_or_404(QuoteRequest, pk = self.kwargs["quoteId"])
        self.object = form.save()
        quoteReq.static_data = self.object
        quoteReq.state = "quo"
        quoteReq.save()
        return super().form_valid(form)

class QuoteValidateView(LoginRequiredMixin, SalesManPermissionMixin, OwnerPermissionMixin, View):
    
    key = "pk"
    ownedClass = QuoteRequest
    
    def get(self, request: HttpRequest, *args: io, **kwargs: io) -> HttpResponse:
        quoteReq = self.get_object()
        validate(quoteReq)
        return redirect(self.get_success_url())
    
    def get_object(self):
        return get_object_or_404(QuoteRequest, pk = self.kwargs["pk"])

    def get_success_url(self) -> str:
         return reverse("detail-quote", kwargs={
             "pk": self.kwargs["pk"]
        })
    def test_func(self) -> bool | None:
        return super().test_func()

class QuoteDraftenView(LoginRequiredMixin, OwnerPermissionMixin, SalesManPermissionMixin, View):

    def get(self, request: HttpRequest, *args: io, **kwargs: io) -> HttpResponse:
        quoteReq = self.get_object()
        draften(quoteReq)
        return redirect(self.get_success_url())

    def get_object(self):
        return get_object_or_404(QuoteRequest, pk = self.kwargs["pk"])

    def get_success_url(self) -> str:
         return reverse("detail-quote", kwargs={
             "pk": self.kwargs["pk"]
        })
    def test_func(self) -> bool | None:
        return super().test_func()

class AddProducts(LoginRequiredMixin, UserPassesTestMixin, FormView):
    form_class = ProductsForm
    template_name = "add-products.html"
    success_url = "success.html"

    def test_func(self) -> bool | None:
        return self.request.user.is_superuser

    def get_success_url(self) -> str:
        return reverse("sales-dashboard")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            print("done")
            print(form.cleaned_data["products"])
            errs = create_prods(form.cleaned_data["products"])
            if errs:
                print(errs)
                return self.form_invalid(form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class ProductsView(ListView):
    template_name = "products.html"
    model = Product
    paginate_by = 30

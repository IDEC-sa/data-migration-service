from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import View, TemplateView, FormView, CreateView, UpdateView, ListView, DetailView
from .forms import UploadForm, StaticDataForm, ProductsForm, CompaniesForm
import io
from django.urls import reverse
from .services import generateCsv, convert_xlsx, create_comps, createProdsFromQuoteRequest, validate, draften, create_prods
from .models import QuoteRequest, Product, Company
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .permissions import SalesManPermissionMixin, SuperUserPermissionMixin, SalesDirectoryPermissionMixin, OwnerPermissionMixin
from django.db import transaction
from django.contrib.auth.mixins import PermissionRequiredMixin
from dal import autocomplete
from django.db.models import Q
from .filters import FilterQuotes, SuperFilterQuotes
from django_filters.views import FilterView

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
            self.template_name = "convert_prods.html"
            context = self.get_context_data(**kwargs)
            context["errors"] = erros
            context["review_url"] = quoteRequest.getRewviewUrl()
            df = convert_xlsx(quoteRequest.excel)
            context['table_data'] = df
            return self.render_to_response(context)
        else:
            return redirect(reverse("detail-quote", kwargs={
                 "pk":quoteRequest.id
            }))

class AllQuotesView(LoginRequiredMixin, ListView):
    model = QuoteRequest
    template_name = "allquotes.html"

    def get_queryset(self):
        user = self.request.user
        if not user.sysRole == "sman" or user.is_superuser:
            return QuoteRequest.objects.filter().order_by('-date_created', 'id')
        else:
            return QuoteRequest.objects.filter(user = self.request.user).order_by('-date_created', 'id')

class InProcessQuotesView(AllQuotesView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.exclude(state="dra")

class DraftQuotesView(AllQuotesView):
        def get_queryset(self):
            return super().get_queryset().filter(state="dra")

class QuoteDetailView(LoginRequiredMixin, DetailView):
    model = QuoteRequest
    template_name = "quote.html"
    permission_required = ["can_view_quoterequest"]

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
    success_url  = "/"
    template_name = "add-excel.html"
    form_class = UploadForm
    def get(self, request: HttpRequest, *args: str, **kwargs: io) -> HttpResponse:
         return super().get(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse("detail-quote", kwargs={
             "pk": self.kwargs["pk"]
        })
    
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
    template_name = "add-excel.html"
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


class ProductsView(ListView):
    template_name = "products.html" ## edit
    model = Company
    paginate_by = 30


class AddCompanies(LoginRequiredMixin, UserPassesTestMixin, FormView):

    form_class = CompaniesForm
    template_name = "add-excel.html"
    success_url = "success.html" # get success url override

    def test_func(self) -> bool | None:
        return self.request.user.is_superuser

    def get_success_url(self) -> str:
        return reverse("sales-dashboard")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            print(form.cleaned_data["Companies"])
            errs = create_comps(form.cleaned_data["Companies"])
            if errs:
                print(errs)
                return self.form_invalid(form)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class CompanyAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Company.objects.none()
        qs = Company.objects.all()
        if self.q:
            qs = qs.filter(Q(latin_name__icontains=self.q) | 
                           Q(arabic_name__icontains=self.q) | 
                           Q(code__istartswith=self.q))
        return qs
    
    def get_result_label(self, item):
        return "".join(item.latin_name + " | " + item.arabic_name + " | " + f"[{item.code}]")

    def get_selected_result_label(self, item):
        return item.latin_name


class GenerateCsvForQuote(View):
    def get(self, request, *args, **kwargs):
        generateCsv(get_object_or_404(QuoteRequest, pk = self.kwargs["pk"]))
        return HttpResponse("success")



class QuotesFilterView(FilterView):
    template_name = 'allquotes.html'
    filterset_class = FilterQuotes
    context_object_name = 'object_list'
    
    def get_queryset(self):
        user = self.request.user
        if not user.sysRole == "sman" or user.is_superuser:
            return QuoteRequest.objects.filter()
        else:
            return QuoteRequest.objects.filter(user = self.request.user)
    

    def get_filterset_class(self):
        user = self.request.user
        if not user.sysRole == "sman" or user.is_superuser:
            return SuperFilterQuotes
        else:
            return FilterQuotes

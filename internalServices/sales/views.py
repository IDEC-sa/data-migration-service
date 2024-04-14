from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import View, TemplateView, FormView, CreateView, UpdateView, ListView, DetailView
from .forms import UploadForm, StaticDataForm, ProductsForm, CompaniesForm
import io
from django.urls import reverse
from .services import generateCsv, convert_xlsx, create_comps, createProdsFromQuoteRequest, validate, draften, create_prods
from .models import QuoteRequest, Product, Company, StaticData
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .permissions import OwnerShipTestMixin, SuperUserPermissionMixin, SalesDirectoryPermissionMixin, OwnerPermissionMixin
from django.db import transaction
from django.contrib.auth.mixins import PermissionRequiredMixin
from dal import autocomplete
from django.db.models import Q
from .filters import FilterQuotes, SuperFilterQuotes
from .sa import MyPaginator
from django_filters.views import FilterView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "index.html"

##change the dashboard based on the sysrole maybe needed?
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

class excelUploader(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('sales.add_quoterequest')
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

class ReviewProducts(LoginRequiredMixin, PermissionRequiredMixin, OwnerShipTestMixin , TemplateView):
    template_name = 'convert_prods.html'
    permission_required = ('sales.can_review_quote', )

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
        context["edit_url"] = quoteRequest.getEditUrl()
        return context

#handle creation and errors when creating the model important!!!!
## handle if the quote is of certain state "draft   "
class CreateProducts(LoginRequiredMixin, PermissionRequiredMixin,
                     OwnerShipTestMixin,
                      TemplateView):
    permission_required = ("sales.change_quoterequest")


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
            context["edit_url"] = quoteRequest.getEditUrl()
            df = convert_xlsx(quoteRequest.excel)
            context['table_data'] = df
            return self.render_to_response(context)
        else:
            return redirect(reverse("detail-quote", kwargs={
                 "pk":quoteRequest.id
            }))

class AllQuotesView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = ("sales.view_quoterequest")
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

class QuoteDetailView(LoginRequiredMixin, OwnerPermissionMixin, OwnerShipTestMixin, DetailView):
    model = QuoteRequest
    template_name = "quote.html"
    permission_required = ["sales.view_quoterequest"]

    def get(self, request: HttpRequest, *args: str, **kwargs: io) -> HttpResponse:
        quoteReq = get_object_or_404(QuoteRequest, pk = self.kwargs["pk"])
        if not quoteReq.productsAdded:
              return redirect(reverse("reviewquote", kwargs={
                   "quoteId": self.kwargs["pk"]
              }))
        return super().get(request, *args, **kwargs)

    # def get_context_data(self, **kwargs) -> dict[str, ]:
    #     context =  super().get_context_data(**kwargs)
    #     return context

class QuoteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):

    permission_required = ("sales.change_quoterequest")
    model = QuoteRequest  
    success_url  = "/"
    template_name = "updatequote.html"
    form_class = StaticDataForm

    def get_forms(self) -> BaseModelForm:
        kwargs = self.get_form_kwargs()
        kwargs.pop("instance")
        if self.get_object().isReady():
            return {"form1": UploadForm(**kwargs, instance=self.get_object()), 
                    "form2": StaticDataForm(**kwargs, instance=self.get_object().static_data)}
        else:
            return {"form1":UploadForm(**kwargs, instance=self.get_object())}

    def post(self, request: HttpRequest, *args: str, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        forms = self.get_forms()
        if all([val.is_valid() for val in forms.values()]):
            for form in forms.values():
                form.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render_to_response(context = forms)

    def get_context_data(self, **kwargs) -> dict[str, ]:
        cn = super().get_context_data(**kwargs)
        # instance = self.get_object()
        cn.update(**self.get_forms())
        return cn

    def get_success_url(self) -> str:
        return reverse("detail-quote", kwargs={
             "pk": self.kwargs["pk"]
        })
    def get_object(self) -> Model:
        return get_object_or_404(QuoteRequest, pk = self.kwargs["pk"])
    
class staticDataView(LoginRequiredMixin, PermissionRequiredMixin, OwnerShipTestMixin, CreateView):
    permission_required = ("sales.can_add_static_to_quote")
    template_name = 'add_static_data.html'
    form_class = StaticDataForm

    def get_success_url(self) -> str:
        return reverse("detail-quote", kwargs={
             "pk": self.kwargs["quoteId"]
        })

    def get_object(self) -> Model:
        return get_object_or_404(QuoteRequest, pk = self.kwargs["quoteId"])

    @transaction.atomic
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        self.object = form.save(commit=False)
        quoteReq = get_object_or_404(QuoteRequest, pk = self.kwargs["quoteId"])
        self.object = form.save()
        quoteReq.static_data = self.object
        quoteReq.state = "quo"
        quoteReq.save()
        return super().form_valid(form)

class QuoteValidateView(LoginRequiredMixin, PermissionRequiredMixin, OwnerShipTestMixin, View):
    permission_required = ("sales.can_validate_quote")
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

class QuoteDraftenView(LoginRequiredMixin, PermissionRequiredMixin, OwnerShipTestMixin, View):

    permission_required = ("sales.can_draften_quote")

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

class ProductsView(ListView, UserPassesTestMixin):
    template_name = "products.html"
    model = Product
    paginate_by = 30
    paginator_class = MyPaginator

    def test_func(self) -> bool | None:
        return self.request.user.is_superuser


class CompaniesView(ListView):
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

class CompanyAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        # if not self.request.user.is_authenticated:
        #     return Company.objects.none()
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

class QuotesFilterView(LoginRequiredMixin, PermissionRequiredMixin, FilterView):

    template_name = 'allquotes.html'
    filterset_class = FilterQuotes
    context_object_name = 'object_list'
    permission_required = ("sales.view_quoterequest")
    paginate_by = 10
    paginator_class = MyPaginator

    def get_queryset(self):
        user = self.request.user
        query = QuoteRequest.objects.order_by("-id")
        if not user.sysRole == "sman" or user.is_superuser:
            return query.filter()
        else:
            return query.filter(user = self.request.user)
    def get(self, request, *args, **kwargs):
        try:
            self.paginate_by = request.GET["paginate"]
        except:
            self.paginate_by = 10
        self.extra_context = {"pages":self.paginate_by}
        return super().get(request, *args, **kwargs)

    def get_filterset_class(self):
        user = self.request.user
        if not user.sysRole == "sman" or user.is_superuser:
            return SuperFilterQuotes
        else:
            return FilterQuotes

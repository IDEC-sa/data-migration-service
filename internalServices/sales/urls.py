from django.urls import path
from .views import excelUploader, QuoteDraftenView, QuoteValidateView, staticDataView, DashboardView, ReviewProducts, CreateProducts, QuoteUpdateView, AllQuotesView, InProcessQuotesView, QuoteDetailView, DraftQuotesView
urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="sales-dashboard"), 
    path("quotes/upload/", excelUploader.as_view(), name = "uploader"),
    path("quotes/<int:quoteId>/review/", ReviewProducts.as_view(), name="reviewquote"),
    path("quotes/<int:quoteId>/create-products/", CreateProducts.as_view(), name="createprods"),
    path("quotes/<int:quoteId>/add-static/", staticDataView.as_view(), name="add-static"),
    path("quotes/all/", AllQuotesView.as_view(), name="all-quotes"),
    path("quotes/validated/", InProcessQuotesView.as_view(), name="in-process-quotes"),
    path("quotes/drafts/", DraftQuotesView.as_view(), name="draft-quotes"),
    path("quotes/<int:pk>/", QuoteDetailView.as_view(), name="detail-quote"),
    path("quotes/<int:pk>/update", QuoteUpdateView.as_view(), name="update-quote"),
    path("quotes/<int:pk>/validate", QuoteValidateView.as_view(), name="validate-quote"),
    path("quotes/<int:pk>/draften", QuoteDraftenView.as_view(), name="draften-quote")
]

from collections.abc import Callable
from typing import Any
from django.contrib.auth.mixins import UserPassesTestMixin,  AccessMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404

class SalesManPermissionMixin(UserPassesTestMixin):
    def test_func(self) -> bool | None:
        print("sdasdas")
        return self.request.user.sysRole == "sman" or self.request.user.is_superuser

# class OwnershipMixin(AccessMixin):

#     ownedClass = object
#     key = ""

#     def dispatch(self, request, *args, **kwargs):
#         obj = get_object_or_404(self.ownedClass, pk=self.kwargs[self.key])
#         print(request.user.is_superuser)
#         if not request.user == obj.user and (not request.user.is_superuser and not request.user.state == "sdir"):
#             return self.handle_no_permission()
#         return super().dispatch(request, *args, **kwargs)

class OwnerPermissionMixin(PermissionRequiredMixin):
    def has_permission(self) -> bool:
       boolll = self.get_object().user == self.request.user
       return boolll

class SuperUserPermissionMixin(PermissionRequiredMixin):
    def has_permission(self) -> bool:
       boolll = self.request.user.is_superuser
       return boolll

class SalesDirectoryPermissionMixin(PermissionRequiredMixin):
    def has_permission(self) -> bool:
       boolll = self.request.user.sysRole == "sdir"
       print(boolll)
       return boolll


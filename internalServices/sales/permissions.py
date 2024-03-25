from collections.abc import Callable
from typing import Any
from django.contrib.auth.mixins import UserPassesTestMixin,  AccessMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404

class SalesManPermissionMixin(UserPassesTestMixin):
    def test_func(self) -> bool | None:
        return self.request.user.sysRole == "sman"

class OwnershipMixin(AccessMixin):

    ownedClass = object
    key = ""

    def dispatch(self, request, *args, **kwargs):
        obj = get_object_or_404(self.ownedClass, pk=self.kwargs[self.key])
        print(self.request.user == obj.user)
        print("ownership verification")

        if not request.user == obj.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

class OwnerPermissionMixin(PermissionRequiredMixin):
    def has_permission(self) -> bool:
       boolll = self.get_object().user == self.request.user
       return boolll

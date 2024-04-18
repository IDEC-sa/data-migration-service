from .models import Action, QuoteRequest

def userLoginAction(user):
    act = Action(actor=user, type="logi")
    act.save()


def userLogoutAction(user):
    act = Action(actor=user, type="logo")
    act.save()


def addQuoteAction(user, quote):
    act = Action(actor=user, quote=quote, type="cre")
    act.save()


def handleQuotesAction(user):
    act = Action(actor=user, type="srch")
    act.save()

def viewQuoteAction(user, quote):
    act = Action(actor=user, quote=quote, type="vis")
    act.save()


def editQuoteAction(user, quote):
    act = Action(actor=user, quote=quote, type="edit")
    act.save()

def validateQuoteAction(user, quote):
    act = Action(actor=user, quote=quote, type="val")
    act.save()

def reviewQuoteAction(user, quote):
    act = Action(actor=user, quote=quote, type="rev")
    act.save()
def draftenQuoteAction(user, quote):
    act = Action(actor=user, quote=quote, type="dra")
    act.save()

def addStaticAction(user, quote):
    act = Action(actor=user, quote=quote, type="adds")
    act.save()


##not yet ued
def approveQuoteAction(user, quote):
    act = Action(actor=user, quote=quote, type="app")
    act.save()
##not yet used
def desapproveQutoeAction(user, quote):
    act = Action(actor=user, quote=quote, type="napp")
    act.save()

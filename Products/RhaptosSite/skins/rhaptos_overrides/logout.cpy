## Controller Python Script "logout"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=Logout handler
##parameters=

# Rhaptos notes:
#  redirect to REQUEST.URL1 to return to where we came from
#  add portal status message
#  use RESPONSE.redirect instead of FormController next_action because it duplicates :list for some reason

from Products.CMFCore.utils import getToolByName

try:
    context.acl_users.logout(context.REQUEST)
except:
    pass  # XXX we expect Unauthorized, but why do we do a bare except then?

REQUEST = context.REQUEST
util = context.plone_utils
skinvar = context.portal_skins.getRequestVarname()
path = '/' + context.absolute_url(1)

if REQUEST.has_key(skinvar) and not context.portal_skins.getCookiePersistence():
    REQUEST.RESPONSE.expireCookie(skinvar, path=path)

# Invalidate existing sessions, but only if they exist.
sdm = getToolByName(context, 'session_data_manager', None)
if sdm is not None:
    session = sdm.getSessionData(create=0)
    if session is not None:
        session.invalidate()

from Products.CMFPlone import transaction_note
transaction_note('Logged out')

#target_url = REQUEST.URL1
target_url = REQUEST.HTTP_REFERER

from Products.RhaptosSite import RhaptosMessageFactory as rMsgFactory
portal = context.portal_url.getPortalObject()
util.addPortalMessage(rMsgFactory("message_logged_out",
                             default=u'You are now logged out.',
                             mapping={"portal_title":portal.Title()}))

# Double '$' to avoid injection into TALES
target_url = target_url.replace('$','$$')
#target_url += '/logged_out'
#return state.set(next_action='redirect_to:string:' + target_url )
return REQUEST.RESPONSE.redirect(target_url)

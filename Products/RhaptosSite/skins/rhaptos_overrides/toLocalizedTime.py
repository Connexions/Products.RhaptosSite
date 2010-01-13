## Script (Python) "toLocalizedTime"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=time=None, long_format=None
##title=
##
# The time parameter must be either a string that is suitable for
# initializing a DateTime or a DateTime object.
# Returns a localized string.

## Rhaptos note: customized solely to remove ridiculously repeated deprecation warning
#context.plone_log("The toLocalizedTime script is deprecated and will be "
#                  "removed in plone 3.5.  Use the method of the @@plone view,"
#                  " or the method in the main_template globals.")

return context.restrictedTraverse('@@plone').toLocalizedTime(time, long_format)

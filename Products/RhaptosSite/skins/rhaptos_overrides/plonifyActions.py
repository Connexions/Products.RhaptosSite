## Script (Python) "plonifyActions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template_id, actions=None, default_tab='view'
##

## Rhaptos Note:
## Overridden to make collection composer work.  The normal Plone
## script denotes a tab as selected if it has the same method name
## (the template id in most cases)  In collection composer, the
## pane on the right has several actions that have the same template,
## just different parameters for the template.  This was causing both
## to be highlighted.

from urllib import unquote
here_url = context.absolute_url()
site_properties=context.portal_properties.site_properties

if actions is None:
    actions=context.portal_actions.listFilteredActionsFor()

actionlist=[]
if same_type(actions, {}):
    if context.getTypeInfo().getId() in site_properties.use_folder_tabs:
        actionlist=actions['folder']+actions['object']+actions.get('object_tabs',[])
    else:
        actionlist=actions['object']+actions.get('object_tabs',[])

plone_actions=[]
use_default=1

request_url = context.REQUEST['ACTUAL_URL']
request_url_path = request_url[len(here_url):]
if request_url_path.startswith('/'):
    request_url_path = request_url_path[1:]

for action in actionlist:
    item={'title':'',
          'id':'',
          'url':'',
          'selected':''}

    item['title']=action['title']
    item['id']=actionid=action['id']

    aurl=action['url'].strip()
    if not (aurl.startswith('http') or aurl.startswith('javascript')):
        item['url']='%s/%s'%(here_url,aurl)
    else:
        item['url']=aurl

    action_method=item['url'].split('/')[-1]

    # Action method may be a method alias: Attempt to resolve to a template.
    try:
        action_method=context.getTypeInfo().queryMethodID(action_method,
                                                          default = action_method)
    except AttributeError:
        # Don't raise if we don't have a CMF 1.5 FTI
        pass

    # we unquote since view names sometimes get escaped
    request_action = unquote( request_url_path )
    try:
        request_action=context.getTypeInfo().queryMethodID(request_action,
                                                           default = request_action)
    except AttributeError:
        # Don't raise if we don't have a CMF 1.5 FTI
        pass
    
    if action_method==template_id:  # Rhaptos patch here: removed "or action_method == request_action:"
        item['selected']=1
        use_default=0

    plone_actions.append(item)

if use_default:
    for action in plone_actions:
        if action['id']==default_tab:
            action['selected']=1
            break

return plone_actions

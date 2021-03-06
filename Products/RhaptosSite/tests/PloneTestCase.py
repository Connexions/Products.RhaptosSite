#
# PloneTestCase
#

# $Id: PloneTestCase.py 5600 2004-09-09 15:45:09Z shh42 $

from Testing import ZopeTestCase
import transaction

ZopeTestCase.installProduct('CMFCore')
ZopeTestCase.installProduct('CMFDefault')
ZopeTestCase.installProduct('CMFCalendar')
ZopeTestCase.installProduct('CMFTopic')
ZopeTestCase.installProduct('DCWorkflow')
ZopeTestCase.installProduct('CMFActionIcons')
ZopeTestCase.installProduct('CMFQuickInstallerTool')
ZopeTestCase.installProduct('CMFFormController')
ZopeTestCase.installProduct('GroupUserFolder')
ZopeTestCase.installProduct('ZCTextIndex')
ZopeTestCase.installProduct('CMFPlone')
ZopeTestCase.installProduct('MailHost', quiet=1)
ZopeTestCase.installProduct('PageTemplates', quiet=1)
ZopeTestCase.installProduct('PythonScripts', quiet=1)
ZopeTestCase.installProduct('ExternalMethod', quiet=1)

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Acquisition import aq_base
import time
import types

portal_name = 'portal'
portal_owner = 'portal_owner'
default_user = ZopeTestCase.user_name


class PloneTestCase(ZopeTestCase.PortalTestCase):
    '''TestCase for Plone testing'''

    def getPortal(self):
        '''Returns the portal object to the bootstrap code.
           DO NOT CALL THIS METHOD! Use the self.portal 
           attribute to access the portal object from tests.
        '''
        return self.app[portal_name]

    def createMemberarea(self, member_id):
        '''Creates a minimal, no-nonsense memberarea.'''
        membership = self.portal.portal_membership
        # Owner
        uf = self.portal.acl_users
        user = uf.getUserById(member_id)
        if user is None:
            raise ValueError, 'Member %s does not exist' % member_id
        user = user.__of__(uf)
        # Home folder may already exist (see below)
        members = membership.getMembersFolder()
        if not hasattr(aq_base(members), member_id):
            _setupHomeFolder(self.portal, member_id)
        # Take ownership of home folder
        home = membership.getHomeFolder(member_id)
        home.changeOwnership(user)
        home.__ac_local_roles__ = None
        home.manage_setLocalRoles(member_id, ['Owner'])
        # Take ownership of personal folder
        personal = membership.getPersonalFolder(member_id)
        personal.changeOwnership(user)
        personal.__ac_local_roles__ = None
        personal.manage_setLocalRoles(member_id, ['Owner'])

    def setGroups(self, groups, name=default_user):
        '''Changes the specified user's groups. Assumes GRUF.'''
        self.assertEqual(type(groups), types.ListType)
        uf = self.portal.acl_users
        uf._updateUser(name, groups=groups, domains=[])
        if name == getSecurityManager().getUser().getId():
            self.login(name)

    def loginPortalOwner(self):
        '''Use if you need to manipulate the portal itself.'''
        uf = self.app.acl_users
        user = uf.getUserById(portal_owner).__of__(uf)
        newSecurityManager(None, user)


class FunctionalTestCase(ZopeTestCase.Functional, PloneTestCase):
    '''Convenience class for functional unit testing'''


def setupPloneSite(app=None, id=portal_name, quiet=0, with_default_memberarea=1):
    '''Creates a Plone site.'''
    if not hasattr(aq_base(app), id):
        _start = time.time()
        if not quiet: ZopeTestCase._print('Adding Plone Site ... ')
        # Add user and log in
        app.acl_users._doAddUser(portal_owner, '', ['Manager'], [])
        user = app.acl_users.getUserById(portal_owner).__of__(app.acl_users)
        newSecurityManager(None, user)
        # Add Plone Site
        factory = app.manage_addProduct['CMFPlone']
        factory.manage_addSite(id, '', create_userfolder=1)
        # Precreate default memberarea for performance reasons
        if with_default_memberarea:
            _setupHomeFolder(app[id], default_user)
        # Log out
        noSecurityManager()
        transaction.commit()
        if not quiet: ZopeTestCase._print('done (%.3fs)\n' % (time.time()-_start,))


def _setupHomeFolder(portal, member_id):
    '''Creates the folders comprising a memberarea.'''
    from Products.CMFPlone.PloneUtilities import _createObjectByType
    membership = portal.portal_membership
    catalog = portal.portal_catalog
    # Create home folder
    members = membership.getMembersFolder()
    _createObjectByType('Folder', members, id=member_id)
    # Create personal folder
    home = membership.getHomeFolder(member_id)
    _createObjectByType('Folder', home, id=membership.personal_id)
    # Uncatalog personal folder
    personal = membership.getPersonalFolder(member_id)
    catalog.unindexObject(personal)


def optimize():
    '''Significantly reduces portal creation time.'''
    # Don't compile expressions on creation
    def __init__(self, text):
        self.text = text
    from Products.CMFCore.Expression import Expression
    Expression.__init__ = __init__
    # Don't clone actions but convert to list only
    def _cloneActions(self):
        return list(self._actions)
    from Products.CMFCore.ActionProviderBase import ActionProviderBase
    ActionProviderBase._cloneActions = _cloneActions
    # Don't setup default directory views
    def setupDefaultSkins(self, p):
        from Products.CMFCore.utils import getToolByName
        ps = getToolByName(p, 'portal_skins')
        ps.manage_addFolder(id='custom')
        ps.addSkinSelection('Basic', 'custom')
    """
    #from Products.CMFPlone.Portal import PloneGenerator
    from Products.CMFPlone.setuphandlers import PloneGenerator
    PloneGenerator.setupDefaultSkins = setupDefaultSkins
    # Don't setup default Members folder
    def setupMembersFolder(self, p):
        pass
    PloneGenerator.setupMembersFolder = setupMembersFolder
    # Don't setup Plone content (besides Members folder)
    def setupPortalContent(self, p):
        p.invokeFactory('Large Plone Folder', id='Members')
        p.portal_catalog.unindexObject(p.Members)
    PloneGenerator.setupPortalContent = setupPortalContent
    """


optimize()


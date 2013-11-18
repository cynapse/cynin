###############################################################################
#cyn.in is an open source Collaborative Knowledge Management Appliance that 
#enables teams to seamlessly work together on files, documents and content in 
#a secure central environment.
#
#cyn.in v2 an open source appliance is distributed under the GPL v3 license 
#along with commercial support options.
#
#cyn.in is a Cynapse Invention.
#
#Copyright (C) 2008 Cynapse India Pvt. Ltd.
#
#This program is free software: you can redistribute it and/or modify it under
#the terms of the GNU General Public License as published by the Free Software 
#Foundation, either version 3 of the License, or any later version and observe 
#the Additional Terms applicable to this program and must display appropriate 
#legal notices. In accordance with Section 7(b) of the GNU General Public 
#License version 3, these Appropriate Legal Notices must retain the display of 
#the "Powered by cyn.in" AND "A Cynapse Invention" logos. You should have 
#received a copy of the detailed Additional Terms License with this program.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of 
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General 
#Public License for more details.
#
#You should have received a copy of the GNU General Public License along with 
#this program.  If not, see <http://www.gnu.org/licenses/>.
#
#You can contact Cynapse at support@cynapse.com with any problems with cyn.in. 
#For any queries regarding the licensing, please send your mails to 
# legal@cynapse.com
#
#You can also contact Cynapse at:
#802, Building No. 1,
#Dheeraj Sagar, Malad(W)
#Mumbai-400064, India
###############################################################################
from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ubify.policy import CyninMessageFactory as _

class ISpaceMembersPortlet(IPortletDataProvider):

    displaytitle = schema.TextLine(title=_(u'Title'),required=False)
    
    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=5)
    role = schema.Choice(title=_(u"Select Role"),
                               description=_(u"Choose a role of members to be displayed for this Space"),
                               vocabulary="ubify.cyninv2theme.portlets.ListRoles")
    
class Assignment(base.Assignment):
    implements(ISpaceMembersPortlet)

    def __init__(self, count=5, role='Member',displaytitle=''):
        self.count = count
        self.resultcount = 0
        self.role = role
        self.displaytitle = displaytitle
        

    @property
    def title(self):
        return _(u"Space Members in role " + self.role)

#def _render_cachekey(fun, self):
#    if self.anonymous:
#        raise ram.DontCache()
#    return render_cachekey(fun, self)

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('spacemembersportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.typesToShow = 'Document'

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        
        self.moreurl = self.portal_url + "/".join(context.getPhysicalPath()) + "/@@spacemembers?membertype=" + self.data.role
        
    #@ram.cache(_render_cachekey)
    #def render(self):    
    #    return xhtml_compress(self._template())

    @property
    def available(self):        
        return not self.anonymous and len(self._data())

    def results(self):
        limit = self.data.count
        return self._data()[:limit]
    
    def portlettitle(self):
        from vocabularies import roleslist        
        roleTitle = self.data.displaytitle
        found = False
        
        if roleTitle is None:
            roleTitle = ""
        if roleTitle == "":
            for r in roleslist:
                if r['id'].lower() == self.data.role.lower():
                    roleTitle = r['name'] + "s"
                    found = True
                if found == True:
                    break
        
        return roleTitle
            
    def generate_dict_list(self,listObjects,context):
        user_role_map = []
        
        for user in listObjects:
            
            roleslist = context.get_local_roles_for_userid(user)
            if len(roleslist) > 0:
                user_role_map.append(dict(useritem = user,roles = roleslist ))    
            else:
                roles_groupslist = []
                aclusers = context.portal_membership.acl_users
                objUser = aclusers.getUserById(user)
                listGroups = objUser.getGroups()
                for gr in listGroups:
                    templist = context.get_local_roles_for_userid(gr)
                    for lst in templist:
                        if lst not in roleslist:
                            roles_groupslist.append(lst)                            
                roles_groupslist.sort()
                user_role_map.append(dict(useritem = user,roles = roles_groupslist ))
            
        return user_role_map
    
    def checkIfGroupGetUsers(self,listobjects,context):
        listdummy = []
        pm = context.portal_membership
        aclusers = pm.acl_users
        
        for obj in listobjects:
            if aclusers.getUserById(obj) is None:
                #user doesn't exists with name search in group
                objGroup = aclusers.getGroupById(obj)
                if objGroup <> None:
                    listtemp = objGroup.listAssignedPrincipals(obj)
                    for tempobj in listtemp:
                        if len(tempobj) > 0 and aclusers.getUserById(tempobj[0]):
                            listdummy.append(tempobj[0])
            else:
                listdummy.append(obj)
        
        return listdummy
        
    def resultscount(self):
        return self.data.resultscount - self.data.count
    
    def concatroles(self,roleslist):
        
        strVal = ""
        for obrole in roleslist:
            strVal = strVal + obrole + ', '
        strVal = str(strVal)    
        strVal = strVal.rstrip(', ')
        return strVal   
    
    @memoize
    def _data(self):
        context = aq_inner(self.context)
        
        objresults = []
        role_to_search = self.data.role
        
        listReaders = context.users_with_local_role('Reader')
        listReaders = self.checkIfGroupGetUsers(listReaders,context)
        
        listContributors = context.users_with_local_role('Contributor')
        listContributors = self.checkIfGroupGetUsers(listContributors,context)
        
        listReviewers = context.users_with_local_role('Reviewer')
        listReviewers = self.checkIfGroupGetUsers(listReviewers,context)

        listEditors = context.users_with_local_role('Editor')
        listEditors = self.checkIfGroupGetUsers(listEditors,context)

        if role_to_search == 'Reader':
            for user in listReaders:
                if user not in listContributors and user not in listReviewers and user not in listEditors:
                    objresults.append(user)
        elif role_to_search == 'Contributor':
            for user in listContributors:
                if user not in listReviewers and user not in listEditors:
                    objresults.append(user)
        elif role_to_search == 'Reviewer':
            for user in listReviewers:
                if user not in listEditors:
                    objresults.append(user)
        elif role_to_search == 'Editor':
            objresults = listEditors
        else:   #Special case when all members will be listed priority given to managers
            listmembers = []
            listtemp = []
            
            for userEditor in listEditors:
                listtemp.append(userEditor)
                listtemp.sort()
            for userReviewer in listReviewers:
                if userReviewer not in listmembers and userReviewer not in listtemp:
                    listmembers.append(userReviewer)
            for userContributor in listContributors:
                if userContributor not in listmembers and userContributor not in listtemp:
                    listmembers.append(userContributor)
            for userReader in listReaders:
                if userReader not in listmembers and userReader not in listtemp:
                    listmembers.append(userReader)
                    
            listmembers.sort()
            listtemp.extend(listmembers)
            objresults.extend(listtemp)
            
            self.data.resultscount = len(objresults)
            return self.generate_dict_list(objresults,context)
        
        objresults.sort()
        self.data.resultscount = len(objresults)
        return self.generate_dict_list(objresults,context)


class AddForm(base.AddForm):
    form_fields = form.Fields(ISpaceMembersPortlet)
    label = _(u"Add Space Members Portlet")
    description = _(u"This portlet displays members for current space.")

    def create(self, data):
        return Assignment(count=data.get('count', 5),role=data.get('role','Reader'))

class EditForm(base.EditForm):
    form_fields = form.Fields(ISpaceMembersPortlet)
    label = _(u"Edit Space Members Portlet")
    description = _(u"This portlet displays members for current space.")
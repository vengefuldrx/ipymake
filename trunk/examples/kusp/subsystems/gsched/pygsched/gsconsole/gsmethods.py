"""
:mod:`gsmethods` -- Action Methods for the Group Scheduling Shell
===========================================================================

.. moduleauthor:: Dillon Hicks <hhicks@ittc.ku.edu>

Summary
-----------

`gsmethods` Public "Command" or "Action" Methods 
        
These are callable by the user by typing their name in the gsconsole,
and sending a list of space seperated arguements. The help text for
each method is generated by its docstring.
"""
import sys
import os
import signal 
import string
from pygsched.gshierarchy import GSGroup, GSThread, GSHierarchy
import pygsched.gsprocutils as gsproc
import pykusp.configutility as config
import pygsched.gssession as session


# This isn't used currently, but here as a reference and for furture
# use.
SYSTEM_GROUP = 'gsched_top_seq_group'

def create_group(self, group=None, member_name=None, schedule=None,  *args):
    """Creates a new uninstalled group within group scheduling.
    
    usage: create_group <group-name> <member-name> <schedule-name>
    
    Note: Extra arguments to create group are ignored.
    """
    
    # Check if the group and schedule are specified, print error
    # messages and return from the method if they are not since
    # group creation will fail.
    if group is None:
        self.write("Error: No Group specified to create!\n")
        self.help("create_group")
        return 
    
    if schedule is None:
        self.write("Error: No schedule specified for Group %s\n" % group)
        self.help("create_group")
        return 
    
    if len(args) > 0:
        # There were extra arguments given, so just ignore them
        # for now.
        self.write("Warning: Ignoring extra arguments to create_group: \n")
        for arg in args: self.write("%s\n" % arg)
        self.write("\n")
        
        
    # Attempt to create the group and store the return value of the 
    # group retrieved by the GSSession backend.
    retval = self.gsched_session.create_group(group, schedule)
        
    if retval == 0:
        # Great, group creation was successful
        self.write("Created Group %s with schedule %s.\n" % (group, schedule))
    else:
        # No there was an error, tell the user that group creation
        # failed and give the error code which is designated by
        # the return value.
        self.write("Error: Unable to create Group"
                   " %s with schedule %s (Error Code %i).\n" % (group, schedule, retval))


def add_thread(self, group=None, thread=None, exclusive=1, *args):
    """Registers a CCSM named member task join a Group.
    
    usage: add_thread <group-name> <thread-name> <exlusivity>
    """
    if group is None:
        self.write("Error: No parent Group specified!\n")
        self.help("add_thread")
        return 

    if thread is None:
        self.write("Error: No thread specified to add to `%s'\n" % group)
        self.help("add_thread")
        return 

    if type(exclusive) is str:
        if exclusive.isalnum():
            exclusive = int(exclusive)
        else:
            self.write("Error: exclusive is not number.\n")
            self.help("add_thread")
            return 

    else:
        if not type(exclusive) is int:
            self.write("Error: exclusive is not number.\n")
            self.help("add_thread")
            return
    
    if exclusive < 0 or exclusive > 1:
        self.write("Error: exclusive is not a proper value %i "
                   "needs to be (0 or 1).\n")
        self.help("add_thread")
        return 
            

    if len(args) > 0:
        # There were extra arguments given, so just ignore them
        # for now.
        self.write("Warning: Ignoring extra arguments"
                   " to add_thread: \n")
        for arg in args: self.write("%s\n" % arg)
        self.write("\n")
    
    self.gsched_session.add_thread_to_group(group, thread, exlusive)


def add_group(self, group=None, member_group=None, *args):
    """Registers a CCSM named Group to join another Group.
    
    usage: add_group_by_name <group-name> <group-to-add-name>
    """
    if group is None:
        self.write("Error: No parent Group specified!\n")
        self.help("add_group_by_name")
        return 
    
    if member_group is None:
        self.write("Error: No member Group specified to add to `%s'\n" % group)
        self.help("add_group_by_name")
        return 
    
    if len(args) > 0:
        # There were extra arguments given, so just ignore them
        # for now.
        self.write("Warning: Ignoring extra arguments to add_group: \n")
        for arg in args: self.write("%s\n" % arg)
        self.write("\n")


    # Attempt to create the group and store the return value of the 
    # group retrieved by the GSSession backend.
    retval = self.gsched_session.add_group_to_group(group, member_group)
    
    if retval == 0:
        # Great, group creation was successful
        self.write("Registered Group `%s' as a member of Group `%s'.\n" % (member_group, group))
    else:
        # No there was an error, tell the user that group creation
        # failed and give the error code which is designated by
        # the return value.
        self.write("Error: Unable to register Group "
                   " `%s' as a member of Group `%s' "
                   "(Error Code %i).\n" % (member_group, group, retval))

        


def leave_group(self, group=None, member_group=None, *args):
    """Have a member Group leave another Group.
    
    usage: leave_group <group-name> <group-to-add-name>
    
    Differs from uninstall_group in that fact that uninstall_group
    must be used to remove a group from the system hierarchy. 
    Otherwise, you must use leave_group.
    """
    if group is None:
        self.write("Error: No parent Group specified!\n")
        self.help("leave_group")
        return 
    
    if member_group is None:
        self.write("Error: No member Group specified to add to `%s'\n" % group)
        self.help("add_group_by_name")
        return 
    
    if len(args) > 0:
        # There were extra arguments given, so just ignore them
        # for now.
        self.write("Warning: Ignoring extra arguments to create_group: \n")
        for arg in args: self.write("%s\n" % arg)
        self.write("\n")

    self.gsched_session.remove_group_from_group(group, member_group)
    
    

def set_exclusive(self, pid=None, *args):
    """Set a thread with some pid to have exclusive control.
    
    usage: set_exclusive <thread-pid>
    """
    self.gsched_session.thread_set_exclusive(pid)
    
def clear_exclusive(self, *args):
    """Clear the exclusive control attribute of a thread with some pid.
    
    usage: clear_exclusive <thread-pid>
    """
    self.gsched_session.thread_clear_exclusive(pid)
    pass
        

def group_info(self, *args):
    """Prints the SDF and members for a given group.
    
    usage: group_info <group-name>
        
    The format of the information for each group is in the form:
        
    group_name (SDF)
    (T) - member_thread0 (PID)
    (T) - member_thread1 (PID)
    (G) - member_group (SDF)
    """
    if len(args) == 0:
        # No groups, stop action
        self.write("\nNo group specified.\n")
        return
    elif len(args) > 1:
        # More than one group specified, we think, so call group
        # info individually for each group.
        for grp in args: 
            self.group_info(grp)
        return

    # There should only be one element in args, the name of the
    # group about which the user wants info.
    group_name = args[0]
    group = self.find_group(group_name)
    if group is None:
        # Apparently the group doesn't exist in the hierarchy.
        self.write("Error: Unable to display information "\
                       "for unknown Group `%s'\n" % group_name)
        return
        
    self.write("\n")
    # Print out the string representation of the group
    # (i.e. <group-name> (<sdf>))
    self.write(str(group)+'\n')

    members = group.get_members()
    
    # We want to give seperate representations to each of member
    # types (group and thread) so make two sublists from the
    # members list segregated by member type.
    mem_threads = filter(lambda member: isinstance(member, GSThread),
                         members)
    mem_groups = filter(lambda member: isinstance(member, GSGroup),
                        members)

        
    for mem_group in mem_groups:
        # Print each member group with 4 spaces of padding, for
        # clarity.
        thread_string = "    (G) - %s\n" % str(mem_group)
        self.write(thread_string)


    for mem_thread in mem_threads:
        # Print each member thread with 4 spaces of padding, for
        # clarity.
        thread_string = "    (T) - %s\n" % str(mem_thread)
        self.write(thread_string)

    self.write('\n')

def print_groups(self, *args):
    """Print all of the groups on the system.
    
    usage: print_groups
    
    Displays all of the Groups that are currently managed by Group
    Scheduling. Groups that are still in Group Scheduling but are
    not installed are currently refered to as `empty groups' and
    are not part of the system Hierarchy. So there are two
    different lists outputted by print_groups:
    
    Groups in the main hierarchy [ name (sdf) ]:
    > group_0 (some_sdf)
    > group_1 (another_sdf)
    ...
    
    Empty or unattached Groups [ name (sdf) ]:
    > unattached_group_0 (some_sdf)
    > unattached_group_1 (another_sdf)
    ...

    Note that, this method will not print out the essential Group
    Scheduling root Group `gsched_top_seq_group' since it is not
    editable.
    """
    gsh = gsproc.parse()
    groups = filter( lambda member: isinstance(member, GSGroup),
                     gsh.get_all_members())

    self.write('\n')
    self.write("Groups in the main hierarchy [ name (sdf) ]:\n")
    if len(groups) > 0:
        for group in groups: self.write("> %s\n" % str(group))
    else:
        self.write("None\n")
      
    groups = gsh.get_empty_groups()
    self.write("\nEmtpy or unattached Groups [ name (sdf) ]:\n")
    if len(groups) > 0:
        for group in groups: self.write("> %s\n" % str(group))
    else:
        self.write("None\n")
        
    self.write('\n')

def cleanup_groups(self, *args):
    """Destroyes all uninstalled Groups and empty (memberless) Groups.
    
    usage: cleanup_groups
    """
    gsh = gsproc.parse()
        

    self.write("Removing groups:\n")
    for group in gsh.get_empty_groups():
        self.write("%s\n" % str(group))
        self.gsched_session.destroy_group(group.get_name())
    
    for member in gsh.get_all_members():
        if isinstance(member, GSGroup):
            if len(member.get_members()) == 0:
                group_name = member.get_name()
                self.write("%s\n" % str(member))
                self.remove_group(group_name)

def remove_group(self, *args):
    """Recursively uninstall and destroy the Group and its members.
    
    usage: remove_group <group-name>
    """
    if len(args) == 0:
        self.write( "Warning: You did not specify a group to remove\n")
        self.help(["remove_group"])
        return

    if len(args) > 1:
        for grp in args: self.remove_group(grp)
        return
    
    group_name = args[0]
    group = self.find_group(group_name)
    if group is None:
        group = self.find_empty_group(group_name)
        if group is None:
            self.write( "Warning: Cannot find Group `%s' "
                        "in Group Scheduling.\n" % group_name)
            return

    self.remove_group_R(group)
            

def uninstall_group(self, *args):
    """Uninstalls a Group from Group Scheduling.
    
    usage: uninstall_group <group-name>
    
    Note: Uninstalling a group one of the prerequisites before
    destroying a group.
    """
    if len(args) == 0:
        # User didnt specify a group to remove, tell them there
        # error and stop this method.
        self.write( "Warning: You did not specify a group to uninstall\n")
        self.help("uninstall_group")
        return
    if len(args) > 1:
        for grp in args: self.uninstall_group(grp)
        return

    group_name = args[0]
    group = self.find_group(group_name)
    if group is None:
        self.write( "Warning: Cannot uninstall non-existent Group: %s\n" % group_name)
            
    self.gsched_session.uninstall_group(group)

    
def destroy_group(self, *args):
    """Destroys the Group Struct of the Group.
        
    usage: destroy_group <group-name>
    
    Uses the GSSession backend to destroy a Group <group-name>. To
    be destroyed the group must first be uninstalled from Group
    Scheduling and have no members. If both of the previous
    conditions are not met, then removing the Group will fail.
    """

    if len(args) == 0:
        # No group specified to destroy, print the warning, and
        # the help about destroy_group.
        self.write( "Warning: You did not specify a group to destroy\n")
        self.help("destroy_group")
        return
    if len(args) > 1:
        # Assume that if there are multiple arguments, that they
        # are all groups to be destroyed, so call the destroy_group 
        # with each group individually.
        for grp in args: self.destroy_group(grp)
        return
            
    # len(args) should only be 1 after the previous two if
    # statments are not entered, and that element is the name of
    # the group to destroy.
    group_name = args[0]
    group = self.find_group(group_name)
    if group is None:
        # The group was not found in the main hierarchy, so check
        # the 'empty groups'.
        group = self.find_empty_group(group_name)
        if group is None:
            # The group was not found in the empty_groups so it
            # doesnt exists, quit this action.
            self.write("Error: Unable to destroy unknown Group `%s'\n" % group_name)
            return 

    # Attempt to destroy the group
    retval = self.gsched_session.destroy_group(group)

    if retval == 0:
        self.write("Destroyed %s successfully\n" % group)
    else:
        self.write("Unable to destroy %s (Error Code %i)\n" % (group, retval))


def load_configfile(self, *args):
    """Loads a Group Scheduling Configuration file into group scheduling.
    """
    if len(args) == 0:
        return
    if len(args) > 1:
        return
    
    inputfile = args[0]
    gsh_config_dict = config.parse_configfile(inputfile)
    gsh = GSHierarchy(gsh_config_dict)
    session.load_hierarchy(gsh)
    
def print_system(self, *args):
    """Prints the whole system hierarchy (all installed Groups and \
thier members) in a tree format.
        """
    gsh = gsproc.parse()
    self.write(str(gsh))

def install_group(self, group_name=None, *args):
    """Installs a Group to the root system group (gsched_top_seq_group).
    
    usage: install_group <group-name>

    The group must be unattached (parentless).
    """
    group = self.find_empty_group(group_name)
    if group is None:
        # The group was not found in the empty_groups so it
        # doesnt exists, quit this action.
        self.write("Error: Unable to install unknown Group `%s'\n" % group_name)
        return 
    
    self.gsched_session.install_group(group)

    ########### END PUBLIC COMMAND METHODS ##########

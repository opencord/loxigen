# Copyright 2013, Big Switch Networks, Inc.
#
# LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
# the following special exception:
#
# LOXI Exception
#
# As a special exception to the terms of the EPL, you may distribute libraries
# generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
# that copyright and licensing notices generated by LoxiGen are not altered or removed
# from the LoxiGen Libraries and the notice provided below is (i) included in
# the LoxiGen Libraries, if distributed in source code form and (ii) included in any
# documentation for the LoxiGen Libraries, if distributed in binary form.
#
# Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
#
# You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
# a copy of the EPL at:
#
# http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# EPL for the specific language governing permissions and limitations
# under the EPL.

"""
@brief Utilities involving LOXI naming conventions

Utility functions for OpenFlow class generation

These may need to be sorted out into language specific functions
"""

import sys
import c_gen.of_g_legacy as of_g
import tenjin
from generic_utils import find, memoize

def class_signature(members):
    """
    Generate a signature string for a class in canonical form

    @param cls The class whose signature is to be generated
    """
    return ";".join([",".join([x["m_type"], x["name"], str(x["offset"])])
                     for x in members])

def type_dec_to_count_base(m_type):
    """
    Resolve a type declaration like uint8_t[4] to a count (4) and base_type
    (uint8_t)

    @param m_type The string type declaration to process
    """
    count = 1
    chk_ar = m_type.split('[')
    if len(chk_ar) > 1:
        count_str = chk_ar[1].split(']')[0]
        if count_str in of_g.ofp_constants:
            count = of_g.ofp_constants[count_str]
        else:
            count = int(count_str)
        base_type = chk_ar[0]
    else:
        base_type = m_type
    return count, base_type

##
# Class types:
#
# Virtual
#    A virtual class is one which does not have an explicit wire
#    representation.  For example, an inheritance super class
#    or a list type.
#
# List
#    A list of objects of some other type
#
# TLV16
#    The wire represenation starts with 16-bit type and length fields
#
# OXM
#    An extensible match object
#
# Message
#    A top level OpenFlow message
#
#

def class_is_message(cls):
    """
    Return True if cls is a message object based on info in unified
    """
    return "xid" in of_g.unified[cls]["union"] and cls != "of_header"

def class_is_tlv16(cls):
    """
    Return True if cls_name is an object which uses uint16 for type and length
    """
    if cls.find("of_action") == 0: # Includes of_action_id classes
        return True
    if cls.find("of_instruction") == 0:
        return True
    if cls.find("of_queue_prop") == 0:
        return True
    if cls.find("of_table_feature_prop") == 0:
        return True
    # *sigh*
    if cls.find("of_meter_band_stats") == 0:  # NOT A TLV
        return False
    if cls.find("of_meter_band") == 0:
        return True
    if cls.find("of_hello_elem") == 0:
        return True
    if cls == "of_match_v3":
        return True
    if cls == "of_match_v4":
        return True
    return False

def class_is_u16_len(cls):
    """
    Return True if cls_name is an object which uses initial uint16 length
    """
    return cls in ["of_group_desc_stats_entry", "of_group_stats_entry",
                   "of_flow_stats_entry", "of_bucket", "of_table_features",
                   "of_bsn_port_counter_stats_entry", "of_bsn_vlan_counter_stats_entry"]

def class_is_oxm(cls):
    """
    Return True if cls_name is an OXM object
    """
    if cls.find("of_oxm") == 0:
        return True
    return False

def class_is_action(cls):
    """
    Return True if cls_name is an action object

    Note that action_id is not an action object, though it has
    the same header.  It looks like an action header, but the type
    is used to identify a kind of action, it does not indicate the
    type of the object following.
    """
    if cls.find("of_action_id") == 0:
        return False
    if cls.find("of_action") == 0:
        return True

    # For each vendor, check for vendor specific action
    for exp in of_g.experimenter_name_to_id:
        if cls.find("of_action" + exp) == 0:
            return True

    return False

def class_is_action_id(cls):
    """
    Return True if cls_name is an action object

    Note that action_id is not an action object, though it has
    the same header.  It looks like an action header, but the type
    is used to identify a kind of action, it does not indicate the
    type of the object following.
    """
    if cls.find("of_action_id") == 0:
        return True

    # For each vendor, check for vendor specific action
    for exp in of_g.experimenter_name_to_id:
        if cls.find("of_action_id_" + exp) == 0:
            return True

    return False

def class_is_instruction(cls):
    """
    Return True if cls_name is an instruction object
    """
    if cls.find("of_instruction") == 0:
        return True

    # For each vendor, check for vendor specific action
    for exp in of_g.experimenter_name_to_id:
        if cls.find("of_instruction_" + exp) == 0:
            return True

    return False

def class_is_meter_band(cls):
    """
    Return True if cls_name is an instruction object
    """
    # meter_band_stats is not a member of meter_band class hierarchy
    if cls.find("of_meter_band_stats") == 0:
        return False
    if cls.find("of_meter_band") == 0:
        return True
    return False

def class_is_hello_elem(cls):
    """
    Return True if cls_name is an instruction object
    """
    if cls.find("of_hello_elem") == 0:
        return True
    return False

def class_is_queue_prop(cls):
    """
    Return True if cls_name is a queue_prop object
    """
    if cls.find("of_queue_prop") == 0:
        return True

    # For each vendor, check for vendor specific action
    for exp in of_g.experimenter_name_to_id:
        if cls.find("of_queue_prop_" + exp) == 0:
            return True

    return False

def class_is_table_feature_prop(cls):
    """
    Return True if cls_name is a queue_prop object
    """
    if cls.find("of_table_feature_prop") == 0:
        return True
    return False

def class_is_stats_message(cls):
    """
    Return True if cls_name is a message object based on info in unified
    """

    return "stats_type" in of_g.unified[cls]["union"]

def class_is_list(cls):
    """
    Return True if cls_name is a list object
    """
    return (cls.find("of_list_") == 0)

def type_is_of_object(m_type):
    """
    Return True if m_type is an OF object type
    """
    # Remove _t from the type id and see if key for unified class
    if m_type[-2:] == "_t":
        m_type = m_type[:-2]
    return m_type in of_g.unified

def list_to_entry_type(cls):
    """
    Return the entry type for a list
    """
    slen = len("of_list_")
    return "of_" + cls[slen:]

def type_to_short_name(m_type):
    if m_type in of_g.of_base_types:
        tname = of_g.of_base_types[m_type]["short_name"]
    elif m_type in of_g.of_mixed_types:
        tname = of_g.of_mixed_types[m_type]["short_name"]
    else:
        tname = "unknown"
    return tname

def type_to_name_type(cls, member_name):
    """
    Generate the root name of a member for accessor functions, etc
    @param cls The class name
    @param member_name The member name
    """
    members = of_g.unified[cls]["union"]
    if not member_name in members:
        debug("Error:  %s is not in class %s for acc_name defn" %
              (member_name, cls))
        os.exit()

    mem = members[member_name]
    m_type = mem["m_type"]
    id = mem["memid"]
    tname = type_to_short_name(m_type)

    return "o%d_m%d_%s" % (of_g.unified[cls]["object_id"], id, tname)


def member_to_index(m_name, members):
    """
    Given a member name, return the index in the members dict
    @param m_name The name of the data member to search for
    @param members The dict of members
    @return Index if found, -1 not found

    Note we could generate an index when processing the original input
    """
    count = 0
    for d in members:
        if d["name"] == m_name:
            return count
        count += 1
    return -1

def member_base_type(cls, m_name):
    """
    Map a member to its of_ type
    @param cls The class name
    @param m_name The name of the member being gotten
    @return The of_ type of the member
    """
    rv = of_g.unified[cls]["union"][m_name]["m_type"]
    if rv[-2:] == "_t":
        return rv
    return rv + "_t"

def member_type_is_octets(cls, m_name):
    return member_base_type(cls, m_name) == "of_octets_t"

def member_returns_val(cls, m_name):
    """
    Should get accessor return a value rather than void
    @param cls The class name
    @param m_name The member name
    @return True if of_g config and the specific member allow a
    return value.  Otherwise False
    """
    m_type = of_g.unified[cls]["union"][m_name]["m_type"]
    return (config_check("get_returns") =="value" and
            m_type in of_g.of_scalar_types)

def config_check(str, dictionary = of_g.code_gen_config):
    """
    Return config value if in dictionary; else return False.
    @param str The lookup index
    @param dictionary The dict to check; use code_gen_config if None
    """

    if str in dictionary:
        return dictionary[str]

    return False

def h_file_to_define(name):
    """
    Convert a .h file name to the define used for the header
    """
    h_name = name[:-2].upper()
    h_name = "_" + h_name + "_H_"
    return h_name

def type_to_cof_type(m_type):
    if m_type in of_g.of_base_types:
        if "cof_type" in of_g.of_base_types[m_type]:
            return of_g.of_base_types[m_type]["cof_type"]
    return m_type


def member_is_scalar(cls, m_name):
    return of_g.unified[cls]["union"][m_name]["m_type"] in of_g.of_scalar_types

def type_is_scalar(m_type):
    return m_type in of_g.of_scalar_types

def skip_member_name(name):
    return name.find("pad") == 0 or name in of_g.skip_members

def enum_name(cls):
    """
    Return the name used for an enum identifier for the given class
    @param cls The class name
    """
    return cls.upper()

def class_in_version(cls, ver):
    """
    Return boolean indicating if cls is defined for wire version ver
    """

    return (cls, ver) in of_g.base_length

def instance_to_class(instance, parent):
    """
    Return the name of the class for an instance of inheritance type parent
    """
    return parent + "_" + instance

def sub_class_to_var_name(cls):
    """
    Given a subclass name like of_action_output, generate the
    name of a variable like 'output'
    @param cls The class name
    """
    pass

def class_is_var_len(cls, version):
    # Match is special case.  Only version 1.2 (wire version 3) is var
    if cls == "of_match":
        return version == 3

    return not (cls, version) in of_g.is_fixed_length

def base_type_to_length(base_type, version):
    if base_type + "_t" in of_g.of_base_types:
        inst_len = of_g.of_base_types[base_type + "_t"]["bytes"]
    else:
        inst_len = of_g.base_length[(base_type, version)]

def version_to_name(version):
    """
    Convert an integer version to the C macro name
    """
    return "OF_" + of_g.version_names[version]

##
# Is class a flow modify of some sort?

def cls_is_flow_mod(cls):
    return cls in ["of_flow_mod", "of_flow_modify", "of_flow_add", "of_flow_delete",
                   "of_flow_modify_strict", "of_flow_delete_strict"]


def all_member_types_get(cls, version):
    """
    Get the members and list of types for members of a given class
    @param cls The class name to process
    @param version The version for the class
    """
    member_types = []

    if not version in of_g.unified[cls]:
        return ([], [])

    if "use_version" in of_g.unified[cls][version]:
        v = of_g.unified[cls][version]["use_version"]
        members = of_g.unified[cls][v]["members"]
    else:
        members = of_g.unified[cls][version]["members"]
    # Accumulate variables that are supported
    for member in members:
        m_type = member["m_type"]
        m_name = member["name"]
        if skip_member_name(m_name):
            continue
        if not m_type in member_types:
            member_types.append(m_type)

    return (members, member_types)

def list_name_extract(list_type):
    """
    Return the base name for a list object of the given type
    @param list_type The type of the list as appears in the input,
    for example list(of_port_desc_t).
    @return A pair, (list-name, base-type) where list-name is the
    base name for the list, for example of_list_port_desc, and base-type
    is the type of list elements like of_port_desc_t
    """
    base_type = list_type[5:-1]
    list_name = base_type
    if list_name.find("of_") == 0:
        list_name = list_name[3:]
    if list_name[-2:] == "_t":
        list_name = list_name[:-2]
    list_name = "of_list_" + list_name
    return (list_name, base_type)

def version_to_name(version):
    """
    Convert an integer version to the C macro name
    """
    return "OF_" + of_g.version_names[version]

def gen_c_copy_license(out):
    """
    Generate the top comments for copyright and license
    """
    import c_gen.util
    c_gen.util.render_template(out, '_copyright.c')

def accessor_returns_error(a_type, m_type):
    is_var_len = (not type_is_scalar(m_type)) and \
        [x for x in of_g.of_version_range if class_is_var_len(m_type[:-2], x)] != []
    if a_type == "set" and is_var_len:
        return True
    elif m_type == "of_match_t":
        return True
    else:
        return False

def render_template(out, name, path, context, prefix = None):
    """
    Render a template using tenjin.
    out: a file-like object
    name: name of the template
    path: array of directories to search for the template
    context: dictionary of variables to pass to the template
    prefix: optional prefix to use for embedding (for other languages than python)
    """
    pp = [ tenjin.PrefixedLinePreprocessor(prefix=prefix) if prefix else tenjin.PrefixedLinePreprocessor() ] # support "::" syntax
    template_globals = { "to_str": str, "escape": str } # disable HTML escaping
    engine = TemplateEngine(path=path, pp=pp)
    out.write(engine.render(name, context, template_globals))

def render_static(out, name, path):
    """
    Write out a static template.
    out: a file-like object
    name: name of the template
    path: array of directories to search for the template
    """
    # Reuse the tenjin logic for finding the template
    template_filename = tenjin.FileSystemLoader().find(name, path)
    if not template_filename:
        raise ValueError("template %s not found" % name)
    with open(template_filename) as infile:
        out.write(infile.read())

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

from generic_utils import find
from collections import namedtuple
import copy
import loxi_globals
import loxi_front_end.frontend_ir as ir

class InputError(Exception):
    pass


FrontendCtx = namedtuple("FrontendCtx", ("used_enums"))

def get_type(t_ast, ctx):
    if t_ast[0] == "enum":
        ctx.used_enums.add(t_ast[1])

    return t_ast[1]

def create_member(m_ast, ctx):
    if m_ast[0] == 'pad':
        return ir.OFPadMember(length=m_ast[1])
    elif m_ast[0] == 'type':
        return ir.OFTypeMember(name=m_ast[2], oftype=get_type(m_ast[1], ctx), value=m_ast[3])
    elif m_ast[0] == 'data':
        if m_ast[2] == 'length' or m_ast[2] == 'len': # Should be moved to parser
            return ir.OFLengthMember(name=m_ast[2], oftype=get_type(m_ast[1], ctx))
        elif m_ast[2] == 'version': # Should be moved to parser
            return ir.OFVersionMember(name=m_ast[2], oftype=get_type(m_ast[1], ctx))
        elif len(m_ast) > 3:
            return ir.OFOptionalDataMember(name=m_ast[2], oftype=get_type(m_ast[1], ctx), condition=(m_ast[3],m_ast[4]))
        else:
            return ir.OFDataMember(name=m_ast[2], oftype=get_type(m_ast[1], ctx))
    elif m_ast[0] == 'discriminator':
        return ir.OFDiscriminatorMember(name=m_ast[2], oftype=get_type(m_ast[1], ctx))
    elif m_ast[0] == 'field_length':
        return ir.OFFieldLengthMember(name=m_ast[2], oftype=get_type(m_ast[1], ctx), field_name=m_ast[3])
    else:
        raise InputError("Dont know how to create member: %s" % m_ast[0])

def create_ofinput(filename, ast):

    """
    Create an OFInput from an AST

    @param ast An AST as returned by loxi_front_end.parser.parse

    @returns An OFInput object
    """
    ctx = FrontendCtx(set())
    ofinput = ir.OFInput(filename, wire_versions=set(), classes=[], enums=[])

    for decl_ast in ast:
        if decl_ast[0] == 'struct':
            # 0: "struct"
            # 1: name
            # 2: potentially list of [param_name, param_value]
            # 3: super_class or None
            # 4: list of members
            superclass = decl_ast[3]
            members = [create_member(m_ast, ctx) for m_ast in decl_ast[4]]

            discriminators = [ m for m in members if isinstance(m, ir.OFDiscriminatorMember) ]
            if len(discriminators) > 1:
                raise InputError("%s: Cannot support more than one discriminator by class - got %s" %
                        (decl_ast[1], repr(discriminators)))
            ofclass = ir.OFClass(name=decl_ast[1], members=members, superclass=superclass,
                    virtual = len(discriminators) > 0,
                    params = { param: value for param, value in decl_ast[2] })
            ofinput.classes.append(ofclass)
        if decl_ast[0] == 'enum':
            # 0: "enum"
            # 1: name
            # 2: potentially list of [param_name, param_value]
            # 3: list of [constant_name, constant_value]+
            enum = ir.OFEnum(name=decl_ast[1],
                    entries=[ir.OFEnumEntry(name=x[0], value=x[2], params={param:value for param, value in x[1] }) for x in decl_ast[3]],
                    params = { param: value for param, value in decl_ast[2] }
                    )
            ofinput.enums.append(enum)
        elif decl_ast[0] == 'metadata':
            if decl_ast[1] == 'version':
                if decl_ast[2] == 'any':
                    ofinput.wire_versions.update(v.wire_version for v in loxi_globals.OFVersions.all_supported)
                elif int(decl_ast[2]) in loxi_globals.OFVersions.wire_version_map:
                    ofinput.wire_versions.add(int(decl_ast[2]))
                else:
                    raise InputError("Unrecognized wire protocol version %r" % decl_ast[2])

    if not ofinput.wire_versions:
        raise InputError("Missing #version metadata")

    return ofinput

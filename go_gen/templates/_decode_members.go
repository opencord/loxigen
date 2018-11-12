:: # Copyright 2013, Big Switch Networks, Inc.
:: # Copyright 2018, Red Hat, Inc.
:: #
:: # LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
:: # the following special exception:
:: #
:: # LOXI Exception
:: #
:: # As a special exception to the terms of the EPL, you may distribute libraries
:: # generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
:: # that copyright and licensing notices generated by LoxiGen are not altered or removed
:: # from the LoxiGen Libraries and the notice provided below is (i) included in
:: # the LoxiGen Libraries, if distributed in source code form and (ii) included in any
:: # documentation for the LoxiGen Libraries, if distributed in binary form.
:: #
:: # Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
:: #
:: # You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
:: # a copy of the EPL at:
:: #
:: # http://www.eclipse.org/legal/epl-v10.html
:: #
:: # Unless required by applicable law or agreed to in writing, software
:: # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
:: # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
:: # EPL for the specific language governing permissions and limitations
:: # under the EPL.
::
:: from loxi_ir import *
:: import go_gen.oftype
:: import loxi_utils.loxi_utils as loxi_utils
::
:: field_length_members = {}
:: for member in members:
::     decoder_expr = 'decoder'
::
::     if type(member) == OFPadMember:
	decoder.Skip(${member.pad_length})
::     else:
::         member_name = self_name + "." + member.goname
::         oftype = go_gen.oftype.lookup_type_data(member.oftype, version)
::
::         if type(member) == OFDataMember or type(member) == OFDiscriminatorMember:
::             if member.name in field_length_members:
::                 decoder_expr = 'decoder.SliceDecoder(int(%s.%s), 0)' % (self_name, field_length_members[member.name].goname)
::             else:
::                 decoder_expr = 'decoder'
::             #endif
::         #endif
::
::         if oftype:
	${oftype.unserialize.substitute(member=member_name, decoder=decoder_expr)}
::             klass = go_gen.oftype.oftype_get_class(member.oftype, version)
::             if klass and hasattr(klass, "params") and klass.params.get("align", 0):
	decoder.SkipAlign()
::             #endif
::         elif loxi_utils.oftype_is_list(member.oftype):
::             include('_decode_list.go', version=version, member=member, self_name=self_name)
::         else:
::             raise Exception("Unhandled member: %s" % (str(member)))
::         #endif
::
::         if type(member) == OFTypeMember:
	// if ${member_name} != ${member.value} {
	// 	return fmt.Errorf("Wrong value '%d' for type, expected '${member.value}'.", ${member_name})
	// }
::         elif type(member) == OFLengthMember:
	decoder = decoder.SliceDecoder(int(${member_name}), ${member.length} + ${member.offset})
::         elif type(member) == OFFieldLengthMember:
::             field_length_members[member.field_name] = member
::         #endif
::
::     #endif
::
:: #endfor
::
:: if ofclass.has_external_alignment:

	decoder.SkipAlign()

:: #endif
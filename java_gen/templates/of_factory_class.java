//:: # Copyright 2013, Big Switch Networks, Inc.
//:: #
//:: # LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
//:: # the following special exception:
//:: #
//:: # LOXI Exception
//:: #
//:: # As a special exception to the terms of the EPL, you may distribute libraries
//:: # generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
//:: # that copyright and licensing notices generated by LoxiGen are not altered or removed
//:: # from the LoxiGen Libraries and the notice provided below is (i) included in
//:: # the LoxiGen Libraries, if distributed in source code form and (ii) included in any
//:: # documentation for the LoxiGen Libraries, if distributed in binary form.
//:: #
//:: # Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
//:: #
//:: # You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
//:: # a copy of the EPL at:
//:: #
//:: # http::: #www.eclipse.org/legal/epl-v10.html
//:: #
//:: # Unless required by applicable law or agreed to in writing, software
//:: # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
//:: # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
//:: # EPL for the specific language governing permissions and limitations
//:: # under the EPL.
//::
//:: import itertools
//:: import of_g
//:: include('_copyright.java')

//:: include('_autogen.java')

package ${factory.package};

//:: include("_imports.java")

public class ${factory.name} implements ${factory.interface.name} {
    public final static ${factory.name} INSTANCE = new ${factory.name}();
    private ${factory.name}() {}

    //:: for name, clazz in factory.interface.sub_factories.items():
    public ${clazz} ${name}() {
        return ${clazz}Ver${factory.version.of_version}.INSTANCE;
    }
    //:: #endfor

//:: for i in factory.interface.members:
    //:: if i.is_virtual:
    //::    continue
    //:: #endif

    //:: if len(i.writeable_members) > 0:
    public ${i.name}.Builder ${factory.interface.method_name(i, builder=True)}() {
        //::   if i.has_version(factory.version) and model.generate_class(i.versioned_class(factory.version)):
        return new ${i.versioned_class(factory.version).name}.Builder();
        //:: else:
        throw new UnsupportedOperationException("${i.name} not supported in version ${factory.version}");
        //:: #endif
    }
    //:: #endif
    //:: if len(i.writeable_members) <= 2:
    public ${i.name} ${factory.interface.method_name(i, builder=False)}(${", ".join("%s %s" % (p.java_type.public_type, p.name) for p in i.writeable_members)}) {
        //::   if i.has_version(factory.version) and model.generate_class(i.versioned_class(factory.version)):
        //:: if len(i.writeable_members) > 0:
        return new ${i.versioned_class(factory.version).name}(
                ${",\n                      ".join(
                         [ prop.name for prop in i.versioned_class(factory.version).data_members])}
                    );
        //:: else:
        return ${i.versioned_class(factory.version).name}.INSTANCE;
        //:: #endif
        //:: else:
        throw new UnsupportedOperationException("${i.name} not supported in version ${factory.version}");
        //:: #endif
    }
    //:: #endif
//:: #endfor

    public OFMessageReader<${factory.base_class}> getReader() {
//:: if factory.versioned_base_class:
        return ${factory.versioned_base_class.name}.READER;
//:: else:
        throw new UnsupportedOperationException("Reader<${factory.base_class}> not supported in version ${factory.version}");
//:: #endif
    }

//:: if factory.interface.name == 'OFOxms':
    @SuppressWarnings("unchecked")
    public <F extends OFValueType<F>> OFOxm<F> fromValue(F value, MatchField<F> field) {
        switch (field.id) {
            //:: for oxm_name in model.oxm_map:
            //::    type_name, value, masked = model.oxm_map[oxm_name]
            //::    if masked:
            //::        continue
            //::    #endif
            //::    method_name = oxm_name.replace('OFOxm', '')
            //::    method_name = method_name[0].lower() + method_name[1:]
            case ${value}:
                //:: # The cast to Object is done to avoid some javac bug that in some versions cannot handle cast from generic type to other types but Object
                return (OFOxm<F>)((Object)${method_name}((${type_name})((Object)value)));
            //:: #endfor
            default:
                return null;
        }
    }

    @SuppressWarnings("unchecked")
    public <F extends OFValueType<F>> OFOxm<F> fromValueAndMask(F value, F mask, MatchField<F> field) {
        switch (field.id) {
            //:: for oxm_name in model.oxm_map:
            //::    type_name, value, masked = model.oxm_map[oxm_name]
            //::    if not masked:
            //::        continue
            //::    #endif
            //::    method_name = oxm_name.replace('OFOxm', '')
            //::    method_name = method_name[0].lower() + method_name[1:]
            case ${value}:
                //:: # The cast to Object is done to avoid some javac bug that in some versions cannot handle cast from generic type to other types but Object
                return (OFOxm<F>)((Object)${method_name}((${type_name})((Object)value), (${type_name})((Object)mask)));
            //:: #endfor
            default:
                return null;
        }
    }

    @SuppressWarnings("unchecked")
    public <F extends OFValueType<F>> OFOxm<F> fromMasked(Masked<F> masked, MatchField<F> field) {
        switch (field.id) {
            //:: for oxm_name in model.oxm_map:
            //::    type_name, value, masked = model.oxm_map[oxm_name]
            //::    if not masked:
            //::        continue
            //::    #endif
            //::    method_name = oxm_name.replace('OFOxm', '')
            //::    method_name = method_name[0].lower() + method_name[1:]
            case ${value}:
                //:: # The cast to Object is done to avoid some javac bug that in some versions cannot handle cast from generic type to other types but Object
                return (OFOxm<F>)((Object)${method_name}((${type_name})((Object)(masked.getValue())), (${type_name})((Object)(masked.getMask()))));
            //:: #endfor
            default:
                return null;
        }
    }
//:: #endif

}

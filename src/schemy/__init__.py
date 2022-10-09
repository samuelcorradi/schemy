from __future__ import annotations
import copy
import re
from datetime import date
from datetime import datetime
from schemy.exceptions import InvalidFieldName, MissingField, InvalidType, InvalidName

class Schema(object):

    default_name:str = 'col{}'

    @staticmethod
    def gen_field_name(field_pos:int):
        return Schema.default_name.format(field_pos)

    def __init__(self):
        self._schema = []
        self._pks = []
        self._alias = {}
        self.gen_field_name = self._instance_gen_field_name

    def __str__(self):
        return self.to_str()

    class SQL(object):

        def __init__(self, schema:Schema):
            self._schema = schema
            """
            Cria comando SQL para create table.
            """

        def sql_cast_type(self, ftype):
            """
            """
            sql_type=''
            if ftype is str:
                sql_type = 'VARCHAR'
            elif ftype is int:
                sql_type = 'INT'
            else:
                raise InvalidType("Unknow type: {}".format(ftype))
            return sql_type 

        def sql_field_schema(self
            , field:Schema._Field
            , max_limit:int
            , min_limit:int)->str:
            """
            Cria a parte de definicao dos campos.
            """
            fname = self._schema._get_field_alias_name(field)
            ftype = self.sql_cast_type(field._f.get('ftype', str))
            sql = "[{}] {}".format(fname, ftype)
            if ftype!='DATETIME':
                size = field._f.get('size', 0)
                primary_key = field in self._schema._pks #._f.get('primary_key', False)
                auto_increment = field._f.get('auto_increment', 0)
                if not auto_increment:
                    # if size<=0:
                    if size<min_limit:
                        size = min_limit
                    sql += "({})".format('MAX' if size>max_limit else str(size))
                if primary_key:
                    sql += ' PRIMARY KEY'
                # soh pode ser identidade se for um campo 
                # original do schema que estah sendo 
                # impresso, e nao uma fk
                if field._schema==self and auto_increment:
                    sql += ' IDENTITY(1,{})'.format(auto_increment)
            if not field._f.get('optional', True):
                sql += ' NOT NULL'
            return sql

        def create_table(self
            , tablename:str
            , cmd_prefix=''
            , cmd_sufix=''
            , max_limit=400
            , min_limit=6
            , exclude_zero_lenght=True)->str:
                
            field_list = []
            for f in self._schema._schema:
                size = f._f.get('size', 0)
                ftype = self.sql_cast_type(f._f.get('ftype', str))
                # field_schema = _default_schema(field_schema)
                # ser for para excluir campos que tem tamanho 0
                # e o tipo deste campo nao for DATETIME
                if exclude_zero_lenght and (size<=0 and ftype!='DATETIME'):
                    continue
                field_list.append(self.sql_field_schema(field=f
                    , max_limit=max_limit
                    , min_limit=min_limit) + "\n")
            return cmd_prefix + "CREATE TABLE {} (\n\t  ".format(tablename) + "\t, ".join(field_list) + ")" + cmd_sufix

    class _Field(object):
        """
        Class to represent the 
        caracteristics of a field.
        """

        def __init__(self
            , name:str
            , ftype=str
            , size:int=50
            , default=None
            , auto_increment:int=0
            , optional:bool=False
            , out_format:str=None):
            self._schema:Schema = None
            # trata o campo default caso
            # seja obritatorio
            if optional and default is None:
                if type is int:
                    default = 0
            self._f = {'size':size
                , 'default': default
                , 'auto_increment':auto_increment
                , 'optional':optional
                , 'out_format':out_format}
            self.set_name(name)
            self.set_type(ftype)

        def copy(self, deep:bool=True):
            cp = copy.deepcopy(self) if deep else copy.copy(self)
            cp._schema = self._schema
            if cp._schema:
                cp._schema.append_field(cp)

        def __deepcopy__(self, memo):
            cp = object.__new__(type(self))
            cp._f = copy.deepcopy(self._f)
            return cp

        def __copy__(self):
            """
            Create an independent copy of this
            object.
            """
            cp = object.__new__(type(self))
            cp._f = self._f
            return cp

        def set_type(self, ftype):
            """
            Define o tipo do campo. Necessita
            receber tipos especificos caso
            contrario retorna erro.
            """
            if ftype not in (str, int, float, bool, datetime, date):
                raise InvalidType("Invalid type: {}".format(type(ftype)))
            self._f['ftype'] = ftype
            return self

        def set_schema(self
            , schema:Schema):
            self._schema = schema

        def is_index(self):
            """
            Tells if the field is part
            of the schema index to which
            it is a part. If the field
            does not have a defined schema
            returns None.
            """
            if self._schema:
                return self in self._schema._pks

        def pk(self):
            """
            Add the field in the primary key 
            list of schema.
            """
            self._schema.set_primary(self)
            return self

        def set_name(self, name:str):
            """
            TODO: restringir ou nao o nome dos campos?
            """
            print(name, type(name))
            # valida a variavel
            if type(name) is not str:
                raise InvalidFieldName("The field name must be a string.")
            if name.isdigit():
                name = Schema.default_name.format(name)
            if not re.fullmatch(re.compile(r"[A-Za-z0-9\_]+"), name):
                pass # raise Exception("Fields must have alphanumeric names, containing only letters, numbers and the character '_'.")
            if re.fullmatch(re.compile(r"[0-9\_]"), name):
                raise InvalidFieldName("Field names must always start with letters.")
            self._f['name'] = name
            return self

        def get_name(self, use_alias=True):
            """
            Gets the field name. If field has 
            an alias, return the alias.
            """
            if self._schema and use_alias and self._schema._alias:
                # print(self._schema._alias)
                keys = list(self._schema._alias.keys())
                values = list(self._schema._alias.values())
                # print(values)
                if self in values:
                    i = values.index(self)
                    return keys[i]
            # if not self._f['name']:
            #     return schema._get_default_name()
            return self._f['name']

    def to_str(self)->str:
        fields = self.get_names()
        return "{" + ','.join(fields) + "}"

    def len(self):
        """
        Informa a quantidade de colunas
        existentes no schema. Basicamente
        conta a quantidade de posicoes da
        lista onde os campos sao definidos.
        """
        return len(self._schema)

    def sql(self)->Schema.SQL:
        return Schema.SQL(self)

    def __get_field_alias_pos(self, field:Schema._Field)->int:
        if self._alias:
            v = list(self._alias.values())
            if field in v:
                i = v.index(field)
                return i
        
    def _get_field_alias_name(self, field:Schema._Field)->str:
        i = self.__get_field_alias_pos(field)
        if i:
            return list(self._alias.keys())[i]
        return field.get_name()


    def copy(self, deep:bool=False)->Schema:
        """
        Faz uma copia do objeto de Schema.
        Eh usado quando se faz copias
        de Datasets.
        """
        cp = copy.deepcopy(self) if deep else copy.copy(self)
        return cp

    def __deepcopy__(self, mode):
        cp = Schema()
        for f in self._schema:
            fcp = copy.deepcopy(f)
            fcp._schema = cp
            cp.append_field(fcp)
            if f in self._pks:
                cp._pks.append(fcp)
            # cp._alias = copy.copy(self._alias)
        print(self._alias)
        if self._alias:
            for k, v in self._alias.items():
                cp._alias[k] = v
        return cp

    def __copy__(self):
        cp = object.__new__(type(self))
        cp._schema = copy.copy(self._schema)
        cp._pks = copy.copy(self._pks)
        cp._alias = copy.copy(self._alias)
        return cp

    def _instance_gen_field_name(self):
        """
        Gera um novo nome para um campo.
        Usa o formato padrão da classe
        para gerar o nome.
        @see Schema.gen_field_name
        @see Schema.default_name
        """
        return Schema.gen_field_name(len(self._schema))

    def __valid_type(self, ftype):
        """
        Valid if is a legal field type.
        """
        return ftype in (int, str, float, bool, bytes, datetime, date)

    def __valid_name(self, name):
        """
        Valid the field name.
        The name must be a string or a int value.
        """
        if name not in (int, str):
            return False
        return True

    def _gen_field(self
        , name:str=None
        , ftype=str
        , size:int=50
        , default=None
        , auto_increment:int=0
        , optional:bool=False
        , out_format:str=None):
        if not self.__valid_type(ftype):
            raise InvalidType("Invalid type: {}".format(type(ftype)))
        if not name:
            name = self.gen_field_name()
        f = self._Field(name=name
            , ftype=ftype
            , size=size
            , default=default
            , auto_increment=auto_increment
            , optional=optional
            , out_format=out_format)
        return f

    def Field(self
        , name:str=None
        , ftype=str
        , size:int=50
        , default=None
        , primary_key:bool=False
        , auto_increment:int=0
        , optional:bool=False
        , out_format:str=None
        , col_ref:int=None
        , pos:str='a')->_Field:
        """
        Interface para instaciar a classe _Field
        e adicionar novos campos ao schema.
        """
        # se nao foi passado um nome, gera um nome
        f = self.add_field(name=name
            , ftype=ftype
            , size=size
            , default=default
            , primary_key=primary_key
            , auto_increment=auto_increment
            , optional=optional
            , out_format=out_format
            , col_ref=col_ref
            , pos=pos)
        return f

    def add_field(self
        , name:str=None
        , ftype=str
        , size:int=50
        , default=None
        , primary_key:bool=False
        , auto_increment:int=0
        , optional:bool=False
        , out_format:str=None
        , col_ref:int=None
        , pos:str='a')->_Field:
        f = self._gen_field(name=name
            , ftype=ftype
            , size=size
            , default=default
            , auto_increment=auto_increment
            , optional=optional
            , out_format=out_format)
        f.set_schema(self)
        self.append_field(field=f, col_ref=col_ref, pos=pos)
        if primary_key:
            self.set_primary(f)
        return f

    def get_field_pos(self, name)->int:
        """
        Retorna a posicao que um campo
        ocupa na lista de campos do schema.
        """
        if type(name) is int:
            if name>len(self._schema):
                raise MissingField("Failed to find field at position: {}. You are trying to refer to a field at position '{}' while there are only '{}' fields defined in the schema.".format(name, name, len(self._schema)))
            return name
        elif type(name) is str:
            allpos = self.get_all_field_pos()
            pos = allpos.get(name, None)
            return pos
        else:
            raise InvalidName("Invalid field name type: '{}'. A field name must be a string or an integer (that indicates the position in the schema).".format(type(name)))
            
    def rm_field(self, name)->_Field:
        pos = self.get_field_pos(name)
        # if field exists
        if pos:
            f = self._schema.pop(pos-1)
            # removes the index
            if f.is_index():
                i = self._pks.index(f)
                self._pks.pop(i)
            # remove alias
            if self._alias:
                v = self._alias.items()
                if f in v:
                    i = v.index(f)
                    self._alias.pop(i)
            f._schema = None
            return f

    def rename_field(self, name:str, new_name:str)->Schema:
        pos = self.get_field_pos(name)
        if pos:
            self.set_alias(self._schema[pos-1], new_name)
        return self

    def get_field(self, aliasname:str):
        """
        """
        flist = self.get_all_field_pos()
        fpos = flist.get(aliasname, 0)
        return self._schema[fpos-1] if fpos else None

    def get_all_field_pos(self)->dict:
        """
        """
        allpos = {}
        for i, f in enumerate(self._schema):
            allpos[f.get_name()]=i+1
        return allpos

    def append_field(self
        , field:_Field
        , col_ref=None
        , pos='a'):
        """
        Metodo para adicionar um campo
        ao schema na posicao indicada.
        """
        # self._schema.append(f)
        if col_ref is None:
            self._schema.append(field)
        else:
            if pos=='a':
                col_ref += 1
            self._schema[col_ref:col_ref] = [field]
        return self

    def pk(self
        , name:str=None
        , ftype=int
        , size:int=50
        , default=None
        , auto_increment:int=1
        , col_ref:int=None
        , pos:str='a'
        , out_format:str=None)->_Field:
        """
        Cria um campo do tipo primary key.
        """
        f = self.Field(name=name
            , ftype=ftype
            , size=size
            , default=default
            , auto_increment=auto_increment
            , col_ref=col_ref
            , pos=pos
            , primary_key=True
            , optional=False
            , out_format=out_format)
        return f

    def get_names(self)->list:
        """
        Retorna a lista de nomes (ou alias)
        de todos os campos do schema.
        """
        name = []
        for f in self._schema:
            name.append(f.get_name())
        return name

    def optional(self
        , name:str=None
        , ftype=str
        , size:int=50
        , col_ref:int=None
        , pos:str='a'
        , out_format:str=None)->_Field:
        """
        Cria um campo opcional.
        """
        return self.Field(name=name
            , ftype=ftype
            , size=size
            , col_ref=col_ref
            , pos=pos
            , default=None
            , auto_increment=0
            , primary_key=False
            , optional=True
            , out_format=out_format)
        
    def set_primary(self, field:_Field):
        """
        Adiciona um campo como parte
        da chave primaria do schema
        caso o campo faca parte do schema.
        """
        # se o campo nao existe, retorna erro
        if not self.field_exists(field):
            raise MissingField("It's not possible to define as key for a schema if field that does not make part of it.")
        if field not in self._pks:
            self._pks.append(field)
        return self

    #################################
    # metodos de relacionamento
    #################################
    def has(self
        , schema:Schema
        , identified=False
        , fields=None
        , alias=None):
        """
        """
        # se a lista de campos nao for informado
        # utiliza as chaves primarias
        if not fields:
            fields = self._pks
        i:int = 0
        for f in fields:
            if not schema.field_exists(f):
                schema.append_field(f)
            if identified:
                schema.set_primary(f)
            if alias and i<=(len(alias)-1):
                schema.set_alias(f, alias[i])
            i += 1
        return self

    def nm(self
        , schema:Schema
        , identified=False
        , source_fields:list=None
        , source_alias:list=None
        , target_fields:list=None
        , target_alias:list=None):
        """
        Create a nxn relation between two schemas.
        Return a third schema who defines the
        relation.
        """
        bridge = Schema()
        self.has(bridge, identified, source_fields, source_alias)
        schema.has(bridge, identified, target_fields, target_alias)
        return bridge

    def belongs(self
        , schema:Schema
        , identified=False
        , fields:list=None
        , alias:list=None)->Schema:
        """
        Propaga os campos do relacionamento
        para o schema fonte.
        """
        # se nao foi indicado quais
        # colunas propagar, usar as pks
        if not fields:
            fields = []
            for pk in schema._pks:
                fields.append(pk)
        # ...
        i:int = 0
        for f in fields:
            if not self.field_exists(f):
                self._schema.append(f)
            # se for um relacionamento identificado
            # coloca esse campo na lista de pks
            if identified:
                self.set_primary(f)
            if alias and i<=(len(alias)-1):
                self.set_alias(f, alias[i])
            i += 1
        # ...
        return self

    def field_exists(self
        , field:_Field)->bool:
        """
        Check if a field is part of schema.
        """
        for f in self._schema:
            if f==field:
                return True 
        return False
        
    def set_alias(self
        , field:_Field
        , alias:str)->Schema:
        """
        Defines an alias for a field.
        """
        # se o campo nao existe, retorna erro
        if not self.field_exists(field):
            raise MissingField("It's not possible to define a alias for a field that does not exist in the schema.")
        self._alias[alias] = field
        return self

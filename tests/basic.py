from schemy import Schema

if __name__ == "__main__":
    # a classe gera nome de colunas
    print(Schema.gen_field_name(10))

    schema = Schema()

    # chave primaria
    schema.pk('id')

    nome = schema.add_field('nome', ftype=str)
    col1 = schema.Field()
    print(schema)
    print(schema.len())

    print(schema.sql().create_table(tablename="table"))

    teste_cp1 = schema.copy(deep=True)
    teste_cp2 = schema.copy(deep=False)
    nome._f['size'] = 100
    print(teste_cp1.sql().create_table("tb_teste"))
    print(teste_cp2.sql().create_table("tb_teste2"))

    print("Posicao do campo {}: {}".format('nome', schema.get_field_pos('nome')))
    print(schema.get_all_field_pos())

    # remove campo
    f = schema.rm_field('col1')
    print(schema.sql().create_table(tablename="tb1"))

    # renomeia campo
    schema.rename_field(name='nome', new_name='nome_completo')
    print(schema.sql().create_table(tablename="tb1"))

    # lista dos campos
    print("\nLista de nomes de campos na ordem com que aparem no schema.")
    print(schema.get_names())

    # pega posicao de um campo no esquema
    print("\nPega a posicao de todos os campos no schema.")
    print(schema.get_all_field_pos())

    # pega posicao de um campo no esquema
    print("\nPega a posicao de um campo no schema.")
    print(schema.get_field_pos('nome_completo'))

    # copia de esquema
    novo_schema = schema.copy(deep=True)
    fld_nome = schema.get_field('nome_completo')
    fld_nome._f['size'] = 88
    print(novo_schema.sql().create_table(tablename="new_table"))

    # relacionamentos
    novo_schema.belongs(schema, alias=['esquema_antigo'])
    print(novo_schema.sql().create_table(tablename="new_table"))

    novo_schema.has(schema, alias=['fk_novo_schema'])
    print(schema.sql().create_table(tablename="new_table"))

    #mn
    relacao = novo_schema.nm(schema)
    print(novo_schema.sql().create_table(tablename="new_table"))
    print(schema.sql().create_table(tablename="table"))
    print(relacao.sql().create_table(tablename="relation"))

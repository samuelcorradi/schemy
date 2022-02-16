from schemy import Schema

if __name__ == "__main__":
    # a classe gera nome de colunas
    print(Schema.gen_field_name(10))

    schema = Schema("teste")

    # chave primaria
    schema.pk('id')

    nome = schema.add_field('nome')
    col1 = schema.Field()
    print(schema)
    print(schema.len())

    print(schema.sql_create_table())

    teste_cp1 = schema.copy(deep=True)
    teste_cp2 = schema.copy(deep=False, newname='teste_cp2')
    nome._f['size'] = 100
    print(teste_cp1.to_sql())
    print(teste_cp2.to_sql())

    print(schema.get_field_pos('nome'))
    print(schema.get_all_field_pos())

    # remove campo
    f = schema.rm_field('col1')
    print(schema.sql_create_table())

    # renomeia campo
    schema.rename_field(name='nome', new_name='nome_completo')
    print(schema.sql_create_table())

    # lista dos campos
    print(schema.get_names())

    # copia de esquema
    novo_schema = schema.copy(newname='nova_tabela', deep=True)
    fld_nome = schema.get_field('nome_completo')
    fld_nome._f['size'] = 88
    print(novo_schema.to_sql())

    # relacionamentos
    novo_schema.belongs(schema, alias=['esquema_antigo'])
    print(novo_schema.to_sql())

    novo_schema.has(schema, alias=['fk_novo_schema'])
    print(schema.to_sql())

    #mn
    relacao = novo_schema.nm(schema)
    print(novo_schema.to_sql())
    print(schema.to_sql())
    print(relacao.to_sql())

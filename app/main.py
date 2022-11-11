from flask import Flask
from flask_restx import reqparse, abort, Api, Resource, fields

app = Flask(__name__)
api = Api(app,
        version='1.0',
        title='API dos Produtos de uma Empresa',
        description='Permite gerenciar os registros dos produtos de uma empresa',
        doc='/doc')

PRODUTOS = [{'id': 1, 'nome': 'calça', 'quantidade': 12, 'preco': 89.94},
            {'id': 2, 'nome': 'camisa', 'quantidade': 54, 'preco': 49.99},
            {'id': 3, 'nome': 'saia', 'quantidade': 33, 'preco': 72.14},
            {'id': 4, 'nome': 'sapato', 'quantidade': 12, 'preco': 99.11},
            {'id': 5, 'nome': 'vestido', 'quantidade': 47, 'preco': 78.32}]

def aborta_se_o_produto_nao_existe(id):
    encontrei = False
    for produto in PRODUTOS:
        if produto['id'] == int(id):
            encontrei = True
    if encontrei == False:
        abort(404, mensagem="O produto com id = {} não existe".format(id)) #404:Not Found

# Parse dos dados enviados na requisição no formato JSON:
parser = reqparse.RequestParser()
parser.add_argument('id', type=int, help='identificador do produto')
parser.add_argument('nome', type=str, help='nome do produto')
parser.add_argument('quantidade', type=int, help='quantidade do produto')
parser.add_argument('preco', type=float, help='preço do produto')


campos_obrigatorios_para_atualizacao = api.model('Atualizaçao de Produto', {
    'id': fields.Integer(required=True, description='identificador do produto'),
    'nome': fields.String(required=True, description='nome do produto'),
    'quantidade': fields.Integer(required=True, description='quantidade do produto'),
    'preco': fields.Float(required=True, description='preço do produto'),
})

campos_obrigatorios_para_atualizacao_parcial = api.model('Atualizaçao de Produto', {
    'preco': fields.Float(required=True, description='preço do produto'),
})

campos_obrigatorios_para_insercao = api.model('Inserção de Produto', {
    'id': fields.Integer(required=False, readonly=True, description='identificador do produto'),
    'nome': fields.String(required=True, description='nome do produto'),
    'quantidade': fields.Integer(required=True, description='quantidade do produto'),
    'preco': fields.Float(required=True, description='preço do produto'),
})

campos_obrigatorios_para_compra_venda = api.model('Venda de Produto', {
    'quantidade': fields.Integer(required=True, description='quantidade do produto'),
})


# Produto:
# 1) Apresenta um único produto.
# 2) Remove um único produto.
# 3) Atualiza (substitui) um produto.


@api.route('/produtos/<id>')
@api.doc(params={'id': 'identificador do produto'})
class Produto(Resource):
    @api.doc(responses={200: 'produto retornado'})
    def get(self, id):
        aborta_se_o_produto_nao_existe(id)
        return PRODUTOS[int(id)]

    @api.doc(responses={204: 'produto removido'}) #204: No Content
    def delete(self, id):
        aborta_se_o_produto_nao_existe(id)
        del PRODUTOS[int(id)]
        return '', 204


    @api.doc(responses={200: 'produto substituído'}) #200: OK
    @api.expect(campos_obrigatorios_para_atualizacao)
    def put(self, id):
        aborta_se_o_produto_nao_existe(id)
        args = parser.parse_args()
        for produto in PRODUTOS:
            if produto['id'] == int(id):
                produto['id'] = args['id']
                produto['nome'] = args['nome']
                produto['quantidade'] = args['quantidade']
                produto['preco'] = args['preco']
                break
            return produto

    @api.doc(responses={200: 'produto substituído'})  # 200: OK
    @api.expect(campos_obrigatorios_para_atualizacao_parcial)
    def patch(self, id):
        aborta_se_o_produto_nao_existe(id)
        args = parser.parse_args()
        for produto in PRODUTOS:
            if produto['id'] == int(id):
                produto['preco'] = args['preco']
                break
        return produto  # 200: OK

# ListaProduto:
# 1) Apresenta a lista de produtos.
# 2) Insere um novo produto.

@api.route('/produtos') 
class ListaProduto(Resource):
    @api.doc(responses={200: 'produtos retornados'})
    def get(self):
        return PRODUTOS

    @api.doc(responses={201: 'produto inserido'}) #201: Created
    @api.expect(campos_obrigatorios_para_insercao)
    def post(self):
        args = parser.parse_args()
        id = -1
        for produto in PRODUTOS:
            if int(produto['id']) > id:
                id = int(produto['id'])
        id = id + 1
        produto = {'id': id, 'nome': args['nome'], 'quantidade': args['quantidade'], 'preco': args['preco']}
        PRODUTOS.append(produto)
        return produto, 201

@api.route('/quantidades')
class QuantidadeTotal(Resource):
    def get(self):
        total = 0 
        for produto in PRODUTOS:
            total = total + produto["quantidade"]
        return total

@api.route('/quantidades/<id>')
class QuantidadeTotalProduto(Resource):
    def get(self, id):
        for produto in PRODUTOS:
            if produto['id'] == int(id):
                return produto['quantidade']

@api.route('/estoque')
class Estoque(Resource):
    def get(self):
        for produto in PRODUTOS:
            menor = produto['quantidade']
            maior = produto['quantidade']
            if produto['quantidade'] < menor:
                menor = produto['quantidade']
            if produto['quantidade'] < maior:
                maior = produto['quantidade']
        dados_estoque = {
            "Maior quantidade" : maior,
            "Menor quantidade" : menor
        }
        return dados_estoque

@api.route('/total/estoque')
class ValorTotalEstoque(Resource):
    def get(self):
        total = 0
        for produto in PRODUTOS:
            total = total + produto["quantidade"]*produto["preco"]
        return total

@api.route('/venda/<id>')
@api.doc(params={'id': 'identificador do produto'})
class VendaProduto(Resource):
    @api.doc(responses={200: 'quantidade do produto retornada'}) 
    @api.expect(campos_obrigatorios_para_compra_venda)
    def patch(self,id):
        aborta_se_o_produto_nao_existe(id)
        args = parser.parse.args()
        for produto in PRODUTOS:
            if produto['id'] == int(id):
                produto['quantidade'] = produto['quantidade'] - int(args['quantidade'])
                break
        return produto
@api.route('/compra/<id>')
@api.doc(params={'id': 'identificador do produto'})
class CompraProduto(Resource):
    @api.doc(responses={200: 'quantidade do produto retornada'})    
    @api.expect(campos_obrigatorios_para_compra_venda)
    def patch(self,id):
        aborta_se_o_produto_nao_existe(id)
        args = parser.parse_args()
        for produto in PRODUTOS:
            if produto['id'] == int(id):
                produto['quantidade'] = produto['quantidade'] + int(args['quantidade'])
                break
        return produto


if __name__ == '__main__':
    app.run(debug=True)
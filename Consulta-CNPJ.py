
import pandas as pd
import requests, json, re, os.path

current_path = os.path.dirname(os.path.realpath(__file__))

class consulta_cnpj:
    def verifica():
        """Verificação se o CSV já existe se não Cria"""
        if os.path.isfile(f'{current_path}\\historico.csv'):
            print("histórico já existe")
            pass
        else:
            print("criando histórico")

            df = pd.DataFrame(columns=[
                'name',
                'document_number',
                'document_type',
                'address',
                'complement',
                'neighborhood',
                'zip_code',
                'city',
                'state',
                'description'
                ] )

            df.to_csv(f'{current_path}\\historico.csv')

    # Adicionando um CNPJ
    def solicita_cnpj(): 
        cnpj = input(str("digite o CNPJ: "))

        """Processando formato do CNPJ"""
        if type(cnpj) is int:
            cnpj = str(cnpj).strip()
        else:
            cnpj = re.split("[./-]",cnpj)
            c = 0
            cnpj_formatado = ''

            for parte in cnpj:
                cnpj_formatado = cnpj_formatado + cnpj[c]
                c = c + 1
            
            cnpj = cnpj_formatado.strip().replace("/", "")
            
        return cnpj

    '''
    CNPJ's para testar
    Linx: 06.948.969/0001-75
    Napp: 20.612.379/0001-06
    Oraculo: 28.057.926/0001-32
    '''

    # Fazendo a request
    def consulta(cnpj):
        result = json.loads((requests.get(f'https://www.receitaws.com.br/v1/cnpj/{cnpj}')).text)
        return result

    # Montando json
    def base(result):
        unidade = {
            "name": f"{result['nome']}",
            "document_number": f"{result['cnpj']}",
            "document_type": "CNPJ",
            "address": f"{result['logradouro']}",
            "complement": f"{result['cnpj']}",
            "neighborhood": f"{result['bairro']}",
            "zip_code": f"{result['cep']}",
            "city": f"{result['municipio']}", 
            "state": f"{result['uf']}",
            "description": f"{result['fantasia']}"
        }

        base = json.dumps(unidade, indent=3) 
        base = json.loads(base)
        return base

    '''Não usar pois pode duplicar uma unidade que já existe ou criar uma unidade que nao deveria existir'''
    #napp = requests.post(f'https://sellers.nappsolutions.io/api/sellers/', base)

    ''' Fazendo os tratamentos em json e transfomando em CSV'''
    def gera_csv(base):
        df_base = pd.json_normalize(base)
        lista_base = df_base.values.tolist()
        lista = list()

        df_historico = pd.read_csv(f'{current_path}\\historico.csv', names=[
                'name',
                'document_number',
                'document_type',
                'address',
                'complement',
                'neighborhood',
                'zip_code',
                'city',
                'state',
                'description'
                ])
        lista_histotico = df_historico.values.tolist()

        for lista in lista_base:
            for item in lista_base:
                name = item[0]
                document_number = item[1]
                document_type = item[2]
                address = item[3]
                complement = str(item[4])
                neighborhood = item[5]
                zip_code = item[6]
                city = item[7]
                state = item[8]
                description = item[9]
                lista.append([name, document_number, document_type, address, complement, neighborhood, zip_code, city, state, description])
            lista_histotico.append(lista[0:9])

        df_final = pd.DataFrame(lista_histotico)

        df_final.drop_duplicates(keep='first', inplace=True)
        df_final.to_csv(f'{current_path}\\historico.csv', header=0, index=False)

    #Execução
    verifica()
    solicita = solicita_cnpj()
    cnpj_f = consulta(solicita)
    baseconsulta = base(cnpj_f)
    gera_csv(baseconsulta)
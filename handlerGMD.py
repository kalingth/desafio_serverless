#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import boto3
from decimal import Decimal
from botocore.exceptions import ClientError
from typing import Any


def responseFactory() -> dict:
    """função responseFactory:

    Função baseada no padrão de projeto Factory. Responsável por criar uma resposta genérica a ser retornada para o API Gateway.
    :return: Dicionário genérico contendo o tipo da resposta e o código da resposta.
    """
    response = dict()
    response["headers"] = {"Content-Type": "application/json"}
    return response


def transformBody(body: dict) -> str:
    """função transformBody

    Furnção responsável por formatar os dados em um texto que possa ser interpretado como JSON.
    :param body: Dicionário contendo os dados que deverão ser formatados.
    :return: Um conjunto de dados em formato textual que deverão ser tratados como um JSON pelo navegador do usuário.
    """
    pattern = lambda item: float(item) if isinstance(item, Decimal) else item
    return json.dumps(body, default=pattern)


def makeBody(s3objectkey: str) -> (str, int):
    """Função makeBody:

    Realiza a leitura dos metadados da imagem informada e retorna o corpo da requisição já corretamente formatado.
    :param s3objectkey: Nome da imagem a ser buscado no banco de dados.
    :return: Retorna os metadados lidos
    """
    body = {"success": False, "data": None}
    try:
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table("serverless-challenge-dev")
        data = table.get_item(Key={"s3objectkey": s3objectkey})
        body["data"] = data["Item"]
    except KeyError as e:
        status_code = 404
        print(e)
    except ClientError as e:
        status_code = 500
        print(e.response["Error"]["Message"])
    else:
        body["success"] = True
        status_code = 200

    return transformBody(body), status_code


def getMetadata(event: dict, context: Any) -> dict:
    """Função getMetadata

    Função executada quando um usuário realiza uma chamada no URN /images/ do End Point criado para a aplicação.
    Caso o registro dos metadados da imagem solicitada sejam encontrados, retornará um JSON no seguinte formato:
        {
            "success": false,   // Indicando que obteve sucesso na requisição.
            "data": {
                "s3objectkey": "",  // Campo que armazena o nome da imagem.
                "width": 0,         // Campo que armazena o comprimento da imagem.
                "height": 0,        // Campo que armazena a altura da imagem.
                "size": 0,          // Campo que armazena o tamanho da imagem em bytes.
                "type": ""          // Campo que armazena o tipo da imagem.
            }
        }
    Caso contrário, retornará um JSON formatado no seguinte schema:
        {
            "success": false,   // Indicando que não obteve sucesso na requisição.
            "data": null        // Pois não encontrou nenhum dado.
        }
    :param event: Dicionário contendo informações do evento que realizou a chamada desta função lambda.
    :param context: Objeto com informações do contexto da aplicação na hora da chamada desta função lambda.
    :return: Dicionário contendo informações importantes para o API Gateway.
    """
    s3objectkey = event["pathParameters"]["s3objectkey"]
    response = responseFactory()
    body, code = makeBody(s3objectkey)
    response["body"] = body
    response["statusCode"] = code
    return response

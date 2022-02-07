#!/usr/bin/python3
# -*- coding: utf-8 -*-

import boto3
import json
from collections import Counter
from typing import Any


def getAllItems() -> dict:
    """Função getAllItems:

    Recupera todos os registros contidos na tabela serverless-challenge-dev no banco de dados DynamoDB.
    :return: Um conjunto de dados contendo os registros recuperados.
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("serverless-challenge-dev")
    scanResponse = table.scan()
    return scanResponse["Items"]


def analyzeFileType(dataset: dict) -> (dict, list):
    """Função analyzeFileType:

    Responsável por analizar os dados referentes aos tipos dos arquivos registrados no banco de dados.
    :param dataset: O conjunto dos dados armazenado no banco de dados.
    :return: Um dicionário contendo a ocorrência de cada tipo e uma lista dos tipos dos arquivos registrados no banco de dados respectivamente.
    """
    occurrence = dict(Counter(data["type"] for data in dataset if data.get("type")))
    filetypes = list(occurrence.keys())
    return occurrence, filetypes


def analyzeMinMax(dataset: dict) -> (str, str):
    """Função analyzeMinMax:

    Responsável por analizar os dados referentes ao tamanho do arquivos registrados no banco de dados.
    :param dataset: O conjunto dos dados armazenado no banco de dados.
    :return: O nome do menor arquivo e do maior arquivo registrado no banco de dados respectivamente.
    """
    smaller = min(dataset, key=lambda data: data["size"])
    larger = max(dataset, key=lambda data: data["size"])
    return smaller["s3objectkey"], larger["s3objectkey"]


def responseFactory() -> dict:
    """função responseFactory:

    Função baseada no padrão de projeto Factory. Responsável por criar uma resposta genérica a ser retornada para o API Gateway.
    :return: Dicionário genérico contendo o tipo da resposta e o código da resposta.
    """
    response = dict()
    response["headers"] = {"Content-Type": "application/json"}
    response["statusCode"] = 200  # By default, will return success.
    return response


def createBody(items: dict) -> str:
    """Função createBody:

    Função responsável por criar o corpo da resposta enviada para o usuário.
    :param items: Um dicionário contendo todos os itens salvos no DynamoDB.
    :return: Um conjunto de dados em formato textual que deverão ser tratados como um JSON pelo navegador do usuário.
    """
    body = dict()
    body["smaller"], body["larger"] = analyzeMinMax(items)
    body["occurrence"], body["types"] = analyzeFileType(items)
    return json.dumps(body)


def infoImages(event: dict, context: Any) -> dict:
    """Função infoImages:

    Função executada quando um usuário realiza uma chamada no URN /summary/ do End Point criado para a aplicação.
    Retorna um JSON que resume os metadados salvos no DynamoDB no seguinte schema:
        {
            "smaller": "",      // Nome do menor arquivo salvo.
            "larger": "",       // Nome do maior arquivo salvo.
            "occurrence": {},   // Objeto javascript contendo Ocorrência de cada tipo no banco de dados.
            "types": []         // Array contendo todos os tipos salvos no banco de dados.
        }
    :param event: Dicionário contendo informações do evento que realizou a chamada desta função lambda.
    :param context: Objeto com informações do contexto da aplicação na hora da chamada desta função lambda.
    :return: Dicionário contendo informações importantes para o API Gateway.
    """
    items = getAllItems()
    response = responseFactory()
    response["body"] = createBody(items)
    return response

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import boto3
import base64
from typing import Any


def downloadHeadersFactory(imageObject: dict, name: str) -> dict:
    """Função downloadHeadersFactory

    Esta função deverá receber o dicionário retornado ao solicitar a imagem ao serviço S3 da AWS e o nome da imagem a ser baixada.
    Ele retornará os headers importantes para o processamento da imagem pelo browser.
    :param imageObject: Dicionário contendo informações da imagem desejada.
    :param name: Nome da imagem para realizar o download.
    :return: Dicionário contendo o tipo do arquivo a ser retornado e a informação que o arquivo deve ser entendido como um anexo.
    """
    headers = dict()
    headers["Content-Disposition"] = f"attachment; filename=\"{name}\""
    headers["Content-Type"] = imageObject["ContentType"]
    return headers


def getImageObject(s3objectkey: str) -> dict:
    """Função getImageObject

    Função responsável por acessar um objeto (através de seu nome) salvo no bucket configurado no S3 e retornar seus dados.
    :param s3objectkey: Nome do objeto que deve ser recuperada da pasta uploads do bucket kalingcket (nome escolhido pro bucket).
    :return: Dicionário contendo os dados do objeto salvo no bucket - inclusive o binário do arquivo.
    """
    s3 = boto3.client("s3")
    bucket = "kalingcket"
    path = "uploads/"
    key = path + s3objectkey
    return s3.get_object(Bucket=bucket, Key=key)


def getImage(event: dict, context: Any) -> dict:
    """Função getImage

    Função executada quando um usuário realiza uma chamada no URN /download/ do End Point criado para a aplicação.
    Caso encontre a imagem salva no bucket, retornará a imagem como resposta, do contrário retornará um JSON no seguinte formato:
        {
            "success": false,                   // Indicando que houve uma falha na requisição.
            "message": "Object not found!!"     // Indicando que o objeto não foi encontrado.
        }
    :param event: Dicionário contendo informações do evento que realizou a chamada desta função lambda.
    :param context: Objeto com informações do contexto da aplicação na hora da chamada desta função lambda.
    :return: Dicionário contendo informações importantes para o API Gateway.
    """
    response = dict()
    s3objectkey = event["pathParameters"]["s3objectkey"]

    try:
        imageObject = getImageObject(s3objectkey)
        image = imageObject["Body"].read()
    except:
        response["statusCode"] = 404
        response["headers"] = {"Content-Type": "application/json"}
        response["body"] = "{ \"success\": false, \"message\": \"Object not found!!\" }"
    else:
        response["headers"] = downloadHeadersFactory(imageObject, s3objectkey)
        response["statusCode"] = 200
        response["body"] = base64.b64encode(image)
        response["isBase64Encoded"] = True

    return response

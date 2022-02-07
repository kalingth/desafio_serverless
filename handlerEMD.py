#!/usr/bin/python3
# -*- coding: utf-8 -*-

import boto3
from typing import Any
from PIL import Image
from urllib.parse import unquote_plus
from concurrent.futures import ThreadPoolExecutor


def inputMetaData(metadata: dict) -> None:
    """Função inputMetaData:

    Função responsável por inserir os metadados extraídos na tabela serverless-challenge-dev.
    :param metadata: Dicionário contendo os metadados extraídos.
    :return: None
    """
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("serverless-challenge-dev")
    table.put_item(Item=metadata)


def readerMeta(record: dict) -> None:
    """função readerMeta

    Função responsável por recuperar a imagem inserida no AWS S3 e ler os metadados relacionados a ela.
    Essa função pode, caso seja de interesse do cliente, ser extendidar para recuperar tags Exif.
    :param record: Registro gerado ao realizar o upload da(s) imagem(ns).
    :return: None
    """
    s3 = boto3.client("s3")
    bucket = record["s3"]["bucket"]["name"]
    key = unquote_plus(record["s3"]["object"]["key"])
    obj = s3.get_object(Bucket=bucket, Key=key)

    metadata = {}
    with Image.open(obj["Body"]) as image:
        metadata["width"], metadata["height"] = image.size
        metadata["type"] = image.format

    metadata["s3objectkey"] = key.replace("uploads/", "")
    metadata["size"] = obj["ContentLength"]
    inputMetaData(metadata)


def extractMetadata(event: dict, context: Any) -> dict:
    """Função extractMetadata:

    Função responsável por, cada vez que for realizado o upload de uma imagem no bucket, extrair os
    metadados desta imagem e os salvar em uma tabela do DynamoDB.
    :param event: Dicionário contendo informações do evento que realizou a chamada desta função lambda.
    :param context: Objeto com informações do contexto da aplicação na hora da chamada desta função lambda.
    :return: Dicionário contendo o estado do processamento. Caso haja um erro, retornará o parâmetro success como False, do contrário retornará True.
    """
    try:
        with ThreadPoolExecutor(max_workers=100) as executor:
            for record in event["Records"]:
                executor.submit(readerMeta, record)
    except:
        return {"success": False}
    else:
        return {"success": True}

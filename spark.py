import requests
import random
from datetime import date, datetime
from lxml import objectify
import json

authorizationParams = '<Placeholder>'
pathToFShare = '<Placeholder>'
versionsTableCS = '<Placeholder>'


def listFiles():
    url = pathToFShare + '?restype=directory&comp=list&' + authorizationParams
    response = requests.get(url).content.decode("utf-8")
    xmlstring = response[(response.find('>') + 1):]
    obj = objectify.fromstring(xmlstring)
    fileNames = list(map(lambda file: file.File.Name, obj.Entries))
    return fileNames


def downloadConfiguration(filename):
    url = pathToFShare + filename + '?' + authorizationParams
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('File was not retrieved', response.content)

    content = response.content.decode("utf-8")

    return content


def downloadFileParametrized(fileSource, authType, authValue):
    url = ''
    headers = {}
    if authType == 'query':
        url = fileSource + '?' + authValue
    else:
        url = fileSource
        if authType == 'header':
            headers = {
                'Authorization': authValue
            }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception('File was not retrieved', response.content)

    content = response.content.decode("utf-8")
    return content


def createOrReplaceFileParametrized(destination, filename, dataLength, authType, authValue):
    url = destination + filename
    if authType == 'query':
        url = url + '?' + authValue

    headers = {
        'x-ms-version': '2020-02-10',
        'x-ms-content-length': str(dataLength),
        'x-ms-type': 'file',
        'x-ms-file-permission': 'inherit',
        'x-ms-file-attributes': 'None',
        'x-ms-file-creation-time': 'now',
        'x-ms-file-last-write-time': 'now',
        'Content-Length': '0',
    }
    if authType == 'header':
        headers['Authorization'] = authValue
    resCode = requests.put(url, headers=headers).status_code
    print('createOrReplaceFileParam: ' + str(resCode))


def uploadContentToExistingFileParametrized(destination, filename, bytesArray, dataLength, authType, authValue):
    url = destination + filename + '?comp=range';
    if authType == 'query':
        url = url + '&' + authValue
    headers = {
        'x-ms-version': '2020-02-10',
        'x-ms-type': 'file',
        'x-ms-file-permission': 'inherit',
        'x-ms-file-attributes': 'None',
        'x-ms-file-creation-time': 'now',
        'x-ms-file-last-write-time': 'now',
        'x-ms-write': 'Update',
        'Content-Length': str(dataLength),
        'x-ms-range': 'bytes=0-' + str(dataLength - 1)
    }
    if authType == 'header':
        headers['Authorization'] = authValue
    response = requests.put(url, bytearray(bytesArray.encode()), headers=headers)
    print('uploadContentToExistingFileParam: ' + str(response.status_code))
    if (response.status_code > 300):
        print(response.content)
        print(response.request.headers)


def uploadFileParametrized(destination, filename, content, authType, authValue):
    data = content
    dataLength = len(data)
    createOrReplaceFileParametrized(destination, filename, dataLength, authType, authValue)
    uploadContentToExistingFileParametrized(destination, filename, content, dataLength, authType, authValue)


def getNameWithoutExtenstion(fileName):
    return fileName[:fileName.rfind('.')]


def getFileExtension(fileName):
    string = str(fileName)
    return string[string.rfind('.') + 1:]


class VersionRow:
    def __init__(self, name, size, rowKey):
        self.name = name
        self.size = size
        self.rowKey = rowKey
        self.PartitionKey = 0


def getVersionsTable():
    url = versionsTableCS + '?' + authorizationParams
    response = requests.get(url).content.decode("utf-8")
    xmlstring = response[(response.find('>') + 1):].replace('d:', '').replace('m:', '')
    obj = objectify.fromstring(xmlstring)
    fileNames = list(map(lambda file: VersionRow(file.content.properties.FileName, file.content.properties.Size,
                                                 file.content.properties.RowKey), obj.entry))
    print(fileNames)
    return fileNames


def updateVersion(versionRow, newSize):
    url = versionsTableCS + "(PartitionKey='" + str(versionRow.PartitionKey) + "', RowKey='" + str(
        versionRow.rowKey) + "')" + '?' + authorizationParams
    body = f"""{{
    "RowKey":{versionRow.rowKey},
    "PartitionKey":{versionRow.PartitionKey},
    "FileName":"{versionRow.name}",
    "Size":{newSize}
    }}
    """
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': str(len(body))
    }
    response = requests.put(url, data=bytearray(body.encode()), headers=headers)
    print(f"row {versionRow.rowKey} updated. Status code: {response.status_code}")


def insertVersion(fileName, size):
    url = versionsTableCS + '?' + authorizationParams
    rowKey = random.randint(0, 1e10)

    body = f"""{{
        "RowKey":"{rowKey}",
        "PartitionKey":"0",
        "FileName":"{fileName}",
        "Size":{size}
        }}
        """
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': str(len(body))
    }
    temp = json.loads(body)
    response = requests.post(url, data=bytearray(body.encode()), headers=headers)
    print(f"row {rowKey} created. Status code: {response.status_code}")


def checkIfFileHasChanges(versions, filename, existingFilesize):
    file = next((x for x in versions if x.name == filename), None)
    if file is None:
        return True
    return file.size != existingFilesize


filesRawList = listFiles()
configurationFiles = list(filter(lambda name: getFileExtension(name) == 'conf', filesRawList))
versions = getVersionsTable()

for conf_name in configurationFiles:
    conf_file = downloadConfiguration(conf_name)
    conf_size = len(conf_file)
    confChanged = checkIfFileHasChanges(versions, conf_name, conf_size)

    if not confChanged:
        print(f"{conf_name} was not changed.")
    conf = json.loads(conf_file)

    authType = conf['authorizationType']
    authValue = conf['authorizationValue']
    sourceUrl = conf['sourceUrl']

    sourceFile = downloadFileParametrized(sourceUrl, authType, authValue)

    sourceChanged = checkIfFileHasChanges(versions, sourceUrl, len(sourceFile))
    if not sourceChanged:
        print(f"{sourceUrl} was not changed.")

    if confChanged or sourceChanged:
        queries = conf['queries']
        queryIndex = 1 if len(queries) > 1 else 0;
        dateString = str(date.today())[2:].replace('-', '')
        for query in queries:
            # process query
            viewName = 'data'
            formattedQuery = str(query).replace('{0}', viewName)

            # write csv to dbfs file
            dbutils.fs.put("dbfs:/temp-source.csv", sourceFile, True)

            df1 = spark.read.option("inferSchema", "true").option("header", "true").format("csv").load(
                "/temp-source.csv")
            df1.createOrReplaceTempView("data")

            spark.sql(formattedQuery).repartition(1).write.mode('overwrite').csv(path='file:/dbfs/temp.csv',
                                                                                 header="true")

            result = dbutils.fs.head(dbutils.fs.ls("dbfs:/temp.csv")[-1].path)
            dbutils.fs.rm("/temp.csv", True)
            dbutils.fs.rm("dbfs:/temp-source.csv", True)
            # delete file
            # upload file
            resultName = conf['resultName']
            resultName = resultName.replace('*', dateString)
            if queryIndex > 0:
                resultName = resultName + '-' + str(queryIndex)

            destination = conf['resultUrl']
            resAuthType = conf['resultAuthorizationType']
            resAuthValue = conf['resultAuthorizationValue']

            uploadFileParametrized(destination, resultName + '.csv', result, resAuthType, resAuthValue)
            queryIndex += 1
        # Versions table updates

        sourceConf = next((x for x in versions if x.name == conf_name), None)
        if (sourceConf is not None):
            updateVersion(sourceConf, conf_size)
        else:
            insertVersion(conf_name, conf_size)

        sourceVersion = next((x for x in versions if x.name == sourceUrl), None)
        if (sourceVersion is not None):
            updateVersion(sourceVersion, len(sourceFile))
        else:
            insertVersion(sourceUrl, len(sourceFile))


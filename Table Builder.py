import requests
import os
import json
import time

API_URL = "https://apis.roblox.com/assets/v1/assets"
API_KEY = "L2oXXEiHE0eMqyp1LhpGnw8+h/Z1Kf+tedGHbYRckUmJU9fgZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkluTnBaeTB5TURJeExUQTNMVEV6VkRFNE9qVXhPalE1V2lJc0luUjVjQ0k2SWtwWFZDSjkuZXlKaVlYTmxRWEJwUzJWNUlqb2lUREp2V0ZoRmFVaEZNR1ZOY1hsd01VeG9jRWR1ZHpncmFDOWFNVXRtSzNSbFpFZElZbGxTWTJ0VmJVcFZPV1puSWl3aWIzZHVaWEpKWkNJNklqUXlNalkwT1RVd0lpd2lZWFZrSWpvaVVtOWliRzk0U1c1MFpYSnVZV3dpTENKcGMzTWlPaUpEYkc5MVpFRjFkR2hsYm5ScFkyRjBhVzl1VTJWeWRtbGpaU0lzSW1WNGNDSTZNVGMxTlRNd01EZzJNQ3dpYVdGMElqb3hOelUxTWprM01qWXdMQ0p1WW1ZaU9qRTNOVFV5T1RjeU5qQjkuWEIzc3FuWHJnaFpVTVk1ak5OT0J3eWg1SU9ObGp5eGRmcE4zOGxKWlZHY05tR3JoOVE2NFQ0cHlKN2Fqallsd2NwYkc2UktyTm5UVEhkbDR1YkNVMWRpQk1iMmJqRlFubENGQldvMzdzcWRKNWJRSndpZjBiNmZiWUhXcGNRWUFwSDR1UnZLeUVXX3d6VVVERXhadk8tdEEwN09Mb0xlaU1VVGxvdjJkS1QtS0ZXMW1hWGU4MEc5N3ViRFpSajJ1QVJjX25lU2NjRU8wVUtMWFI4U25UVEFMZnd3VGhYVnRvLXozbnBRQVdVR003STZBVzVzQUpET0gzemhqNjBlWWNaSEY2RjZ4U3ZxRnVDTkM2VEZ4dHlrTzh0QnBrV3AwTXlBVVlURlhGZ2JtM0VhZW8wcjBycmo1dVNWa0Zmb1VZUjg5UEhkM1dNLWtGY3NFUG5hT3V3"
USER_ID = "42264950"
OPERATIONS_URL = "https://apis.roblox.com/assets/v1/operations/"

finalNestDict = {}

validFileNames = []

def GetMeshName(filename):
    cleaned = filename.replace(".png", "").replace(".jpg", "")
    meshName = "Mesh" + cleaned[-2:].replace("0", "")
    return meshName

def GetTextureType(filename):
    if "Normal_OpenGL" in filename:
        return "Normal"
    if "Roughness" in filename:
        return "Roughness"
    if "Base_Color" in filename:
        return "Base_Color"

def AddTextureToDict(filename, rbxassetID):

    meshName = GetMeshName(filename)

    if meshName not in finalNestDict:
        finalNestDict[meshName] = {
            "DiffuseAssetID":"",
            "NormalAssetID":"",
            "RoughnessAssetID":""
        }

    textureType = GetTextureType(filename)
    
    if textureType == "Normal":
        finalNestDict[meshName]["NormalAssetID"] = rbxassetID
    if textureType == "Roughness":
        finalNestDict[meshName]["RoughnessAssetID"] = rbxassetID
    if textureType == "Base_Color":
        finalNestDict[meshName]["DiffuseAssetID"] = rbxassetID

def IsInvalidValidFile(filename):
    if not (filename.endswith(".png")):
        return True      
    elif not ("Normal_OpenGL" in filename or "Roughness" in filename or "Base_Color" in filename):
        return True
    else:
        return False


#program begins here
while True:
    folderPath = input("Enter path to folder: ")
    if os.path.isdir(folderPath):
        break
    else:
        print("Directory not found")

for filename in os.listdir(folderPath):

    if IsInvalidValidFile(filename):
        continue

    with open(os.path.join(folderPath, filename), "rb") as img_file:

        metadata = {
            "assetType": "Decal",
            "displayName": (f"{GetMeshName(filename)} {GetTextureType(filename)} Texture"),
            "description": "Uploaded via Table Builder",
            "creationContext": {
                "creator": {
                    "userId": USER_ID
                }
            }
        }

        response = requests.post(
            API_URL,
            headers={"x-api-key": API_KEY},
            files = {
                "request": (None, json.dumps(metadata), "application/json"),
                "fileContent": (filename, img_file, "image/png")
            }
        )

        if response.ok:
            print("Successfully uploaded " + filename)
        else:
            print(f"Failed to upload {filename}: {response.text} ")
            print(f"Skipping file")
            continue
        
        try:
            path = response.json().get("path")
            operation_id = path.split('/')[-1]
            print(f"Seccessfully retreived OperationID for {filename}, now polling..")
        except:
            print(f"Could not get the OperationID for {filename}")
            print("Skipping assetID retreval for this file")
            continue

        startTime = time.time()
        maxWaitTime = 60 #1 minute
        retryDelay = 2
        finalAssetID = None

        #Keep checking operation until complete/failed/reaches max times
        while(time.time() - startTime < maxWaitTime):
            
            operationResponse = requests.get(
                OPERATIONS_URL + operation_id,
                headers={"x-api-key": API_KEY}
            )

            if not operationResponse.ok:
                print(f"  - Polling failed for {filename}: {operationResponse.text}, Reatempting..")
                time.sleep(10)
                continue
            
            poll_data = operationResponse.json()
            
            is_done = poll_data.get("done", False)
            
            if is_done:
                print(f"Polling successfull for {filename}, adding assetID to dictionary")
                finalAssetID = poll_data.get("response", {}).get("assetId")
                break 

            else:
                print(f" Still polling.. {filename}")
                time.sleep(retryDelay)

        if finalAssetID:
            AddTextureToDict(filename, finalAssetID)
            print("AssetID: {finalAssetID}")
        else:
            print(f"Stopped polling for {filename} after {maxWaitTime}s. No AssetID was retrieved.")
    
print("Done!")

with open(os.path.join(r"C:\Users\culio\AppData\Local\Roblox\Plugins", "Texture_Map.lua"), "w") as f:
    f.write("local textureMap = {\n")
    for mesh, textures in finalNestDict.items():
        f.write(f'    {mesh} = {{\n')
        for texType, assetID in textures.items():
            f.write(f'        {texType} = "rbxassetid://{assetID}",\n')
        f.write("    },\n")
    f.write("}\n")
    f.write("return textureMap\n")


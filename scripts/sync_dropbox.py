import os, pathlib, io, re
import dropbox
from PIL import Image, ImageOps
import requests
for name in ("DROPBOX_APP_KEY","DROPBOX_APP_SECRET","DROPBOX_REFRESH_TOKEN"):
 if not os.environ.get(name,"").strip(): raise SystemExit("Missing secret: "+name)
response=requests.post("https://api.dropboxapi.com/oauth2/token",auth=(os.environ["DROPBOX_APP_KEY"].strip(),os.environ["DROPBOX_APP_SECRET"].strip()),data={"grant_type":"refresh_token","refresh_token":os.environ["DROPBOX_REFRESH_TOKEN"].strip()},timeout=30)
if not response.ok:
 try: error=response.json().get("error","unknown")
 except ValueError: error="non_json_response"
 allowed={"invalid_grant","invalid_client","invalid_request","invalid_access_token","unsupported_grant_type","invalid_scope"}
 raise SystemExit("Dropbox OAuth HTTP "+str(response.status_code)+": "+(error if isinstance(error,str) and error in allowed else "unclassified_error"))
token=response.json()["access_token"]
print("Dropbox OAuth refresh succeeded")
db=dropbox.Dropbox(oauth2_access_token=token)

folders={"CLAAS_AXION_960_2019":"960","CLAAS_AXION_950_2018":"950-2018","CLAAS_AXION_950_2019":"950-2019","CLAAS_AXION_930_2019":"930","COMPANY":"company"}
result=db.files_list_folder("/publish",recursive=True)
count=0
while True:
 for entry in result.entries:
  if not isinstance(entry,dropbox.files.FileMetadata): continue
  parts=entry.path_display.strip("/").split("/")
  if len(parts)!=3 or parts[1] not in folders or not re.fullmatch(r"[0-9]{1,3}\.(jpg|jpeg|png|webp)",parts[2],re.I): continue
  if entry.size>30000000: continue
  _,response=db.files_download(entry.path_lower)
  with Image.open(io.BytesIO(response.content)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   im.thumbnail((1800,1800))
   dest=pathlib.Path("assets/catalog")/folders[parts[1]]/(pathlib.Path(parts[2]).stem+".webp")
   dest.parent.mkdir(parents=True,exist_ok=True)
   im.save(dest,"WEBP",quality=85)
   count+=1
 if not result.has_more: break
 result=db.files_list_folder_continue(result.cursor)
print(f"Processed {count} approved images")

import json
root=pathlib.Path("assets/catalog")
root.mkdir(parents=True,exist_ok=True)
manifest={key:[p.as_posix() for p in sorted((root/key).glob("*.webp"))] for key in folders.values()}
(root/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")

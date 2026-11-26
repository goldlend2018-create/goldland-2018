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

import json
mapping={"8910402":"950-2019","8914210":"930","8977926":"950-2018"}
root=pathlib.Path("assets/catalog")
root.mkdir(parents=True,exist_ok=True)
count=0
for listing,machine in mapping.items():
 try:
  page=db.files_list_folder("/"+listing)
 except dropbox.exceptions.ApiError as exc:
  if exc.error.is_path() and exc.error.get_path().is_not_found():
   print("Missing listing folder: "+listing)
   continue
  raise
 entries=list(page.entries)
 while page.has_more:
  page=db.files_list_folder_continue(page.cursor)
  entries.extend(page.entries)
 photos=sorted((e for e in entries if isinstance(e,dropbox.files.FileMetadata) and re.fullmatch(listing+r"_[0-9]+\.(jpg|jpeg|png|webp)",e.name,re.I) and e.size<=30000000),key=lambda e:e.name)
 for i,entry in enumerate(photos,1):
  _,download=db.files_download(entry.path_lower)
  with Image.open(io.BytesIO(download.content)) as im:
   im=ImageOps.exif_transpose(im).convert("RGB")
   im.thumbnail((1800,1800))
   dest=root/machine/f"{i:02d}.webp"
   dest.parent.mkdir(parents=True,exist_ok=True)
   im.save(dest,"WEBP",quality=85)
   count+=1
 print(f"Listing {listing}: {len(photos)} photos")
if not count: raise SystemExit("No matching listing photos accessible to Dropbox app")
manifest={key:[p.as_posix() for p in sorted((root/key).glob("*.webp"))] for key in ["960","950-2018","950-2019","930","company"]}
(root/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
print(f"Processed {count} approved images")

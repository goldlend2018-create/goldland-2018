import os, pathlib, io, re
import dropbox
from PIL import Image, ImageOps
db=dropbox.Dropbox(oauth2_refresh_token=os.environ["DROPBOX_REFRESH_TOKEN"],app_key=os.environ["DROPBOX_APP_KEY"],app_secret=os.environ["DROPBOX_APP_SECRET"])
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

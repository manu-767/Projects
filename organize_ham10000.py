import os
import pandas as pd
import shutil

# Set paths
metadata_path = r"C:\Users\manum\Downloads\archive\HAM10000_metadata.csv"
img_dir_1 = r"C:\Users\manum\Downloads\archive\HAM10000_images_part_1"
img_dir_2 = r"C:\Users\manum\Downloads\archive\HAM10000_images_part_2"
output_base = r"C:\Users\manum\Skin-Disease-Detection\ISIC2018"

# Read metadata
df = pd.read_csv(metadata_path)

# Create output folders
label_list = df['dx'].unique()
for label in label_list:
    os.makedirs(os.path.join(output_base, label), exist_ok=True)

# Copy images to correct folders
not_found = 0
for i, row in df.iterrows():
    img_file = row['image_id'] + '.jpg'
    label = row['dx']
    src_path = os.path.join(img_dir_1, img_file)
    if not os.path.exists(src_path):
        src_path = os.path.join(img_dir_2, img_file)
    if not os.path.exists(src_path):
        not_found += 1
        continue
    dst_path = os.path.join(output_base, label, img_file)
    shutil.copyfile(src_path, dst_path)

print("✅ All done!")
if not_found:
    print(f"⚠️ {not_found} images not found.")

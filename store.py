import pymongo
import gridfs
import pandas as pd
import requests
from bson.objectid import ObjectId
from io import BytesIO

# Connect to the MongoDB instance
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Access the database
db = client["mydatabase"]

# Initialize GridFS
fs = gridfs.GridFS(db)

# Access the collections
image_details_collection = db["image_details"]

def store_images_and_details(image_folder_path, csv_file_path):
    # Read CSV file
    df = pd.read_csv(csv_file_path)

    # Print column names for debugging
    print("CSV Column Names:", df.columns)

    # Iterate through the CSV rows
    for index, row in df.iterrows():
        # Generate a new ObjectId for this image
        image_id = ObjectId()

        # Use the image URL from the CSV file
        image_url = row['Image URL']
        
        try:
            # Download the image from the URL
            response = requests.get(image_url)
            image_data = BytesIO(response.content)
            
            # Store image in GridFS
            fs.put(image_data, _id=image_id, filename=f"{image_id}.jpg")
            print(f"Stored image with ObjectId: {image_id}")

        except Exception as e:
            print(f"Failed to download or store image from URL {image_url}: {e}")
            continue

        # Store image details in the collection
        image_details = {
            "_id": image_id,
            "Medicine Name": row["Medicine Name"],
            "Composition": row["Composition"],
            "Uses": row["Uses"],
            "Side_effects": row["Side_effects"],
            "Image URL": image_url,
            "Manufacturer": row["Manufacturer"],
            "Excellent Review %": row["Excellent Review %"],
            "Average Review %": row["Average Review %"],
            "Poor Review %": row["Poor Review %"]
        }
        image_details_collection.insert_one(image_details)

        print(f"Stored details for image with ObjectId: {image_id}")

# Example usage
image_folder_path = r"C:\Users\cuted\OneDrive\Desktop\img"  # Path not used in this case
csv_file_path = r"C:\Users\cuted\OneDrive\Desktop\Medicine_Details.csv"
store_images_and_details(image_folder_path, csv_file_path)

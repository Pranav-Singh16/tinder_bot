import io
import time
import requests
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
# from location import location
from image_extracter import extract_images
# from face_comparison import FaceComparer

TOKEN = '7568800497:AAEtyLB-u7ZyF8vZaZy0G0hxEKz9jpo-D4w'
# face_comparer = FaceComparer(method='insightface')
print('starting')

user_image = None
user_location = None

# Handler to start the interaction with the bot
async def start(update: Update, context) -> None:
    await update.message.reply_text("Welcome to the bot! Please share your location to get started.")

# Handler to capture text input (location)
async def handle_location(update: Update, context) -> None:
    global user_location
    user_location = update.message.text.strip()  # Store the user's location input
    print('feeding location to ml')
    # actual_location = location(user_location)
    print('replying actual location')
    await update.message.reply_text(f"Got it! Your location is: {user_location}. Please send an image now.")

    # Ask the user to send an image after location is provided
    # await update.message.reply_text("Please send an image now.")

# Handler to capture and process photo input
async def handle_photo(update: Update, context) -> None:
    global user_image, user_location
    if user_location is None:
        await update.message.reply_text("Please provide a location first.")
        return

    # Check if the message contains a photo
    if update.message.photo:
        photo_file = await update.message.photo[-1].get_file()  # Get the highest quality photo
        file_path = 'received_image.jpg'
        
        # Download the photo to the server using the correct method
        await photo_file.download_to_drive(file_path)  # Download and save the photo

        # Log the received image
        print(f"Image received and saved as '{file_path}'")

        loading_message = await update.message.reply_text("Image received! Now retrieving data from Tinder.")
        await update.message.reply_text("Please wait, we're working on it")

        user_image = Image.open(file_path)

        # Trigger image extraction asynchronously
        image_urls = await extract_images(user_location)
        
        if image_urls:
            total_images = len(image_urls)
            for i, image_url in enumerate(image_urls):
                await update.message.reply_text(f"Comparing face {i + 1}/{total_images}...")

                # Assuming image_url is a URL, download the image from the URL
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    img_byte_array = io.BytesIO(img_response.content)  # Convert the image to byte array
                    
                    # Open the image (Pillow can handle webp if the right libraries are installed)
                    try:
                        tinder_image = Image.open(img_byte_array)
                    except Exception as e:
                        await update.message.reply_text(f"Error opening the image: {str(e)}")
                        continue

                    # Convert the image to RGB if it's not already (important for comparison)
                    if tinder_image.mode != 'RGB':
                        tinder_image = tinder_image.convert('RGB')

                    # Compare the user image with the scraped image
                    # similarity_score = face_comparer.compare_faces(user_image, tinder_image)
                    
                    # Create the comparison result text
                    # if isinstance(similarity_score, dict): 

                    #     similarity_score = similarity_score.get("score", 0)

                    # if similarity_score ==0:
                    #     result_text = f"No face find in Tinder Image"
                        
                    # if similarity_score >= 0.65:
                    #     result_text = f"Match found! Similarity score: {similarity_score:.2f}"
                    # else:
                    #     result_text = f"No match found. Similarity score: {similarity_score:.2f}"

                    # if isinstance(similarity_score, dict):
                    #     # If similarity_score is a dictionary, check if it contains a 'score' key
                    #     similarity_score = similarity_score.get("score", 0)

                    # # Ensure that similarity_score is a number (float or int)
                    # try:
                    #     similarity_score = float(similarity_score)
                    # except (ValueError, TypeError):
                    #     similarity_score = 0  # In case it can't be converted to a number, default to 0

                    # # Handle cases where no faces are detected
                    # if similarity_score == 0:
                    #     result_text = "No face found in Tinder Image"  # More descriptive message

                    # # Handle the case where faces are detected but no match is found
                    # elif similarity_score >= 0.65:
                    #     result_text = f"Match found! Similarity score: {similarity_score:.2f}"
                    # else:
                    #     result_text = f"No match found. Similarity score: {similarity_score:.2f}"

                    result_text = 'no model assigned yet'


                    # Send the image back as a reply
                    img_byte_array.seek(0)  # Reset byte stream pointer to the start
                    await update.message.reply_photo(photo=img_byte_array)
                    await update.message.reply_text(result_text)

                    # Add a small delay before sending the next image
                    if i < total_images - 1:
                        time.sleep(2)  # Adding a delay between sending images for better user experience

        else:
            await update.message.reply_text("Sorry, no images found for this location.")
    else:
        await update.message.reply_text("No photo received. Please send a valid image.")

def main() -> None:
    # Create the application instance
    application = Application.builder().token(TOKEN).build()

    # Add command handler for /start
    application.add_handler(CommandHandler("start", start))

    # Add message handler for location input (string)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.LOCATION, handle_location))

    # Add message handler for photo input
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()

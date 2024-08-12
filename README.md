# lactosafeAPI
Lactose Intolerance Helper
Overview
Lactose Intolerance Helper is an application designed to assist individuals with lactose intolerance by accurately identifying food items and assessing their risk of containing lactose. The app leverages the Gemini API from Google for its image recognition capabilities, allowing users to make informed dietary choices with ease.

Features
Accurate Food Recognition: Uses the Gemini API to identify a wide variety of food items from images with high accuracy.
Lactose Risk Assessment: Classifies foods into five lactose risk categories—Nonexistent, Low, Medium, High, and Very High—based on custom criteria defined within the app.
User-Friendly Interface: Simple and intuitive design for quick and easy use.
Rapid Response: Provides quick feedback on both food identification and lactose risk assessment.
How It Works
Image Recognition: Users upload an image of the food item. The app sends this image to the Gemini API, which returns detailed information about the food.
Risk Classification: Based on the returned food data, the app makes a second request to the Gemini API, which classifies the food into one of five lactose risk categories (Nonexistent, Low, Medium, High, Very High) according to specific criteria defined within the app.

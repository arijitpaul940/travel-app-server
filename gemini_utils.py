import google.generativeai as genai


# Set your API key here or use environment variable
GOOGLE_API_KEY = "AIzaSyBuhhdg3xjOtLX2UbSFO5iJC2c3LSO17Ss"
genai.configure(api_key=GOOGLE_API_KEY)

# List all available models
models = genai.list_models()
for model in models:
  print(f"Model name: {model.name}")
  print(f"Supported generation methods: {model.supported_generation_methods}\n")


def estimate_budget_with_gemini(place_name, best_time, duration, total_persons):
  prompt = f"""
  I want you to estimate the budget for a tour.
  - Destination: {place_name}
  - Duration: {duration}
  - Best Time to Visit: {best_time}
  - Number of Persons: {total_persons}
  Consider transportation, accommodation, food, local travel, and activities. Provide a rough but realistic budget in INR.
  """
  model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')
  response = model.generate_content(prompt)
  return response.text

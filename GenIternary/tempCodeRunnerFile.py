def generate_itinerary():
    user_data = request.form
    destination = user_data.get('destinations', 'unknown destination')

    # Fetch weather data for the selected destination
    weather_data = get_weather(destination)

    weather_details = []  # Initialize weather_details as an empty list

    # Check if weather data is valid
    if 'error' not in weather_data:
        # Get current weather
        current_temp = weather_data['current']['temp_c']
        current_condition = weather_data['current']['condition']
        current_date = "Today"

        # Append current weather to weather_details
        weather_details.append({
            'date': current_date,
            'temperature': f"{current_temp}°C",
            'description': current_condition
        })

        # Add forecast data
        for day in weather_data['forecast']:
            weather_details.append({
                'date': day['date'],
                'temperature': f"Max: {day['max_temp_c']}°C, Min: {day['min_temp_c']}°C",
                'description': day['condition'],
            })

        # Construct a detailed prompt with a dedicated weather block
        prompt = f"""
        Create a detailed {user_data.get('duration', 7)}-day travel itinerary for a trip to {destination}.
        
        Traveler Information:
        - Budget: {user_data.get('budget', 'standard')}
        - Interests: {user_data.get('interests', 'none')}
        - Travel style: {user_data.get('travel_style', 'explorer')}
        - Previous visits: {user_data.get('previous_visits', 'first time')}
        - Food preferences: {user_data.get('food_preferences', 'none')}
        - Traveling with: {user_data.get('traveling_with', 'solo')}
        - Explore hidden gems: {user_data.get('hidden_gems', 'yes')}
        - Cultural tips: {user_data.get('cultural_tips', 'none')}
        - Local events: {user_data.get('events', 'none')}
        
        Weather Information for {destination}:
        {weather_details}

        Please generate an itinerary that includes places to visit, recommended activities, and suggestions for meals based on this information.
        """

        try:
            # Fetch the itinerary from the GroQ API based on the prompt
            itinerary = get_groq_response(prompt)

            # Split itinerary by day (assuming the returned itinerary uses "Day X" format)
            days = itinerary.split('Day ')[1:]  # Splits the text, ignoring the first empty string
            days = [f'Day {day}' for day in days]  # Adding 'Day ' back to each day

            # Render the itinerary HTML page
            return render_template('itinerary.html', itinerary=days, weather_data=weather_details, destination=destination)
        
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Error: Could not connect to GroQ API. Exception: {e}'}), 500
        except Exception as e:
            return jsonify({'error': f'Error: Unexpected error occurred. Exception: {e}'}), 500

    else:
        # Handle case where weather data is unavailable
        return jsonify({'error': 'Weather data unavailable.'}), 400
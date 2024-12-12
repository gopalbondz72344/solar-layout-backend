from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from pymongo import MongoClient
import logging
import random
# MongoDB connection setup
client = MongoClient("mongodb+srv://saigopalbonthu:EawZVxqRxoU2tLCZ@node.8s5hmks.mongodb.net/")  # Replace with your MongoDB URI
db = client['solarR&Ddatabase']  # Database name
collection = db['generated_ids']  # Collection name
solar_plants_collection= db['solar_plants']

logger = logging.getLogger(__name__)

@csrf_exempt
def layout_Register(request):
    if request.method == 'POST':
        try:
            # Parse input JSON
            data = json.loads(request.body.decode("utf-8"))
            logger.debug(f"Received data: {data}")

            # Extract and validate inputs
            plant_id = data.get('PlantID')  # Matches the key from the React frontend
            smb_count = data.get('SmbCount')
            string_count = data.get('StringCount')
            panel_count = data.get('PanelCount')

            # Validate required fields
            if not all([plant_id, smb_count, string_count, panel_count]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Missing required fields: PlantID, SmbCount, StringCount, or PanelCount'
                }, status=400)

            # Ensure numeric fields are integers
            try:
                smb_count = int(smb_count)
                string_count = int(string_count)
                panel_count = int(panel_count)
            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Fields SmbCount, StringCount, and PanelCount must be integers'
                }, status=400)

            # Check for duplicate PlantID
            existing_record = collection.find_one({'PlantID': plant_id})
            if existing_record:
                return JsonResponse({
                    'status': 'error',
                    'message': f'PlantID "{plant_id}" already exists. Please use a unique PlantID.'
                }, status=400)

            # Store the data in MongoDB
            record = {
                'PlantID': plant_id,
                'SmbCount': smb_count,
                'StringCount': string_count,
                'PanelCount': panel_count,
            }
            insert_result=collection.insert_one(record)

              # Add the inserted ID to the response and convert ObjectId to string
            record['_id'] = str(insert_result.inserted_id)

            # Return success response
            return JsonResponse({'status': 'success', 'data': record}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)

        except Exception as e:
            logger.exception("An unexpected error occurred")
            return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)



# ==================================================================================================================================================
@csrf_exempt
def get_details_by_plant_id(request, plant_id):
    """
    Retrieve SMB, String, and Panel details for a given PlantID.
    """
    if request.method == 'GET':
        try:
            # Query MongoDB for the document with the given PlantID
            record = collection.find_one({'PlantID': plant_id}, {'_id': 0})  # Exclude MongoDB's _id field
            
            if not record:
                return JsonResponse({'status': 'error', 'message': f'No data found for PlantID: {plant_id}'}, status=404)

            # Return the data as JSON
            return JsonResponse({'status': 'success', 'data': record}, status=200)
        except Exception as e:
            logger.exception("An unexpected error occurred")
            return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred: ' + str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def get_all_plants(request):
    if request.method == 'GET':
        try:
            logger.info("GET request received for all plant details.")
            # Retrieve all plants from the collection
            plants = solar_plants_collection.find({})  # Fetch all fields

            # Prepare a list to hold plant details
            plant_list = []
            for plant in plants:

                plant_details = {
                    'Plant_ID': plant.get('Plant_ID'),
                }
                plant_list.append(plant_details)

            logger.info(f"Retrieved {len(plant_list)} plants.")
            return JsonResponse({'plants': plant_list}, status=200)

        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}", exc_info=True)
            return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=500)

    logger.warning("Invalid request method used.")
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# =============================================================================================================================================

# @csrf_exempt
# def get_power_output(request, plant_id):
#     if request.method == 'GET':
#         try:
#             # Validate plant ID
#             if not plant_id:
#                 return JsonResponse({'status': 'error', 'message': 'Plant ID is required'}, status=400)

#             # Retrieve SmbCount and StringCount from MongoDB
#             record = collection.find_one({'PlantID': plant_id})
#             if not record:
#                 return JsonResponse({'status': 'error', 'message': 'Plant ID not found'}, status=404)

#             smb_count = record.get('SmbCount')
#             string_count = record.get('StringCount')

#             if smb_count is None or string_count is None:
#                 return JsonResponse({'status': 'error', 'message': 'SmbCount or StringCount missing in database'}, status=500)

#             try:
#                 smb_count = int(smb_count)
#                 string_count = int(string_count)
#             except ValueError:
#                 return JsonResponse({'status': 'error', 'message': 'Fields SmbCount and StringCount must be integers'}, status=400)

#             # Initialize output
#             response_data = []

#             # Generate power outputs for each string within each SMB
#             for smb in range(1, smb_count + 1):
#                 smb_id = f"SMB{smb:02}"  # Format SMB ID as SMB01, SMB02, etc.
#                 smb_data = {'smb_id': smb_id, 'strings': []}

#                 for string in range(1, string_count + 1):
#                     string_id = f"{smb}.{string}"

#                     # Randomly generate voltage and current for the string
#                     voltage = random.uniform(0, 1500)  # Example: Voltage in volts
#                     current = random.uniform(0, 10)    # Example: Current in amperes

#                     # Calculate power output for this string
#                     power_output = round(voltage * current, 2)  # Power in watts (rounded to 2 decimals)
#                     smb_data['strings'].append({
#                         'string_id': string_id,
#                         'power_output': f"{power_output}W"
#                     })

#                 response_data.append(smb_data)

#             # Return the generated IDs as a JSON response
#             return JsonResponse({'status': 'success', 'data': response_data}, status=200)
#         except json.JSONDecodeError:
#             return JsonResponse({'status': 'error', 'message': 'Invalid JSON format'}, status=400)
#         except Exception as e:
#             logger.exception("An unexpected error occurred")
#             return JsonResponse({'status': 'error', 'message': 'An unexpected error occurred: ' + str(e)}, status=500)
#     else:
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
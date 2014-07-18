def convert_to_type(original_value, data_type):
  if data_type == 'bool':
    converted_value = True if original_value=='1' else False
  elif setting.data_type == 'float':
    converted_value = float(original_value)
  else:
    converted_value = str(original_value)
  return converted_value

def convert_to_db_format(original_value, data_type):
  if data_type == 'bool':
    converted_value = '1' if original_value else '0'
  else:
    converted_value = str(original_value)
  return converted_value

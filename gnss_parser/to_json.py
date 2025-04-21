import json

from astropy.units import Quantity

def quantity_converter(obj):
    if isinstance(obj, Quantity):
        return {"value": obj.value, "unit": str(obj.unit)}
    return json.dumps(obj)

def format_as_json(message_name, svId, header, page_header, content) -> str:
    result = {
        'message': message_name,
        'satellite': svId,
        'subframe': header.subframe_id,
    }
    if page_header:
        result['page'] = page_header.page_id
    result['content'] = content.__dict__
    return json.dumps(result, default=quantity_converter)

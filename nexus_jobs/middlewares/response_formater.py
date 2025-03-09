from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response', None)
        status_code = response.status_code if response else 200

        # Ensure data is a dictionary
        if not isinstance(data, dict):
            data = {"message": data}

        if status_code >= 400:
            response_data = {
                "status": "error",
                "message": data.get("detail", "An error occurred"),
                "errors": data.get("errors") or {key: value for key, value in data.items() if key != "detail"},
            }
        else:
            response_data = {
                "status": "success",
                "data": data if data is not None else {},
            }

        return super().render(response_data, accepted_media_type, renderer_context)

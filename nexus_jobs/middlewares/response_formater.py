from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Get response status
        response = renderer_context.get('response', None)
        status_code = response.status_code if response else 200

        # Wrap response data
        modified_response = {
            "status": "success" if status_code in [200, 201] else "error",
            "data": data
        }

        return super().render(modified_response, accepted_media_type, renderer_context)
